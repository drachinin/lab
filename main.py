def check_cow_status(sensorCurrent: float | int) -> str:
  
    """
    Вычисление температуры по сигналу датчика и анализ состояния коровы.
    Входные данные: sensorCurrent (int или float) - ток с датчика в мА (диапазон 4-20 мА)
    Выходные данные: итоговая строка со статусом датчика и коровы
    """
  
    if type(sensorCurrent) not in (int, float) or type(sensorCurrent) == bool:
        raise TypeError("Неверный тип сигнала")

    if sensorCurrent < 0:
        raise ValueError("Отрицательное значение сигнала")

    if sensorCurrent == 0:
        return "Получен сигнал 0mA, датчик отключен"
    elif 0 < sensorCurrent <= 3.9 or sensorCurrent >= 20.1:
        return f"Получен сигнал {sensorCurrent}mA, датчик неисправен"

    tempMin = 0.0
    tempMax = 75.0
    measuredTemp = (sensorCurrent - 4) * (tempMax - tempMin) / (20 - 4) + tempMin

    if 37.5 <= measuredTemp <= 39.0:
        cowState = "с коровой все хорошо"
    elif 35.0 <= measuredTemp <= 37.4:
        cowState = "корова замерзла, требуется обогрев"
    elif 39.1 <= measuredTemp <= 39.5:
        cowState = "корова перегрелась, требуется охлаждение"
    elif measuredTemp < 34.9:
        cowState = "требуется внимание (датчик свалился или корова плохо себя чувствует)"
    elif measuredTemp > 39.6:
        cowState = "срочно вызывайте ветеринара, коровка заболела"
    else:
        cowState = "состояние неопределено"

    return f"Получен сигнал датчика {sensorCurrent}mA, датчик исправен, температура {measuredTemp} градусов, {cowState}"


try:
    userValue = float(input("Введите данные датчика (ток в мА): "))
    print(check_cow_status(userValue))
except (ValueError, TypeError):
    print("Введены некорректные данные!")
