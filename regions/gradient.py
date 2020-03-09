import math

# make the assumption that g is constant throughout the atmosphere, equal to its value at sea level
g0 = 9.80655  # m/s
R = 287  # J/(kg*K)


class Gradient:
    def __init__(self, lapse_rate, temperature1, pressure1, density1):
        self.lapse_rate = lapse_rate
        self.temperature1 = temperature1
        self.pressure1 = pressure1
        self.density1 = density1

    def temperature_at(self, altitude):
        return self.temperature1 + self.lapse_rate*altitude

    def pressure_at(self, altitude):
        k = g0 / (R * self.lapse_rate)
        ratio = self.temperature_at(altitude) / self.temperature1
        return self.pressure1 * math.pow(ratio, -k)

    def density_at(self, altitude):
        k = g0 / (R * self.lapse_rate)
        ratio = self.temperature_at(altitude) / self.temperature1
        return self.density1 * math.pow(ratio, -k - 1)
