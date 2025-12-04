import json
import os

class ReservationManager:
    RESERVATIONS_FILE = "reservations.json"

    @staticmethod
    def load_reservations() -> dict:
        if not os.path.exists(ReservationManager.RESERVATIONS_FILE):
            return {}

        with open(ReservationManager.RESERVATIONS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}

    @staticmethod
    def save_reservations(reservations: dict) -> None:
        with open(ReservationManager.RESERVATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(reservations, f, indent=4, ensure_ascii=False)

    @staticmethod
    def add_reservation(user: str, flight_code: str) -> bool:
        reservations = ReservationManager.load_reservations()
        user_reservations = reservations.get(user, [])

        if flight_code not in user_reservations:
            user_reservations.append(flight_code)
            reservations[user] = user_reservations
            ReservationManager.save_reservations(reservations)
            return True

        return False
