import threading
import time
import config

# Thread lock
lock = threading.Lock()


def log_request(ip_address, filename, status_code):
    with lock:
        try:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            file_name = filename.lstrip('/') if isinstance(filename, str) else str(filename)
            if file_name == '':
                file_name = config.DEFAULT_PAGE
            log_entry = f"{ip_address}, {timestamp}, {file_name}, {status_code}\n"
            with open(config.LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")
