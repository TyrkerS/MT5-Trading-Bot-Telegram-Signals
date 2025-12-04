import MetaTrader5 as mt5

simbol = "XAUUSD-VIP"  # Change to "XAUUSD" if this one does not work

# Initialize MetaTrader 5
if not mt5.initialize():
    print(" Error connecting to MT5")
    print(mt5.last_error())
    quit()

print(" Successful connection to MetaTrader 5")

# Account information
compte = mt5.account_info()
if compte is not None:
    print("Active account:", compte.login)

# Check symbol
info = mt5.symbol_info(simbol)
if info is None or not info.visible:
    print(f" The symbol {simbol} is not available or visible.")
    mt5.shutdown()
    quit()

# Force quotes if needed
mt5.symbol_select(simbol, True)

# Get tick
tick = mt5.symbol_info_tick(simbol)
if tick is None:
    print(" Unable to get tick. Maybe there are no active quotes.")
elif tick.bid == 0 or tick.ask == 0:
    print(" Tick received but with zero values. Market closed or inactive.")
else:
    print(f" Valid tick received: BID = {tick.bid}, ASK = {tick.ask}")

# Show symbol information
print("Minimum volume:", info.volume_min)
print("Volume step:", info.volume_step)
print("Maximum volume:", info.volume_max)
print("Allowed filling mode:", info.trade_calc_mode)

# Close connection
mt5.shutdown()



import MetaTrader5 as mt5

simbol = "XAUUSD-VIP"
lot = 0.01
pip = 0.1
deviacio = 20

if not mt5.initialize():
    print(" Unable to initialize MT5:", mt5.last_error())
    quit()

mt5.symbol_select(simbol, True)
tick = mt5.symbol_info_tick(simbol)

if tick is None:
    print(" Unable to get tick")
    mt5.shutdown()
    quit()

preu = tick.ask
sl = preu - 50 * pip
tp = preu + 30 * pip

modes = {
    mt5.ORDER_FILLING_FOK: "FOK",
    mt5.ORDER_FILLING_IOC: "IOC",
    mt5.ORDER_FILLING_RETURN: "RETURN"
}

for mode, nom in modes.items():
    print(f"\n Testing filling mode: {nom}")
    ordre = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": simbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": preu,
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "deviation": deviacio,
        "magic": 123456,
        "comment": f"Test {nom}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mode,
    }

    resultat = mt5.order_send(ordre)
    if resultat.retcode == mt5.TRADE_RETCODE_DONE:
        print(f" WORKS! Order sent successfully using mode {nom}")
        break
    else:
        print(f" Error: {resultat.retcode} - Does not work with mode {nom}")

mt5.shutdown()
