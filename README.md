# AUTOMATED TRADING & TELEGRAM INTEGRATION BOT

**Language:** Python  
**README Language:** English

---

## ⭐ Project Summary
TTBot is an automated trading bot designed to interact with **MetaTrader 5 (MT5)** and **Telegram**.  
Its primary purpose is to receive signals, execute trades, manage operations, and log activity — all in an automated workflow.

The project includes:
- A **Telegram listener** that receives commands or signals  
- An **MT5 handler** that opens, closes, and monitors trades  
- A structured execution flow for testing and validating trading logic  
- Configuration files and build artifacts for packaging the bot

This project demonstrates the fundamentals of algorithmic trading automation and message‑based control using Telegram.

---

## 🧩 Technologies & Skills Demonstrated

### **Trading Automation**
- Interaction with **MetaTrader 5 API**
- Automated order execution  
- Trade management and testing scripts  
- Logging of trading operations  

### **Telegram Bot Integration**
- Command listener  
- Structured message handling  
- Session persistence via `.session` files  

### **Python Development**
- Modular codebase  
- Use of configuration files (`config.json`)  
- Packaging with `.spec` (PyInstaller)  
- Test scripts for MT5 and trading operations  

### **Software Engineering Practices**
- Separation of concerns (Telegram ↔ Trading logic)  
- Configurable environment  
- Script organization and testing  

---

## 📁 Project Structure

```
MT5-Trading-Bot-Telegram-Signals/
└── src/
    ├── config.json              → Bot configuration (tokens, settings, credentials)
    ├── TTBot.py                 → Main bot logic
    ├── TelegramList.py          → Telegram listener / processor
    ├── Mt5Test.py               → MT5 connection test script
    ├── OperationTest.py         → Trade operation testing
    ├── lector.session           → Telegram session cache
    ├── lector_session.session   → Telegram session backup
    ├── build/                   → Build artifacts
    ├── dist/                    → PyInstaller packaged executables
    └── TTBot.spec               → PyInstaller configuration
```

### Design Philosophy
- **Telegram in, MT5 out:** Bot receives messages → applies logic → places trades.  
- **Testability:** Separate scripts validate MT5 connection and operation flow.  
- **Configurability:** Credentials and parameters stored in JSON instead of hard‑coded.  
- **Packagable:** `.spec` file enables building a standalone executable for deployment.

---

## 🔍 Project Details

### **Main Bot (TTBot.py)**
Handles:
- Initialization  
- Loading configuration  
- Starting Telegram listener  
- Connecting to MT5  
- Running the main event loop  

### **Telegram Listener (TelegramList.py)**
Responsible for:
- Receiving signals or commands  
- Parsing and forwarding them to TTBot  
- Managing session files  

### **Trading Logic**
Scripts include:
- **Mt5Test.py** — tests broker login, symbol availability, and MT5 API status  
- **OperationTest.py** — simulates/open/close trade operations without using the full bot  

---

## ▶️ How to Run the Project

### **1. Install dependencies**
```
pip install MetaTrader5 telethon
```

(Optional additional packages depending on code details.)

### **2. Configure the bot**
Edit `src/config.json`:
- Telegram API credentials  
- MT5 login & password  
- Trading parameters (symbol, lot size, risk settings…)  

### **3. Run test scripts (recommended)**
Check MT5 connection:
```
python Mt5Test.py
```

Check trading operations:
```
python OperationTest.py
```

### **4. Start the full bot**
```
python TTBot.py
```

### **5. (Optional) Build executable**
Using PyInstaller:
```
pyinstaller TTBot.spec
```
Result will appear under `dist/`.

---

## ✔ Summary
TTBot is a fully‑structured automated trading bot that integrates **Telegram messaging** with **MetaTrader 5 trading**.  
It provides:
- A clean modular Python architecture  
- Automated trading logic  
- Testable MT5 and Telegram components  
- Configurability and deployability through a `.spec` file  

Ideal for experimenting with automated trading or building more advanced trading strategies.

