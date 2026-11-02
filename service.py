"""Сервис с CRUD-операциями и проверками связей."""
from dataclasses import fields
from typing import Any
from models import MODEL_TYPES
from exceptions import ValidationError, NotFoundError


class BookingService:
    def __init__(self) -> None:
        self.data: dict[str, dict[int, Any]] = {name: {} for name in MODEL_TYPES}
        self.next_ids: dict[str, int] = {name: 1 for name in MODEL_TYPES}

    def list_items(self, entity: str) -> list[Any]:
        self._check_entity(entity)
        return list(self.data[entity].values())

    def get(self, entity: str, item_id: int) -> Any:
        self._check_entity(entity)
        try:
            return self.data[entity][item_id]
        except KeyError as exc:
            raise NotFoundError(f"Запись {entity} с ID={item_id} не найдена.") from exc

    def create(self, entity: str, values: dict[str, Any]) -> Any:
        self._check_entity(entity)
        self._validate(entity, values)
        model = MODEL_TYPES[entity]
        allowed = {field.name for field in fields(model)}
        unknown = set(values) - allowed - {"id"}
        if unknown:
            raise ValidationError(f"Неизвестные поля: {', '.join(sorted(unknown))}")
        item_id = self.next_ids[entity]
        payload = dict(values)
        payload["id"] = item_id
        try:
            obj = model(**payload)
        except TypeError as exc:
            raise ValidationError(f"Не хватает обязательных полей или есть лишние поля: {exc}") from exc
        self.data[entity][item_id] = obj
        self.next_ids[entity] += 1
        return obj

    def update(self, entity: str, item_id: int, values: dict[str, Any]) -> Any:
        current = self.get(entity, item_id)
        payload = {field.name: getattr(current, field.name) for field in fields(current)}
        payload.update(values)
        payload["id"] = item_id
        self._validate(entity, payload, current_id=item_id)
        try:
            updated = MODEL_TYPES[entity](**payload)
        except TypeError as exc:
            raise ValidationError(str(exc)) from exc
        self.data[entity][item_id] = updated
        return updated

    def delete(self, entity: str, item_id: int) -> None:
        self.get(entity, item_id)
        dependencies = {
            "passengers": ("bookings", "passenger_id"),
            "carriers": ("vehicles", "carrier_id"),
            "transport_types": ("vehicles", "transport_type_id"),
            "stations": ("routes", "departure_station_id"),
            "routes": ("trips", "route_id"),
            "vehicles": ("trips", "vehicle_id"),
            "trips": ("bookings", "trip_id"),
            "seats": ("bookings", "seat_id"),
            "bookings": ("tickets", "booking_id"),
        }
        if entity in dependencies:
            child_entity, foreign_key = dependencies[entity]
            if any(getattr(x, foreign_key) == item_id for x in self.data[child_entity].values()):
                raise ValidationError("Нельзя удалить запись: на неё ссылаются другие записи.")
        if entity == "bookings" and any(x.booking_id == item_id for x in self.data["payments"].values()):
            raise ValidationError("Сначала удалите связанные платежи.")
        del self.data[entity][item_id]

    def _check_entity(self, entity: str) -> None:
        if entity not in MODEL_TYPES:
            raise ValidationError(f"Неизвестный тип записи: {entity}")

    def _validate(self, entity: str, values: dict[str, Any], current_id: int | None = None) -> None:
        self._check_entity(entity)
        positive_fields = {
            "distance_km", "seat_count", "base_price", "price", "amount"
        }
        for key in positive_fields & values.keys():
            if float(values[key]) <= 0:
                raise ValidationError(f"Поле {key} должно быть больше нуля.")
        for key in ("full_name", "name", "city", "vehicle_number", "seat_number",
                    "ticket_number", "passport_number", "departure_time", "arrival_time"):
            if key in values and isinstance(values[key], str) and not values[key].strip():
                raise ValidationError(f"Поле {key} не должно быть пустым.")
        foreign_keys = {
            "routes": {"departure_station_id": "stations", "arrival_station_id": "stations"},
            "vehicles": {"carrier_id": "carriers", "transport_type_id": "transport_types"},
            "trips": {"route_id": "routes", "vehicle_id": "vehicles"},
            "seats": {"vehicle_id": "vehicles"},
            "bookings": {"passenger_id": "passengers", "trip_id": "trips", "seat_id": "seats"},
            "tickets": {"booking_id": "bookings"},
            "payments": {"booking_id": "bookings"},
        }
        for key, target in foreign_keys.get(entity, {}).items():
            if key in values and values[key] not in self.data[target]:
                raise ValidationError(f"Связанная запись {target} с ID={values[key]} не существует.")
        if entity == "routes" and values.get("departure_station_id") == values.get("arrival_station_id"):
            raise ValidationError("Станции отправления и прибытия должны различаться.")
        if entity == "bookings":
            seat_id = values.get("seat_id")
            trip_id = values.get("trip_id")
            seat = self.data["seats"].get(seat_id)
            trip = self.data["trips"].get(trip_id)
            if seat and trip and seat.vehicle_id != trip.vehicle_id:
                raise ValidationError("Выбранное место не относится к транспортному средству рейса.")
            for booking in self.data["bookings"].values():
                if booking.id != current_id and booking.trip_id == trip_id and booking.seat_id == seat_id and booking.status != "Отменён":
                    raise ValidationError("Это место уже забронировано на выбранный рейс.")

    def export_data(self) -> dict[str, list[dict[str, Any]]]:
        return {
            entity: [vars(obj).copy() for obj in records.values()]
            for entity, records in self.data.items()
        }

    def import_data(self, raw: dict[str, list[dict[str, Any]]]) -> None:
        new_data: dict[str, dict[int, Any]] = {name: {} for name in MODEL_TYPES}
        new_next: dict[str, int] = {name: 1 for name in MODEL_TYPES}
        try:
            for entity, model in MODEL_TYPES.items():
                for row in raw.get(entity, []):
                    obj = model(**row)
                    new_data[entity][obj.id] = obj
                    new_next[entity] = max(new_next[entity], obj.id + 1)
        except (TypeError, ValueError, KeyError) as exc:
            raise ValidationError(f"Некорректная структура данных: {exc}") from exc
        old_data, old_next = self.data, self.next_ids
        self.data, self.next_ids = new_data, new_next
        try:
            for entity, records in self.data.items():
                for obj in records.values():
                    self._validate(entity, vars(obj), current_id=obj.id)
        except Exception:
            self.data, self.next_ids = old_data, old_next
            raise
