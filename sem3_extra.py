import re

def process_log_file(file_path: str) -> None:
    """
    Обрабатывает лог-файл и выводит сообщения по заданным регулярным выражениям.
    :param file_path: путь к файлу с логами
    :return: None
    """
    with open(file_path, "r", encoding="utf-8") as stream:
        records = stream.readlines()

    pattern_levels = r"^\d{4}-\d{2}-\d{2}\s+(\d{2}:\d{2}:\d{2})\s+(ERROR|WARN)\s+(.+)$"
    pattern_ip_addr = r"^\d{4}-\d{2}-\d{2}\s+(\d{2}:\d{2}:\d{2})\s+([A-Z]+)\s+(.*\b\d{1,3}(?:\.\d{1,3}){3}\b.*)$"

    for entry in records:
        match = re.match(pattern_levels, entry.strip())
        if match:
            t_val, lvl_val, msg_val = match.groups()
            print(f"{t_val} {lvl_val} {msg_val}")

    for entry in records:
        match = re.match(pattern_ip_addr, entry.strip())
        if match:
            t_val, lvl_val, msg_val = match.groups()
            print(f"{t_val} {lvl_val} {msg_val}")


process_log_file("logs.txt")
