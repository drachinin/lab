"""Модели предметной области: бронирование билетов на транспорт."""
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Passenger:
    id: int
    full_name: str
    passport_number: str
    phone: str
    email: str


@dataclass
class Carrier:
    id: int
    name: str
    phone: str


@dataclass
class TransportType:
    id: int
    name: str


@dataclass
class Station:
    id: int
    name: str
    city: str


@dataclass
class Route:
    id: int
    departure_station_id: int
    arrival_station_id: int
    distance_km: float


@dataclass
class Vehicle:
    id: int
    carrier_id: int
    transport_type_id: int
    vehicle_number: str
    seat_count: int


@dataclass
class Trip:
    id: int
    route_id: int
    vehicle_id: int
    departure_time: str
    arrival_time: str
    base_price: float
    status: str = "Запланирован"


@dataclass
class Seat:
    id: int
    vehicle_id: int
    seat_number: str
    seat_class: str


@dataclass
class Booking:
    id: int
    passenger_id: int
    trip_id: int
    seat_id: int
    booking_date: str
    status: str = "Забронирован"


@dataclass
class Ticket:
    id: int
    booking_id: int
    ticket_number: str
    price: float
    issued_at: str


@dataclass
class Payment:
    id: int
    booking_id: int
    amount: float
    payment_method: str
    payment_date: str
    status: str = "Оплачен"


MODEL_TYPES = {
    "passengers": Passenger,
    "carriers": Carrier,
    "transport_types": TransportType,
    "stations": Station,
    "routes": Route,
    "vehicles": Vehicle,
    "trips": Trip,
    "seats": Seat,
    "bookings": Booking,
    "tickets": Ticket,
    "payments": Payment,
}


def model_to_dict(model: Any) -> dict[str, Any]:
    """Преобразует dataclass-объект в обычный словарь."""
    return asdict(model)
