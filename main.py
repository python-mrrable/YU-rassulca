import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import logging
from browser_handler import start_process

class App:
    def __init__(self, master):
        self.master = master
        master.title("Рассылка в Яндекс Услуги")
        master.geometry("600x400")

        self.url_file = tk.StringVar()
        self.message_file = tk.StringVar()
        self.proxy_file = tk.StringVar()
        self.threads = tk.StringVar(value="1")

        tk.Label(master, text="Файл с URL:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(master, textvariable=self.url_file, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(master, text="Выбрать", command=lambda: self.load_file(self.url_file)).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(master, text="Файл с сообщениями:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(master, textvariable=self.message_file, width=40).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(master, text="Выбрать", command=lambda: self.load_file(self.message_file)).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(master, text="Файл с прокси:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(master, textvariable=self.proxy_file, width=40).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(master, text="Выбрать", command=lambda: self.load_file(self.proxy_file)).grid(row=2, column=2, padx=5, pady=5)

        tk.Label(master, text="Количество потоков:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(master, textvariable=self.threads, width=5).grid(row=3, column=1, padx=5, pady=5)

        self.log_text = scrolledtext.ScrolledText(master, state='disabled', width=70, height=15)
        self.log_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        self.start_button = tk.Button(master, text="Запустить", command=self.start_process)
        self.start_button.grid(row=5, column=0, pady=10)

        self.stop_button = tk.Button(master, text="Остановить", command=self.stop_process, state='disabled')
        self.stop_button.grid(row=5, column=2, pady=10)
        self.stop_flag = threading.Event()

        # Настройка логирования
        self.setup_logging()

    def load_file(self, variable):
        file_path = filedialog.askopenfilename()
        if file_path:
            variable.set(file_path)

    def setup_logging(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(self)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def write(self, message):
        def append():
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, message)
            self.log_text.configure(state='disabled')
            self.log_text.yview(tk.END)
        
        self.log_text.after(0, append)

    def flush(self):
        pass

    def start_process(self):
        url_file = self.url_file.get()
        message_file = self.message_file.get()
        proxy_file = self.proxy_file.get()
        threads = int(self.threads.get())

        if not url_file or not message_file:
            tk.messagebox.showerror("Ошибка", "Пожалуйста, выберите все необходимые файлы.")
            return
        
        self.stop_flag.clear()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        threading.Thread(target=self.run_process, args=(url_file, message_file, proxy_file, threads)).start()

    def stop_process(self):
        self.stop_flag.set()

    def run_process(self, url_file, message_file, proxy_file, threads):
        try:
            start_process(url_file, message_file, proxy_file, threads, self.stop_flag)
        finally:
            self.master.after(0, self.on_process_finish)

    def on_process_finish(self):
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()