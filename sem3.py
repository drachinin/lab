import re

def extract_sku(content: str, pattern: str = r"(\d{4}-[A-Z]{2})|([A-Z]{2}-\d{4}(-[A-Z]{3})?)") -> list[str | None]:
    """
    Выделяет артикулы заказов из текста.
    :param content:
    :return:

    Примеры регулярных выражений:
    ([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]){2} (определяем mac)
    [a-z]+@[a-z0-9A-Z]*\.[a-z]*            (определяем email)
    (\b[87]+){1}[\d-9\w]{10}\b             (определяем телефон)
    \b[А-Я]{1}[а-я]+ [А-Я]{1}[а-я]+         (определяем имя)
    """
    result_list = []
    
    if type(content) != str:
        raise TypeError
    if type(pattern) != str:
        raise TypeError
    if type(pattern) != str:
        raise TypeError

    text_lines = content.splitlines()
    for current_line in text_lines:
        match = re.search(pattern, current_line)
        result_list.append(match[0] if match else None)
        
    return result_list


raw_data = open("file.txt", "r").read()
for item in extract_sku(raw_data):
    print(item)
