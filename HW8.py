import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    from atmosphere import std_atm_earth
    from plane import Plane

    # Initialize The Global Flyer plane object
    plane = Plane(
        Cd_0=0.016,
        Em=None,
        e_w=0.94,
        chord=37.2 / 34.8,# MAC
        span=34.8,
        Cl_max=1.2,
        Lam=None,
        tc_max=None,
        W_0=98000,
        W_1=14900,
        cj=0.42,
        T_a_sl=10200,
        atmosphere=std_atm_earth()
    )

    plane.set_altitude_range(500, 10000, 100)
    drag = plane.drag(plane.Cd(plane.Cd_i(plane.Cl(80))), 80)
    t_a = plane.jet_thrust_available()
    R_C = 80*(t_a - drag)/98000
    print(R_C)

    plane.set_altitude(10000)
    print(plane.jet_thrust_available())
    print(plane.speed_min_max(plane.jet_thrust_available()))