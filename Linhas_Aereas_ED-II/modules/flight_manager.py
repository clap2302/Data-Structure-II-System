import json
import os

class FlightManager:
    FILE_PATH = "data/flights.json"

    @staticmethod
    def load_flights_dict():
        if not os.path.exists(FlightManager.FILE_PATH):
            return {}

        with open(FlightManager.FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        flights = {}
        for flight in data:
            flights[flight["code"]] = {
                "origin": flight["origin"],
                "destiny": flight["destiny"],
                "miles": flight["miles"],
                "ticket_price": flight["price"],  # <- ajustado
                "airplane_type": flight["airplane_type"],
                "num_seats": flight["num_seats"],
                "reserved": flight.get("reserved_seats", 0),  # <- renomeado
                "flight_datetime": flight["departure_datetime"],  # <- renomeado
                "duration": flight["duration_minutes"]  # <- renomeado
            }

        return flights

    @staticmethod
    def save_flights_dict(flights_dict):
        data = []

        for code, flight in flights_dict.items():
            data.append({
                "code": code,
                "origin": flight["origin"],
                "destiny": flight["destiny"],
                "miles": flight["miles"],
                "price": flight["ticket_price"],
                "airplane_type": flight["airplane_type"],
                "num_seats": flight["num_seats"],
                "reserved_seats": flight["reserved"],
                "departure_datetime": flight["flight_datetime"],
                "duration_minutes": flight["duration"]
            })

        os.makedirs("data", exist_ok=True)

        with open(FlightManager.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
