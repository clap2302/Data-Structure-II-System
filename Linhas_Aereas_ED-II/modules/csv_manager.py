import csv
import os

class CSVManager:

    @staticmethod
    def add_user(dataList: list, path: str = '../archives/users.csv') -> int:
        keys = ["name", "user", "password", "cpf", "miles", "dateAndTime", "duration"]
        data = dict(zip(keys, dataList))

        # Ler arquivo se existir
        try:
            with open(path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []

        line_count = len(lines)

        # Detecta se header existe
        header_exists = False
        if line_count > 0:
            first_line = lines[0].strip()
            expected_header = ",".join(keys)
            header_exists = (first_line == expected_header)

        # Calcula a linha do novo registro
        new_line_number = 1 if not header_exists else line_count

        # Escreve no arquivo
        with open(path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)

            if not header_exists:
                writer.writeheader()

            writer.writerow(data)

        return new_line_number


    @staticmethod
    def get_users(path: str = 'archives/users.csv') -> list:
        registers = []

        if not os.path.exists(path):
            return registers

        with open(path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for line in reader:
                registers.append(line)

        return registers
