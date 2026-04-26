# desktop_app.py
import webview
from task_manager import app
import threading

def run_flask():
    app.run(port=5000)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    webview.create_window('My Tasks', 'http://127.0.0.1:5000')
    webview.start()