from datetime import datetime

def log_message(user_id, is_bot, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "BOT" if is_bot else "USER"
    
    log_entry = f"[{timestamp}] {prefix}: {text}\n"
    
    with open(f'user_logs/{user_id}.log', 'a', encoding='utf-8') as file:
        file.write(log_entry)