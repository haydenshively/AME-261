from .regions.isothermal import Isothermal
from .regions.gradient import Gradient


def region_type(lapse_rate):
    if lapse_rate == 0:
        return Isothermal
    else:
        return Gradient


class Atmosphere:
    def __init__(self, data, temperature_sl, pressure_sl, density_sl):
        region = region_type(data[0][1])(data[0][1],
                                         temperature_sl,
                                         pressure_sl,
                                         density_sl)

        self.regions = [(data[0][0], region)]
        data.pop(0)

        for inflection_altitude, lapse_rate in data:
            relative_altitude = inflection_altitude - self.regions[-1][0]

            t = region.temperature_at(relative_altitude)
            p = region.pressure_at(relative_altitude)
            rho = region.density_at(relative_altitude)

            region = region_type(lapse_rate)(lapse_rate, t, p, rho)
            self.regions.append((inflection_altitude, region))

        self.regions.reverse()

    def temperature_at(self, altitude):
        for inflection_altitude, region in self.regions:
            if inflection_altitude <= altitude:
                return region.temperature_at(altitude - inflection_altitude)

    def pressure_at(self, altitude):
        for inflection_altitude, region in self.regions:
            if inflection_altitude <= altitude:
                return region.pressure_at(altitude - inflection_altitude)

    def density_at(self, altitude):
        for inflection_altitude, region in self.regions:
            if inflection_altitude <= altitude:
                return region.density_at(altitude - inflection_altitude)

    def viscosity_coeff_at(self, altitude):
        t = self.temperature_at(altitude)
        return 1.54 * (1 + 0.0039*(t - 250)) * 10**-5

    def speed_of_sound_at(self, altitude):
        t = self.temperature_at(altitude)
        return (1.4 * 287 * t)**0.5

    def knudsen_number_at(self, altitude, A=1.26):
        mu = self.viscosity_coeff_at(altitude)
        rho = self.density_at(altitude)
        t = self.temperature_at(altitude)

        return A * mu / (rho * (287 * t) ** 0.5)


def std_atm_earth():
    """
    Define the different regions of the standard atmosphere
    """
    regions = [
        (0, -0.0065),
        (11000, 0),
        (25000, 0.003)
    ]  # altitude, lapse rate
    """
    Define constants at sea level
    """
    t_sl = 288.16  # K
    p_sl = 101325  # Pa
    rho_sl = 1.2250  # kg/m^3

    # Initialize atmosphere object
    atm = Atmosphere(regions, t_sl, p_sl, rho_sl)
    return atm
