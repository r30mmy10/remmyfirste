import os
import tarfile
import argparse
import json
from datetime import datetime
import subprocess


class Emulator:
    def __init__(self, user, host, fs_path, log_path):
        self.user = user
        self.host = host
        self.fs_path = fs_path
        self.log_path = log_path
        self.current_dir = '.'
        self.log = []

        # Load virtual filesystem from tar archive
        self.tar = tarfile.open(fs_path, 'r')
        self.fs = {member.name: member for member in self.tar.getmembers()}

        # Run startup script if it exists
        self.run_startup_script()

    def run(self):
        while True:
            command = input(f"[{self.user}@{self.host} {self.current_dir}] $ ")
            self.log_action(command)

            if command == "exit":
                print("Exiting emulator.")
                break
            elif command.startswith("ls"):
                self.handle_ls()
            elif command.startswith("cd"):
                self.handle_cd(command.split()[1:])
            elif command.startswith("wc"):
                self.handle_wc(command.split()[1:])
            elif command.startswith("tac"):
                self.handle_tac(command.split()[1:])
            else:
                print(f"Error: Unknown command '{command}'")

        self.tar.close()
        self.save_log()

    def run_startup_script(self):
        startup_script = "startup.sh"
        if os.path.exists(startup_script):
            try:
                subprocess.run(["bash", startup_script], check=True)
                self.log_action(f"Ran startup script: {startup_script}")
            except subprocess.CalledProcessError as e:
                print(f"Error running startup script: {e}")
                self.log_action(f"Failed to run startup script: {startup_script}")

    def handle_ls(self):
        # Получаем содержимое текущей директории
        current_path = self.current_dir if self.current_dir != '.' else ''
        contents = [name for name in self.fs if name.startswith(current_path) and name != current_path]

        # Фильтруем скрытые файлы и папки
        filtered_contents = [name for name in contents if not os.path.basename(name).startswith('.')]

        if not filtered_contents:
            print(f"Contents of directory '{self.current_dir}': (empty)")
        else:
            print(f"Contents of directory '{self.current_dir}':")
            for item in filtered_contents:
                relative_path = os.path.relpath(item, current_path)
                if '/' not in relative_path or relative_path.index('/') == len(relative_path) - 1:
                    print(relative_path.split('/')[0])

    def handle_cd(self, args):
        if not args:
            print("Error: No directory specified")
            return

        target_dir = args[0]

        # Обработка команды возврата на уровень выше
        if target_dir == "..":
            if self.current_dir == "." or self.current_dir == "/":
                print("Error: Already at root directory")
            else:
                self.current_dir = os.path.dirname(self.current_dir)
            return

        # Формируем новый путь
        potential_path = os.path.normpath(os.path.join(self.current_dir, target_dir)).strip('./')

        # Проверка, существует ли такой путь в виртуальной файловой системе
        if potential_path in self.fs and self.fs[potential_path].isdir():
            self.current_dir = potential_path
        else:
            print(f"Error: Directory '{target_dir}' not found.")

    def handle_wc(self, args):
        if not args:
            print("Error: No file specified")
            return

        file_name = args[0]
        potential_path = os.path.join(self.current_dir, file_name).strip('./')

        if potential_path in self.fs and self.fs[potential_path].isfile():
            file_content = self.tar.extractfile(self.fs[potential_path]).read().decode()
            line_count = len(file_content.splitlines())
            word_count = len(file_content.split())
            char_count = len(file_content)
            print(f"{line_count} {word_count} {char_count} {file_name}")
        else:
            print(f"Error: File '{file_name}' not found.")

    def handle_tac(self, args):
        if not args:
            print("Error: No file specified")
            return

        file_name = args[0]
        potential_path = os.path.join(self.current_dir, file_name).strip('./')

        if potential_path in self.fs and self.fs[potential_path].isfile():
            file_content = self.tar.extractfile(self.fs[potential_path]).read().decode()
            for line in reversed(file_content.splitlines()):
                print(line)
        else:
            print(f"Error: File '{file_name}' not found.")

    def log_action(self, command):
        self.log.append({
            'user': self.user,
            'command': command,
            'timestamp': datetime.now().isoformat()
        })

    def save_log(self):
        with open(self.log_path, 'w') as log_file:
            json.dump(self.log, log_file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True, help="User name for prompt")
    parser.add_argument("--host", required=True, help="Host name for prompt")
    parser.add_argument("--fs", required=True, help="Path to the tar file representing the filesystem")
    parser.add_argument("--log", required=True, help="Path to the log file")

    args = parser.parse_args()
    emulator = Emulator(args.user, args.host, args.fs, args.log)
    emulator.run()

