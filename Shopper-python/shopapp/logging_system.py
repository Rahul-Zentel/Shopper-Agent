import sys
import io
from collections import deque
from datetime import datetime
from threading import Lock
from typing import List, Dict

class LogCapture:
    def __init__(self, max_lines: int = 1000):
        self.max_lines = max_lines
        self.logs = deque(maxlen=max_lines)
        self.lock = Lock()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, text: str):
        if text.strip():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {text.strip()}"
            with self.lock:
                self.logs.append(log_entry)
        self.original_stdout.write(text)
        self.original_stdout.flush()

    def flush(self):
        self.original_stdout.flush()

    def get_logs(self, limit: int = None) -> List[str]:
        with self.lock:
            logs_list = list(self.logs)
        if limit:
            return logs_list[-limit:]
        return logs_list

    def clear_logs(self):
        with self.lock:
            self.logs.clear()

log_capture = LogCapture()

def setup_logging():
    sys.stdout = log_capture
    sys.stderr = log_capture

def get_recent_logs(limit: int = 100) -> List[Dict[str, str]]:
    logs = log_capture.get_logs(limit)
    return [{"timestamp": log.split("]")[0][1:], "message": "]".join(log.split("]")[1:]).strip()}
            for log in logs if "]" in log]
