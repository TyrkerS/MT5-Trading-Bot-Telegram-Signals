import MetaTrader5 as mt5

simbol = "XAUUSD-VIP"
lot = 0.01
pip = 0.1
deviacio = 20

# Initialize MetaTrader 5
if not mt5.initialize():
    print(" Unable to initialize MT5:", mt5.last_error())
    quit()

# Select symbol
mt5.symbol_select(simbol, True)

# Get current prices
tick = mt5.symbol_info_tick(simbol)
if not tick:
    print(" Unable to get tick")
    mt5.shutdown()
    quit()

preu = tick.ask
sl = preu - 50 * pip
tp = preu + 30 * pip

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
    "comment": "Test order",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,  # Correct filling mode
}

resultat = mt5.order_send(ordre)

if resultat.retcode != mt5.TRADE_RETCODE_DONE:
    print(f" Error sending order: {resultat.retcode}")
    print(" Details:", resultat)
else:
    print(" Order sent successfully!")

mt5.shutdown()
