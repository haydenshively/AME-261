import math
import numpy as np


class Plane:
    def __init__(self, Cd_0, Em, e_w, chord, span, Cl_max, Lam, tc_max, W_0, W_1, cj, T_a_sl, atmosphere):
        # design parameters
        self.Cd_0 = Cd_0        # Profile drag coefficient
        self.Em = Em            # Max Lift-to-Drag ratio
        self.e_w = e_w          # Oswalt Aircraft Efficiency
        self.chord = chord      # [m]
        self.span = span        # [m]
        self.Cl_max = Cl_max    # Maximum lift coefficient
        self.Lam = Lam          # Wing sweep angle [degrees]
        self.tc_max = tc_max    # Max t/c
        self.W_0 = W_0          # Weight at takeoff [N]
        self.W_1 = W_1          # Weight without fuel [N]
        self.cj = cj            # Specific fuel consumption [N-fuel/N-thrust/hr]
        self.T_a_sl = T_a_sl    # Maximum thrust at sea level [N]
        # computed
        self.planform_area = span * chord
        self.AR = span ** 2 / self.planform_area
        self.K = 1.0 / (math.pi * self.e_w * self.AR)
        # environment
        self.atmosphere = atmosphere
        self.set_altitude(0.0)

    @property
    def Cl_min_drag(self):
        return math.sqrt(math.pi * self.e_w * self.AR * self.Cd_0)

    def set_altitude(self, h_in_meters):
        self.sound_speed = self.atmosphere.speed_of_sound_at(h_in_meters)
        self.atm_density = self.atmosphere.density_at(h_in_meters)

    def set_altitude_range(self, min, max, step):
        sound_speed = []
        atm_density = []
        for i in range(min, max, step):
            sound_speed.append(self.atmosphere.speed_of_sound_at(i))
            atm_density.append(self.atmosphere.density_at(i))

        self.sound_speed = np.asarray(sound_speed)
        self.atm_density = np.asarray(atm_density)

    """Computes the value of Cl required to support the plane's weight"""
    def Cl(self, speed):
        q = Plane.convert_speed_to_q(self.atm_density, speed)
        return self.W_0 / (q * self.planform_area)

    def Cd_i(self, Cl):
        return Cl**2 * self.K

    def Cd(self, Cd_i, Cd_c=0):
        return self.Cd_0 + Cd_i + Cd_c

    def speed(self, Cl):
        return np.sqrt(2 * self.W_0 / (self.atm_density * self.planform_area * Cl))

    def speed_stall(self):
        return self.speed(self.Cl_max)

    def drag(self, Cd, speed):
        q = Plane.convert_speed_to_q(self.atm_density, speed)
        return Cd * q * self.planform_area

    def pow_required(self, drag, speed):
        return drag * speed

    def jet_thrust_available(self):
        return self.T_a_sl * Plane.sigma(self.atm_density, self.atmosphere.density_at(0.0))

    def jet_pow_available(self, speed):
        return self.jet_thrust_available() * speed

    def jet_pow_excess(self, drag, speed):
        return self.jet_pow_available(speed) - self.pow_required(drag, speed)

    def rate_of_climb(self, drag, speed):
        return self.jet_pow_excess(drag, speed) / self.W_0

    def q_min_max(self, thrust_available):
        coeff = thrust_available / (2 * self.Cd_0 * self.planform_area)
        fact = 4 * self.K * self.Cd_0 * (self.W_0 / thrust_available)**2
        fact = np.sqrt(1 - fact)
        q_min = coeff * (1 - fact)
        q_max = coeff * (1 + fact)
        return np.vstack((q_min, q_max))

    def speed_min_max(self, thrust_available):
        return Plane.convert_q_to_speed(self.atm_density, self.q_min_max(thrust_available))

    def critical_mach(self, Cl):
        # Note: Do not use this function if Cl > 1.4
        Cl[Cl > 1.4] = 0
        mach_zero_sweep = 0.87 - 0.175*Cl - 0.83*self.tc_max
        m = 0.83 - 0.583*Cl + 0.111*Cl**2
        mach_some_sweep = mach_zero_sweep / np.power(math.cos(math.radians(self.Lam)), m)
        return mach_some_sweep

    def Cd_c(self, Cl, speed):
        mach = speed / self.sound_speed
        x = mach / self.critical_mach(Cl)
        y = 3.97 * np.power(10.0, -9) * np.exp(12.7*x)
        y += np.power(10.0, -40) * np.exp(81*x)
        result = y * math.pow(math.cos(math.radians(self.Lam)), 3)
        # filter out weird spikes, likely caused by negatives and float precision errors
        # result[result > result[-10]] = 0
        return result

    @staticmethod
    def convert_q_to_speed(atm_density, q):
        return np.sqrt(2 * q / atm_density)

    @staticmethod
    def convert_speed_to_q(atm_density, speed):
        return 0.5 * atm_density * np.square(speed)

    @staticmethod
    def sigma(atm_density, atm_density_sl):
        return atm_density / atm_density_sl
