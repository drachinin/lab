"""Исключения приложения для бронирования билетов."""


class BookingError(Exception):
    """Базовая ошибка предметной области."""


class ValidationError(BookingError):
    """Ошибка проверки введённых данных."""


class NotFoundError(BookingError):
    """Запрошенная запись не найдена."""


class StorageError(BookingError):
    """Ошибка чтения или записи файла."""
