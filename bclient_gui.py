import tkinter as tk
from tkinter import messagebox
from bclient import BClient

class BClientGUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("BClient GUI")

        self.input_field = tk.Entry(self.root)
        self.input_field.pack()

        self.send_button = tk.Button(self.root, text="Send Data", command=self.send_data)
        self.send_button.pack()

        self.disconnect_button = tk.Button(self.root, text="Disconnect", command=self.disconnect)
        self.disconnect_button.pack()

        self.receive_button = tk.Button(self.root, text="Receive Data", command=self.receive_data)
        self.receive_button.pack()

    def send_data(self):
        text = self.input_field.get()
        try:
            self.client.send_data(text)
            messagebox.showinfo("Success", "Text sent successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def disconnect(self):
        try:
            self.client.disc_bserv()
            messagebox.showinfo("Success", "Disconnected successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def receive_data(self):
        try:
            self.client.recieve_msg()
            messagebox.showinfo("Success", "Data received successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    peer = BClient()
    app = BClientGUI(peer)
    app.run()