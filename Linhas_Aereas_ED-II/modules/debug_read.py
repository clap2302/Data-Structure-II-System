from flight_manager import FlightManager

f = FlightManager.load_flights_dict()
print("Total flights:", len(f))
for k, v in list(f.items())[:3]:
    print(k, v)
