"""Консольный интерфейс лабораторной работы № 1, вариант 9."""
from pathlib import Path
from datetime import datetime
from service import BookingService
from storage import JsonStorage, XmlStorage
from exceptions import BookingError

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "data" / "data.json"
XML_PATH = ROOT / "data" / "data.xml"

LABELS = {
    "passengers": "Пассажиры", "carriers": "Перевозчики",
    "transport_types": "Виды транспорта", "stations": "Станции",
    "routes": "Маршруты", "vehicles": "Транспортные средства",
    "trips": "Рейсы", "seats": "Места", "bookings": "Бронирования",
    "tickets": "Билеты", "payments": "Платежи",
}


def parse_value(value: str):
    value = value.strip()
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


class ConsoleApp:
    def __init__(self) -> None:
        self.service = BookingService()
        self.json_storage = JsonStorage()
        self.xml_storage = XmlStorage()
        if JSON_PATH.exists():
            try:
                self.service.import_data(self.json_storage.load(JSON_PATH))
            except BookingError as exc:
                print(f"Не удалось загрузить стартовые данные: {exc}")

    def run(self) -> None:
        while True:
            print("\\n=== Бронирование билетов на транспорт ===")
            print("1 — список записей  2 — найти по ID  3 — добавить")
            print("4 — изменить  5 — удалить  6 — сохранить JSON")
            print("7 — загрузить JSON  8 — сохранить XML  9 — загрузить XML")
            print("0 — выход")
            command = input("Команда: ").strip()
            try:
                if command == "0":
                    print("Работа завершена.")
                    return
                if command in {"1", "2", "3", "4", "5"}:
                    entity = self.choose_entity()
                    if command == "1":
                        for obj in self.service.list_items(entity):
                            print(vars(obj))
                    elif command == "2":
                        print(vars(self.service.get(entity, int(input("ID: ")))))
                    elif command == "3":
                        values = self.read_values(entity)
                        print("Создано:", vars(self.service.create(entity, values)))
                    elif command == "4":
                        item_id = int(input("ID записи: "))
                        values = self.read_values(entity, partial=True)
                        print("Обновлено:", vars(self.service.update(entity, item_id, values)))
                    else:
                        self.service.delete(entity, int(input("ID записи: ")))
                        print("Запись удалена.")
                elif command == "6":
                    self.json_storage.save(JSON_PATH, self.service.export_data())
                    print("Данные сохранены в JSON.")
                elif command == "7":
                    self.service.import_data(self.json_storage.load(JSON_PATH))
                    print("Данные загружены из JSON.")
                elif command == "8":
                    self.xml_storage.save(XML_PATH, self.service.export_data())
                    print("Данные сохранены в XML.")
                elif command == "9":
                    self.service.import_data(self.xml_storage.load(XML_PATH))
                    print("Данные загружены из XML.")
                else:
                    print("Неизвестная команда.")
            except (BookingError, ValueError, OSError) as exc:
                print(f"Ошибка: {exc}")

    def choose_entity(self) -> str:
        entities = list(LABELS)
        for index, entity in enumerate(entities, 1):
            print(f"{index} — {LABELS[entity]}")
        number = int(input("Тип записи: "))
        if not 1 <= number <= len(entities):
            raise ValueError("Неверный номер типа записи.")
        return entities[number - 1]

    def read_values(self, entity: str, partial: bool = False) -> dict:
        model = __import__("models").MODEL_TYPES[entity]
        values = {}
        for field in model.__dataclass_fields__.values():
            if field.name == "id":
                continue
            if partial and input(f"Изменить {field.name}? (д/н): ").strip().lower() != "д":
                continue
            raw = input(f"{field.name} ({field.type}): ")
            if raw == "" and partial:
                continue
            values[field.name] = parse_value(raw)
        return values


if __name__ == "__main__":
    ConsoleApp().run()
