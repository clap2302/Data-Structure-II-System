import json
import os

class FlightManager:
    # Ajuste o caminho se necessário
    FILE_PATH = "archives/flights.json"

    @staticmethod
    def _read_raw():
        if not os.path.exists(FlightManager.FILE_PATH):
            return None
        with open(FlightManager.FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_flights_dict():
        """
        Retorna um dicionário { code: flight_info_normalized }.
        Aceita como entrada:
          - lista de objetos (seu JSON atual)
          - dicionário já indexado por code
        Normaliza nomes de campos para:
          origin, destiny, miles, ticket_price, airplane_type,
          num_seats, reserved, flight_datetime, duration
        """
        raw = FlightManager._read_raw()
        if raw is None:
            return {}

        flights_out = {}

        # Caso o arquivo já seja um dicionário indexado por código
        if isinstance(raw, dict):
            items = raw.items()
        elif isinstance(raw, list):
            # transformar lista em pares (code, obj)
            items = []
            for obj in raw:
                code = obj.get("code") or obj.get("codigo")
                if not code:
                    continue
                items.append((code, obj))
        else:
            return {}

        for code, obj in items:
            # Mapear com fallback entre pt/en keys
            origin = obj.get("origin") or obj.get("origem")
            destiny = obj.get("destiny") or obj.get("destino")
            miles = obj.get("miles") or obj.get("milhas") or 0
            price = obj.get("price") or obj.get("preco") or obj.get("ticket_price") or 0
            airplane = obj.get("airplane_type") or obj.get("aeronave")
            num_seats = obj.get("num_seats") or obj.get("assentos") or 0
            reserved = obj.get("reserved_seats") or obj.get("reserved") or 0
            flight_dt = obj.get("departure_datetime") or obj.get("flight_datetime") or obj.get("data_hora")
            duration = obj.get("duration_minutes") or obj.get("duration") or 0

            # normalize types
            try:
                miles = int(miles)
            except:
                miles = 0
            try:
                price = float(price)
            except:
                price = 0.0
            try:
                num_seats = int(num_seats)
            except:
                num_seats = 0
            try:
                reserved = int(reserved)
            except:
                reserved = 0
            try:
                duration = int(duration)
            except:
                duration = 0

            flights_out[str(code)] = {
                "origin": origin,
                "destiny": destiny,
                "miles": miles,
                "ticket_price": price,
                "airplane_type": airplane,
                "num_seats": num_seats,
                "reserved": reserved,
                "flight_datetime": flight_dt,
                "duration": duration
            }

        return flights_out

    @staticmethod
    def save_flights_dict(flights_dict):
        """
        Salva convertendo para lista no formato 'JSON canônico' com chaves em inglês.
        """
        data = []
        for code, f in flights_dict.items():
            data.append({
                "code": code,
                "origin": f.get("origin"),
                "destiny": f.get("destiny"),
                "miles": int(f.get("miles", 0)),
                "price": float(f.get("ticket_price", 0)),
                "airplane_type": f.get("airplane_type"),
                "num_seats": int(f.get("num_seats", 0)),
                "reserved_seats": int(f.get("reserved", 0)),
                "departure_datetime": f.get("flight_datetime"),
                "duration_minutes": int(f.get("duration", 0))
            })

        os.makedirs(os.path.dirname(FlightManager.FILE_PATH) or ".", exist_ok=True)
        with open(FlightManager.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all_flights():
        """
        Retorna todos os voos no mesmo formato usado pelo sistema:
        { code: {origin, destiny, miles, ...} }
        """
        return FlightManager.load_flights_dict()
