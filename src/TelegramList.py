from telethon.sync import TelegramClient
import json

with open("config.json") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]

with TelegramClient('lector', api_id, api_hash) as client:
    dialogs = client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_channel:
            print(f"📡 {dialog.name} → ID: {dialog.id}")
