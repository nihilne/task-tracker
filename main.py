import sys
import socket
import threading
import uvicorn

from app import app
from pystray import Icon, Menu, MenuItem
from PIL import Image

LOCK_PORT = 54052
APP_PORT = 8080


def start_server():
    uvicorn.run(app=app, host="127.0.0.1", port=APP_PORT)


def on_exit(icon, item):
    icon.stop()


def ipc_listener(icon, sock: socket.socket):
    sock.listen(1)
    while True:
        conn, _ = sock.accept()
        msg = conn.recv(1024).decode().strip()
        if msg == "notify":
            icon.notify("Task Tracker is already running.")
        conn.close()


def main():
    image = Image.open("assets/tt.ico")
    menu = Menu(MenuItem("Exit", on_exit))
    icon = Icon("tticon", image, "Task Tracker", menu)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", LOCK_PORT))
    except OSError:
        try:
            s = socket.create_connection(("127.0.0.1", LOCK_PORT), timeout=1)
            s.sendall(b"notify")
            s.close()
        except Exception:
            pass
        sys.exit()

    threading.Thread(target=ipc_listener, args=(icon, sock), daemon=True).start()
    threading.Thread(target=start_server, daemon=True).start()
    icon.run()


if __name__ == "__main__":
    main()
