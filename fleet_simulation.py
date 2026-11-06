class Driver:
    def __init__(self, name, license_id):
        self.name = name
        self.license_id = license_id
        self.hours_driven = 0  # track total driving hours

    def drive(self, hours):
        self.hours_driven += hours


class Bus:
    def __init__(self, plate, capacity, fuel_level=100):
        self.plate = plate
        self.capacity = capacity
        self.fuel_level = fuel_level
        self.passengers = 0
        self.driver = None

    def assign_driver(self, driver):
        self.driver = driver

    def board_passengers(self, number):
        self.passengers = min(self.capacity, self.passengers + number)

    def drop_passengers(self, number):
        self.passengers = max(0, self.passengers - number)

    def drive(self, distance_km, fuel_consumption_per_km=0.2):
        fuel_used = distance_km * fuel_consumption_per_km
        self.fuel_level = max(0, self.fuel_level - fuel_used)
        if self.driver:
            self.driver.drive(distance_km / 50)  # assume avg 50 km/h

    def status(self):
        emptiness = 1 - (self.passengers / self.capacity)
        print(f"Bus {self.plate}: {self.fuel_level:.1f}% fuel, "
              f"emptiness {emptiness*100:.1f}%, "
              f"driver: {self.driver.name if self.driver else 'None'}")
