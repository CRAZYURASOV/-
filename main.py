#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Мини-эмулятор оболочки (этап 1)
Требования:
 - GUI с заголовком "Эмулятор - [username@hostname]"
 - Раскрытие переменных окружения ($VAR, ${VAR})
 - Заглушки команд: ls, cd (печатают своё имя и аргументы)
 - Команда exit
 - Демонстрация ошибок
"""

import os
import shlex
import socket
import getpass
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

class ShellEmulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.user = getpass.getuser()
        self.host = socket.gethostname()
        self.title(f"Эмулятор - [{self.user}@{self.host}]")
        self.geometry("800x500")

        # Текущая директория эмулятора (синхронизирована с реальной, но можно отозвать)
        self.cwd = os.getcwd()

        # UI: окно вывода и поле ввода
        self.output = scrolledtext.ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 11))
        self.output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        entry_frame = tk.Frame(self)
        entry_frame.pack(fill=tk.X, padx=6, pady=(0,6))
        self.prompt_label = tk.Label(entry_frame, text=self._prompt_text(), font=("Consolas", 11))
        self.prompt_label.pack(side=tk.LEFT)

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(entry_frame, textvariable=self.input_var, font=("Consolas", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

        # показать приветствие
        self._print_intro()

    def _prompt_text(self):
        # Формируем короткую подсказку вида: username@host:cwd$
        short_cwd = os.path.basename(self.cwd) or self.cwd
        return f"{self.user}@{self.host}:{short_cwd}$ "

    def _print_intro(self):
        self._write(f"Эмулятор оболочки (REPL) — прототип\nОС: {os.name}  Текущая директория: {self.cwd}\n")
        self._write("Поддерживаемые (заглушки): ls, cd, exit\nПримеры: ls -la $HOME    cd /path    exit\n\n")

    def _write(self, text):
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def on_enter(self, event=None):
        raw = self.input_var.get()
        self.input_var.set("")  # очистить поле ввода
        if raw.strip() == "":
            return
        # отобразить команду в выводе вместе с подсказкой
        self._write(self._prompt_text() + raw + "\n")
        try:
            self.execute_line(raw)
        except Exception as e:
            self._write(f"Ошибка выполнения: {e}\n")

        # обновить подсказку (например, после cd)
        self.prompt_label.config(text=self._prompt_text())

    def expand_env(self, s: str) -> str:
        """
        Раскрытие переменных окружения в строке.
        Используем os.path.expandvars (поддерживает $VAR и ${VAR}).
        """
        return os.path.expandvars(s)

    def parse_command(self, line: str):
        """
        Разбор строки команды:
         - раскрытие переменных окружения
         - разделение на токены с учётом кавычек (shlex)
        Возвращает (cmd, args_list).
        """
        expanded = self.expand_env(line)
        try:
            tokens = shlex.split(expanded)
        except ValueError as e:
            raise RuntimeError(f"Ошибка парсинга: {e}")
        if not tokens:
            return None, []
        return tokens[0], tokens[1:]

    def execute_line(self, line: str):
        cmd, args = self.parse_command(line)
        if cmd is None:
            return

        # обработка встроенных команд (заглушки)
        if cmd == "exit":
            self._write("exit\n")
            self.quit()
            return

        if cmd == "ls":
            # заглушка: выводим имя команды и аргументы
            self._write(f"[ls] аргументы: {args}\n")
            # в качестве небольшой "демонстрации" можем показать содержимое текущей директории без фильтров
            try:
                files = os.listdir(self.cwd)
                self._write("Содержимое (рут каталога эмулятора):\n")
                for name in files:
                    self._write("  " + name + "\n")
            except Exception as e:
                self._write(f"Ошибка при чтении директории: {e}\n")
            return

        if cmd == "cd":
            # заглушка: печать аргументов и пробуем сменить директорию
            self._write(f"[cd] аргументы: {args}\n")
            target = args[0] if args else os.path.expanduser("~")
            # путь относительный к текущей директории эмулятора
            new_path = os.path.abspath(os.path.join(self.cwd, target)) if not os.path.isabs(target) else target
            try:
                os.chdir(new_path)  # синхронизируем с реальной ОС (можно убрать, но полезно)
                self.cwd = os.getcwd()
                self._write(f"Перешли в: {self.cwd}\n")
            except Exception as e:
                self._write(f"cd: {e}\n")
            return

        # неизвестная команда -> ошибка
        self._write(f"Команда не найдена: {cmd}\n")

def main():
    app = ShellEmulator()
    app.mainloop()

if __name__ == "__main__":
    main()
