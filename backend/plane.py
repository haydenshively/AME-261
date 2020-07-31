import math
import numpy as np

g0 = 9.80655  # m/s


class Plane:
    def __init__(self, Cd_0, e_w, S, b, Cl_max, Lam, tc_max, W_struct, W_fuel, W_engines, W_payload, cj, T_a_sl, n_struct, atmosphere):
        # design parameters
        self.Cd_0 = Cd_0                # Profile drag coefficient
        self.e_w = e_w                  # Oswalt Aircraft Efficiency
        self.S = S                      # [m^2]
        self.b = b                      # [m]
        self.Cl_max = Cl_max            # Maximum lift coefficient
        self.Lam = Lam                  # Wing sweep angle [degrees]
        self.tc_max = tc_max            # Max t/c
        self.W_struct = W_struct
        self.W_fuel = W_fuel
        self.W_engines = W_engines
        self.W_payload = W_payload
        # self.W_0 = W_0                  # Weight at takeoff [N]
        # self.W_1 = W_1                  # Weight without fuel [N]
        self.cj = cj/60/60 if cj else cj# Specific fuel consumption [N-fuel/N-thrust/hr] -> convert to seconds
        self.T_a_sl = T_a_sl            # Maximum thrust at sea level [N]
        self.n_struct = n_struct        # Structural load factor
        # # computed
        # self.MAC = S / b
        # self.AR = b ** 2 / S
        # self.K = 1.0 / (math.pi * self.e_w * self.AR)
        # environment
        self.atmosphere = atmosphere
        self.set_altitude(0.0)

    @property
    def MAC(self):
        return self.S / self.b

    @property
    def AR(self):
        return self.b ** 2 / self.S

    @property
    def K(self):
        return 1.0 / (math.pi * self.e_w * self.AR)

    @property
    def W_0(self):
        return self.W_struct + self.W_fuel + self.W_engines + self.W_payload

    @property
    def W_1(self):
        return self.W_struct + self.W_engines + self.W_payload

    @property
    def Cl_min_drag(self):
        return math.sqrt(math.pi * self.e_w * self.AR * self.Cd_0)

    @property
    def LoverDmax(self):
        return math.sqrt(1 / (4 * self.K * self.Cd_0))

    @property
    def Em(self):
        return self.LoverDmax

    @property
    def ToverWmax(self):
        return self.jet_thrust_available() / self.W_0

    @property
    def n_aero(self):
        return self.LoverDmax * self.ToverWmax

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
        return self.W_0 / (q * self.S)

    def Cd_i(self, Cl):
        return Cl ** 2 * self.K

    def Cd(self, Cd_i, Cd_c=0):
        return self.Cd_0 + Cd_i + Cd_c

    def speed(self, Cl, n=1.0):
        return np.sqrt(2 * n * self.W_0 / (self.atm_density * self.S * Cl))

    def speed_stall(self):
        return self.speed(self.Cl_max)

    # equivalent to speed for L/D max
    def speed_Dmin(self):
        Cl = np.sqrt(self.Cd_0 / self.K)
        return self.speed(Cl)

    def speed_PRmin(self):
        Cl = np.sqrt(3 * self.Cd_0 / self.K)
        return self.speed(Cl)

    # slightly higher than speed for minimum drag; designed to be a good compromise
    # for cruise speed. see Anderson page 521
    def speed_carson(self):
        return max(self.speed_Dmin(), self.speed_stall()) * 1.32

    def speed_takeoff(self):
        return 1.2 * self.speed_stall()

    def speed_landing(self):
        return 1.3 * self.speed_stall()

    def drag(self, Cd, speed):
        q = Plane.convert_speed_to_q(self.atm_density, speed)
        return Cd * q * self.S

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

    def max_range_const_h(self, Cl, Cd_c=0):
        # max when Cl = sqrt(Cd_0 / (3*k))
        term1 = (2 / self.cj)
        term2 = np.sqrt(2 / (self.atm_density * self.S))
        term3 = np.sqrt(Cl) / self.Cd(self.Cd_i(Cl), Cd_c)
        term4 = np.sqrt(self.W_0) - np.sqrt(self.W_1)
        return term1 * term2 * term3 * term4

    def max_range_const_speed(self, speed, Cd_c=0):
        # max when Cl = sqrt(Cd_0 / (3*k))
        # --> max when V = 1.316V_Dmin
        # W / atm_density must be constant
        Cl = self.Cl(speed)
        E = Cl / self.Cd(self.Cd_i(Cl), Cd_c)
        return (speed * E / self.cj) * np.log(self.W_0 / self.W_1)

    def max_range(self, Cd_c=0):
        # TODO could incorporate more stuff
        return self.max_range_const_h(np.sqrt(self.Cd_0 / 3 / self.K), Cd_c)

    def q_min_max(self, thrust_available):
        coeff = thrust_available / (2 * self.Cd_0 * self.S)
        fact = 4 * self.K * self.Cd_0 * (self.W_0 / thrust_available) ** 2
        fact = np.sqrt(1 - fact)
        q_min = coeff * (1 - fact)
        q_max = coeff * (1 + fact)
        return np.vstack((q_min, q_max))

    def speed_min_max(self, thrust_available):
        return Plane.convert_q_to_speed(self.atm_density, self.q_min_max(thrust_available))

    def critical_mach(self, Cl, supercritical_foil=False):
        # Note: Do not use this function if Cl > 1.4
        # Cl[Cl > 1.4] = 0
        if supercritical_foil:
            mach_zero_sweep = 0.95 - 0.175 * Cl - 0.83 * self.tc_max
        else:
            mach_zero_sweep = 0.87 - 0.175 * Cl - 0.83 * self.tc_max
        m = 0.83 - 0.583 * Cl + 0.111 * Cl ** 2
        mach_some_sweep = mach_zero_sweep / np.power(math.cos(math.radians(self.Lam)), m)
        return mach_some_sweep

    def Cd_c(self, Cl, speed, supercritical_foil=False):
        mach = speed / self.sound_speed
        x = mach / self.critical_mach(Cl, supercritical_foil)
        y = 3.97 * np.power(10.0, -9) * np.exp(12.7 * x)
        y += np.power(10.0, -40) * np.exp(81 * x)
        result = y * math.pow(math.cos(math.radians(self.Lam)), 3)
        # filter out weird spikes, likely caused by negatives and float precision errors
        # result[result > result[-10]] = 0
        return result

    def ground_effect(self, wing_height):
        fact = 16 * wing_height / self.b
        return fact**2 / (1 + fact**2)

    def d_takeoff(self, rolling_coeff, wing_height):
        # uses Anderson Eq. 6.103
        numerator = self.W_0**2 * 1.44
        thrust = self.jet_thrust_available()
        # calculate average value of all retarding forces (use V=0.7V_lo)
        speed = 0.7 * self.speed_takeoff()
        Cd_i = self.ground_effect(wing_height) * self.Cd_i(self.Cl_max)
        drag = self.drag(self.Cd(Cd_i), speed)
        lift = Plane.convert_speed_to_q(self.atm_density, speed) * self.S * self.Cl_max
        friction = rolling_coeff * (self.W_0 - lift)
        retarding = drag + max(0, friction)
        # bring it all together
        denominator = g0 * self.atm_density * self.S * self.Cl_max * (thrust - retarding)
        return numerator / denominator

    def d_landing(self, rolling_coeff, wing_height, percent_T_r):
        # uses Anderson Eq. 6.113
        numerator = self.W_1**2 * 1.69
        thrust = self.jet_thrust_available() * percent_T_r
        # calculate average value of all retarding forces (use V=0.7V_T)
        speed = 0.7 * self.speed_landing()
        Cd_i = self.ground_effect(wing_height) * self.Cd_i(self.Cl_max)
        drag = self.drag(self.Cd(Cd_i), speed)
        lift = Plane.convert_speed_to_q(self.atm_density, speed) * self.S * self.Cl_max
        friction = rolling_coeff * (self.W_1 - lift)
        retarding = drag + max(0, friction)
        # bring it all together
        denominator = g0 * self.atm_density * self.S * self.Cl_max * (thrust + retarding)
        return numerator / denominator

    def d_takeoff_virginiatech(self, rolling_coeff, wing_height, const = 0):
        # http://www.dept.aoe.vt.edu/~lutze/AOE3104/takeoff&landing.pdf
        Cd_i = self.ground_effect(wing_height) * self.Cd_i(self.Cl_max)
        Cd = self.Cd(Cd_i)
        A = g0 * (self.jet_thrust_available() / self.W_0 - rolling_coeff)
        B = (g0 / self.W_0) * (0.5 * self.atm_density * self.S * (Cd - rolling_coeff*self.Cl_max) + const)
        return (0.5 / B) * np.log(A / (A - self.speed_takeoff()**2 * B))



    @staticmethod
    def convert_q_to_speed(atm_density, q):
        return np.sqrt(2 * q / atm_density)

    @staticmethod
    def convert_speed_to_q(atm_density, speed):
        return 0.5 * atm_density * np.square(speed)

    @staticmethod
    def sigma(atm_density, atm_density_sl):
        return atm_density / atm_density_sl

    """The following methods are for banking jet planes in level, unaccelerated flight"""
    @property
    def structural_bank_limit(self):
        return math.degrees(math.acos(1.0 / self.n_struct))

    @staticmethod
    def load_factor_required_for(speed, radius):
        return np.sqrt(1.0 + np.square(speed * speed / (g0 * radius)))

    def lift_required_for(self, speed, radius):
        return self.W_0 * Plane.load_factor_required_for(speed, radius)

    def Cl_required_for(self, speed, radius):
        q = Plane.convert_speed_to_q(self.atm_density, speed)
        return self.lift_required_for(speed, radius) / (q * self.S)

    def turning_radius(self, speed, load_factor):
        q = Plane.convert_speed_to_q(self.atm_density, speed)
        return 2 * q / (self.atm_density * g0 * np.sqrt(np.square(load_factor) - 1))

    @staticmethod
    def turning_rate(speed, load_factor):
        return np.degrees(g0 * np.sqrt(np.square(load_factor) - 1) / speed)

    @staticmethod
    def n_for_bank(angle):
        return 1.0 / np.cos(np.radians(angle))

    def n_cl_max(self, speed):
        q = Plane.convert_speed_to_q(self.atm_density, speed)
        return self.Cl_max * q * self.S / self.W_0

    def n_thrust(self, speed):
        q = Plane.convert_speed_to_q(self.atm_density, speed)
        part = self.jet_thrust_available() - (self.Cd_0 * q * self.S)
        part *= q * self.S / self.K
        part /= np.square(self.W_0)
        return np.sqrt(part)
