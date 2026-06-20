from telegram_alerts import TelegramAlerts
tg = TelegramAlerts(token="8941980034:AAHEbSWvm9ebGQsWyMEoXChZKlvyD8s5oQI", chat_id="8966556590")
tg.send_message("Test message - reply if you see this!")
print("Sent!")