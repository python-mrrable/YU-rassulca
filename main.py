import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from browser_handler import start_process
import logging

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
        tk.Entry(master, textvariable=self.threads, width=5).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        self.start_button = tk.Button(master, text="Запустить", command=self.start)
        self.start_button.grid(row=4, column=0, columnspan=3, pady=10)

        self.stop_button = tk.Button(master, text="Остановить", command=self.stop, state=tk.DISABLED)
        self.stop_button.grid(row=5, column=0, columnspan=3, pady=10)

        self.log = scrolledtext.ScrolledText(master, height=10, width=70)
        self.log.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        self.process_thread = None
        self.stop_flag = threading.Event()

        self.setup_logger()

    def setup_logger(self):
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.configure(state='disabled')
                    self.text_widget.yview(tk.END)
                self.text_widget.after(0, append)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        text_handler = TextHandler(self.log)
        text_handler.setLevel(logging.INFO)
        text_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(text_formatter)
        logger.addHandler(text_handler)

    def load_file(self, var):
        filetypes = [("Text files", "*.txt"), ("Excel files", "*.xlsx")]
        if var == self.message_file:
            filetypes = [("Excel files", "*.xlsx")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            var.set(filename)

    def start(self):
        if not all([self.url_file.get(), self.message_file.get(), self.proxy_file.get()]):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите все необходимые файлы")
            return

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stop_flag.clear()

        self.process_thread = threading.Thread(target=self.run_process)
        self.process_thread.start()

    def stop(self):
        self.stop_flag.set()
        logging.info("Останавливаем процесс...")
        self.stop_button.config(state=tk.DISABLED)

    def run_process(self):
        try:
            start_process(
                self.url_file.get(),
                self.message_file.get(),
                self.proxy_file.get(),
                int(self.threads.get()),
                self.stop_flag
            )
        except Exception as e:
            logging.error(f"Ошибка: {str(e)}", exc_info=True)
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()