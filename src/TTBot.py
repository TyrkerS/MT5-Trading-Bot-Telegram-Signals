import difflib
import MetaTrader5 as mt5
import json
import asyncio
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient, events

# ---- CONFIGURATION ----
with open("config.json") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
canal = -1002164511324  # Telegram channel ID

simbol = "XAUUSD-VIPc"
lot = 0.15
tp_individual_pips = 20
tp_global_usd = 25
sl_global_usd = -2100
promedi_pips = 20
max_ordres_obertes = 15
deviacio = 100

pip = 0.1  # Will be assigned dynamically after connecting.

ordre_actual = None
ultima_entrada = None
temps_senyal = None


# --- MT5 FUNCTIONS ---
def connectar_mt5():
    """Initializes the connection with MetaTrader 5."""
    if not mt5.initialize():
        print(f"Error connecting to MetaTrader 5: {mt5.last_error()}")
        return False
    print("Connected to MetaTrader 5")
    return True


def obtenir_ordres_obertes():
    """Returns all open positions for the configured symbol."""
    posicions = mt5.positions_get(symbol=simbol)
    return posicions if posicions else []


def calcular_profit_flotant():
    """
    Calculates floating profit by summing the 'profit' field of each open position.
    This value is always accurate because it's returned by the broker.
    """
    total = 0.0
    posicions = obtenir_ordres_obertes()
    for p in posicions:
        total += p.profit
    return total


def calcular_profit_tancat():
    """Calculates closed profit from deals executed after the current signal."""
    if not temps_senyal:
        return 0.0

    from_date = temps_senyal

    tick = mt5.symbol_info_tick("XAUUSD-VIP")
    if tick is not None:
        to_date = datetime.fromtimestamp(tick.time, tz=timezone.utc)
    else:
        print("Unable to get tick")
        return 0.0

    history_deals = mt5.history_deals_get(from_date, to_date)

    if history_deals is None:
        return 0.0

    deals_closed = [
        d for d in history_deals
        if d.entry == mt5.DEAL_ENTRY_OUT and d.symbol == simbol
    ]

    total_profit = 0.0
    for deal in deals_closed:
        total_profit = sum(deal.profit for deal in deals_closed)
    total_profit += deal.profit

    return total_profit



def enviar_ordre(tipus):
    """Sends a new market order (BUY or SELL)."""
    global ultima_entrada

    if not mt5.symbol_select(simbol, True):
        print(f"Unable to select symbol {simbol}")
        return

    tick = mt5.symbol_info_tick(simbol)
    if tick is None or tick.bid == 0 or tick.ask == 0:
        print("Invalid tick, cannot send order.")
        return

    tipus_ordre = mt5.ORDER_TYPE_BUY if tipus == "BUY" else mt5.ORDER_TYPE_SELL

    if tipus == "BUY":
        preu_actual = tick.ask
        tp_price = preu_actual + tp_individual_pips * pip
    else:
        preu_actual = tick.bid
        tp_price = preu_actual - tp_individual_pips * pip

    ordre = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": simbol,
        "volume": lot,
        "type": tipus_ordre,
        "price": preu_actual,
        "deviation": deviacio,
        "comment": f"Averaging {tipus}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
        "tp": round(tp_price, mt5.symbol_info(simbol).digits)
    }

    resultat = mt5.order_send(ordre)
    if resultat.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Error sending order: {resultat.retcode} - {resultat.comment}")
    else:
        print(f"Order {tipus} opened at {preu_actual}")
        ultima_entrada = preu_actual


def comprovar_promedi(tipus):
    """Checks whether a new averaging order needs to be opened."""
    posicions = obtenir_ordres_obertes()
    if not posicions or len(posicions) >= max_ordres_obertes:
        return

    ultima_posicio = sorted(posicions, key=lambda p: p.time_msc)[-1]
    tick = mt5.symbol_info_tick(simbol)
    if not tick:
        return

    if tipus == "BUY":
        preu_actual = tick.ask
        pips_negatius = (ultima_posicio.price_open - preu_actual) / pip
    else:
        preu_actual = tick.bid
        pips_negatius = (preu_actual - ultima_posicio.price_open) / pip

    if pips_negatius >= promedi_pips:
        enviar_ordre(tipus)


def tancar_totes():
    """Closes all open positions for the symbol."""
    posicions = obtenir_ordres_obertes()
    if not posicions:
        print("No positions to close.")
        return

    print(f"Closing {len(posicions)} position(s)...")

    for pos in posicions:
        tick = mt5.symbol_info_tick(pos.symbol)
        if not tick:
            continue

        preu_tancament = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask
        tipus_contra = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

        ordre = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": pos.ticket,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": tipus_contra,
            "price": preu_tancament,
            "deviation": deviacio,
            "comment": "Bot forced close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        resultat = mt5.order_send(ordre)
        if resultat.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Position {pos.ticket} closed.")
        else:
            print(f"Error closing position {pos.ticket}: {resultat.retcode} - {resultat.comment}")


def reiniciar_senyal():
    """Resets all signal-related state variables."""
    global ordre_actual, ultima_entrada, temps_senyal
    ordre_actual = None
    ultima_entrada = None
    temps_senyal = None
    print("Signal reset. Waiting for new signal...")


def processar_missatge(text):
    """Processes the Telegram message and decides whether to trade."""
    global ordre_actual, ultima_entrada, temps_senyal

    text = text.lower()

    closing_keywords = ["cerramos"]

    for word in text.split():
        match = difflib.get_close_matches(word, closing_keywords, n=1, cutoff=0.8)
        if match:
            print("Close signal detected. Closing all positions.")
            tancar_totes()
            reiniciar_senyal()
            return

    if ordre_actual is not None:
        print(f"A trade sequence is already active ({ordre_actual}). Ignoring new signal.")
        return

    nou_ordre = None
    if "buy" in text:
        nou_ordre = "BUY"
    elif "sell" in text:
        nou_ordre = "SELL"

    if nou_ordre:
        print(f"New signal received: {nou_ordre}")
        ordre_actual = nou_ordre
        enviar_ordre(ordre_actual)

        tick = mt5.symbol_info_tick("XAUUSD-VIP")

        if tick is not None:
            temps_senyal = datetime.fromtimestamp(tick.time, tz=timezone.utc)
            print("Server time:", temps_senyal)
        else:
            print("Unable to get tick time.")


# --- ASYNCHRONOUS MAIN LOOP ---
async def main():
    global ordre_actual, temps_senyal, pip

    if not connectar_mt5():
        return

    simbol_info = mt5.symbol_info(simbol)
    if not simbol_info:
        print(f"Unable to get symbol info for {simbol}. Exiting.")
        mt5.shutdown()
        return

    print(f"Pip/point value for {simbol} set to: {pip}")

    async with TelegramClient('lector_session', api_id, api_hash) as client:
        @client.on(events.NewMessage(chats=canal))
        async def handler(event):
            processar_missatge(event.message.message)

        print("Bot active. Listening for Telegram signals...")

        while True:
            if ordre_actual:
                posicions_obertes = obtenir_ordres_obertes()

                if not posicions_obertes and ordre_actual:
                    print("No open positions. Resetting signal...")
                    reiniciar_senyal()
                    continue

                profit_flotant = calcular_profit_flotant()
                profit_tancat = calcular_profit_tancat()
                total = profit_flotant + profit_tancat

                print(f"Floating: {profit_flotant:.2f} USD, Closed: {profit_tancat:.2f} USD | TOTAL: {total:.2f} USD")

                if total >= tp_global_usd:
                    print(f"Global TP reached ({total:.2f} USD). Closing everything...")
                    tancar_totes()
                    await asyncio.sleep(1)
                    reiniciar_senyal()

                elif total <= sl_global_usd:
                    print(f"Global SL reached ({total:.2f} USD). Closing everything...")
                    tancar_totes()
                    await asyncio.sleep(1)
                    reiniciar_senyal()
                else:
                    comprovar_promedi(ordre_actual)

            await asyncio.sleep(1)


# --- ENTRY POINT ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Disconnecting...")
    finally:
        if mt5.terminal_info():
            mt5.shutdown()
            print("Disconnected from MetaTrader 5.")
