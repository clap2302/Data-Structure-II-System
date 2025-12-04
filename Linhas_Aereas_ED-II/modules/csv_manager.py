import csv
import os

class CSVManager:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, "..", "archives", "users.csv")
    CSV_PATH = os.path.normpath(CSV_PATH)

    @staticmethod
    def add_user(dataList: list, path: str = CSV_PATH) -> int:
        keys = ["name", "user", "password", "cpf", "miles"]
        data = dict(zip(keys, dataList))

        header_exists = False

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8', newline='') as file:
                reader = csv.reader(file)
                first = next(reader, None)
                if first == keys:  # compara lista, não string
                    header_exists = True

        # escreve
        with open(path, 'a', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            if not header_exists:
                writer.writeheader()
            writer.writerow(data)

        return 0

    def remove_user(cpf: str, path: str = CSV_PATH) -> bool:
        """Remove um usuário do CSV baseado no CPF. Retorna True se removeu."""
        
        if not os.path.exists(path):
            return False

        rows = []
        removed = False

        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            header = reader.fieldnames

            for row in reader:
                if row["cpf"] == cpf:
                    removed = True
                    continue
                rows.append(row)

        # Reescrever o arquivo inteiro sem o usuário removido
        with open(path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)

        return removed


    @staticmethod
    def get_users(path: str = CSV_PATH) -> list:
        registers = []

        if not os.path.exists(path):
            return registers

        with open(path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for line in reader:
                registers.append(line)

        return registers
