"""Сохранение и загрузка данных в JSON и XML."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from exceptions import StorageError


class JsonStorage:
    def save(self, path: str | Path, data: dict[str, Any]) -> None:
        try:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Не удалось сохранить JSON: {exc}") from exc

    def load(self, path: str | Path) -> dict[str, Any]:
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Не удалось загрузить JSON: {exc}") from exc


class XmlStorage:
    def save(self, path: str | Path, data: dict[str, Any]) -> None:
        try:
            root = ET.Element("transport_booking")
            for entity, records in data.items():
                entity_node = ET.SubElement(root, entity)
                for record in records:
                    item = ET.SubElement(entity_node, "item")
                    for key, value in record.items():
                        child = ET.SubElement(item, key)
                        child.text = str(value)
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            tree.write(target, encoding="utf-8", xml_declaration=True)
        except (OSError, TypeError) as exc:
            raise StorageError(f"Не удалось сохранить XML: {exc}") from exc

    def load(self, path: str | Path) -> dict[str, Any]:
        try:
            root = ET.parse(path).getroot()
            result: dict[str, list[dict[str, Any]]] = {}
            int_fields = {"id", "carrier_id", "transport_type_id", "departure_station_id",
                          "arrival_station_id", "route_id", "vehicle_id", "seat_count",
                          "passenger_id", "trip_id", "seat_id", "booking_id"}
            float_fields = {"distance_km", "base_price", "price", "amount"}
            for entity_node in root:
                result[entity_node.tag] = []
                for item in entity_node.findall("item"):
                    row: dict[str, Any] = {}
                    for child in item:
                        value: Any = child.text or ""
                        if child.tag in int_fields:
                            value = int(value)
                        elif child.tag in float_fields:
                            value = float(value)
                        row[child.tag] = value
                    result[entity_node.tag].append(row)
            return result
        except (OSError, ET.ParseError, ValueError) as exc:
            raise StorageError(f"Не удалось загрузить XML: {exc}") from exc
