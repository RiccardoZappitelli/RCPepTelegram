import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# -------------------------
# Core abstraction
# -------------------------

class User:
    def __init__(self, name):
        self.name = name
        self.chatroom = None

    def send(self, message: str):
        if self.chatroom:
            self.chatroom.broadcast(self, message)

    def receive(self, sender, message: str):
        raise NotImplementedError


# -------------------------
# Chat mediator
# -------------------------

class ChatRoom:
    def __init__(self):
        self.users = []

    def add_user(self, user: User):
        user.chatroom = self
        self.users.append(user)

    def broadcast(self, sender: User, message: str):
        for user in self.users:
            if user != sender:
                user.receive(sender, message)


# -------------------------
# Backend user (no GUI)
# -------------------------

class BackendUser(User):
    def __init__(self, name, on_receive=None):
        super().__init__(name)
        self.on_receive = on_receive

    def receive(self, sender, message: str):
        if self.on_receive:
            self.on_receive(sender.name, message)


# -------------------------
# GUI user (Tkinter)
# -------------------------

class GUIUser(User):
    def __init__(self, name):
        super().__init__(name)

        self.root = tk.Tk()
        self.root.title(name)

        self.chat_box = ScrolledText(self.root, state="disabled", width=50, height=15)
        self.chat_box.pack(padx=10, pady=5)

        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side="left", padx=(10, 5), pady=5)
        self.entry.bind("<Return>", lambda e:self._send_gui())

        self.send_btn = tk.Button(self.root, text="Send", command=self._send_gui)
        self.send_btn.pack(side="left", padx=(0, 10), pady=5)

    def _send_gui(self):
        msg = self.entry.get().strip()
        if not msg:
            return

        self.entry.delete(0, tk.END)
        self._append(f"You: {msg}")
        self.send(msg)

    def receive(self, sender, message: str):
        self._append(f"{sender.name}: {message}")

    def _append(self, text):
        self.chat_box.configure(state="normal")
        self.chat_box.insert(tk.END, text + "\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see(tk.END)

    def stop(self):
        self.safe_destroy()

    def start(self, stop_event=None):
        if stop_event:
            print(f"[Chat] Polling stop event: {stop_event=}")
            self._poll_stop_event(stop_event)
        self.root.mainloop()

    def _poll_stop_event(self, stop_event):
        if stop_event.is_set():
            print("[Chat] Destroying window")
            self.root.quit()
            self.root.destroy()
            return
        self.root.after(200, self._poll_stop_event, stop_event)

if __name__ == "__main__":
    # -------------------------
    # Example usage
    # -------------------------

    def backend_receive(sender, message):
        print(f"[Backend received] {sender}: {message}")


    chat = ChatRoom()

    backend = BackendUser("BackendUser", on_receive=backend_receive)
    gui_user = GUIUser("GUIUser")

    chat.add_user(backend)
    chat.add_user(gui_user)

    # Backend sends manually
    backend.send("Hello from backend.")

    gui_user.start()