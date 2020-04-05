import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    from atmosphere import std_atm_earth
    from plane import Plane

    # Initialize Boeing 777-200 plane object
    plane = Plane(
        Cd_0=0.020,
        Em=None,
        e_w=0.93,
        chord=423 / 61,# MAC
        span=61,
        Cl_max=2.3,
        Lam=31.6,
        tc_max=0.13,
        W_0=2380000,
        W_1=None,
        cj=None,
        T_a_sl=342000*2,
        atmosphere=std_atm_earth()
    )

    """QUESTION 1 and 2 PLOTS ---------------------------------------------------------------------------------------"""
    # FOR 0m --------------------------------------------------------------------------------------------------------
    # compute velocity range
    plane.set_altitude(0)  # meters
    T_a = plane.jet_thrust_available()  # N
    V_limits = plane.speed_min_max(T_a)  # m/s
    V_range = np.arange(V_limits[0, 0], V_limits[1, 0] + 5, 5)
    # compute drag
    Cd_inc = plane.Cd(plane.Cd_i(plane.Cl(V_range)))
    Cd_com = Cd_inc + plane.Cd_c(plane.Cl(V_range), V_range)
    D_inc = plane.drag(Cd_inc, V_range)
    D_com = plane.drag(Cd_com, V_range)
    # compute R/C
    RC_inc = plane.rate_of_climb(D_inc, V_range)
    RC_com = plane.rate_of_climb(D_com, V_range)
    print('% Difference (R/C max @ 0km), Incompressible and Compressible: {}'.format(100 * (RC_inc.max() - RC_com.max()) / RC_inc.max()))
    # plot
    plt.plot(V_range/plane.sound_speed, RC_inc, '-r', label='R/C (incompressible), 0m')
    plt.plot(V_range/plane.sound_speed, RC_com, '--r', label='R/C (compressible), 0m')
    # plt.xlim(V_range.min() - 10, V_range.max() + 10)
    plt.xlim(0, 1.25)
    plt.ylim(0, 50)
    # AGAIN FOR 8000m -----------------------------------------------------------------------------------------------
    # compute velocity range
    plane.set_altitude(8000)  # meters
    T_a = plane.jet_thrust_available()  # N
    V_limits = plane.speed_min_max(T_a)  # m/s
    V_range = np.arange(V_limits[0, 0], V_limits[1, 0] + 5, 5)
    # compute drag
    Cd_inc = plane.Cd(plane.Cd_i(plane.Cl(V_range)))
    Cd_com = Cd_inc + plane.Cd_c(plane.Cl(V_range), V_range)
    D_inc = plane.drag(Cd_inc, V_range)
    D_com = plane.drag(Cd_com, V_range)
    # compute R/C
    RC_inc = plane.rate_of_climb(D_inc, V_range)
    RC_com = plane.rate_of_climb(D_com, V_range)
    print('% Difference (R/C max @ 8km), Incompressible and Compressible: {}'.format(100 * (RC_inc.max() - RC_com.max()) / RC_inc.max()))
    # plot
    plt.plot(V_range/plane.sound_speed, RC_inc, '-b', label='R/C (incompressible), 8km')
    plt.plot(V_range/plane.sound_speed, RC_com, '--b', label='R/C (compressible), 8km')
    # fancy text
    plt.title('R/C vs Mach Number for 777, at 0km and 8km')
    plt.xlabel('Mach Number')
    plt.ylabel('Rate of Climb [m/s]')
    plt.legend(loc='upper left')
    plt.show()

    """QUESTION 3 PLOT ----------------------------------------------------------------------------------------------"""
    plane.set_altitude_range(0, 14000, 100)
    # compute velocity range
    T_a = plane.jet_thrust_available()  # N
    V_limits = plane.speed_min_max(T_a)  # m/s
    V_range = np.linspace(V_limits[0], V_limits[1], 140)
    # compute drag
    Cd_inc = plane.Cd(plane.Cd_i(plane.Cl(V_range)))
    Cd_com = Cd_inc + plane.Cd_c(plane.Cl(V_range), V_range)
    D_inc = plane.drag(Cd_inc, V_range)
    D_com = plane.drag(Cd_com, V_range)
    # compute R/C max
    RC_inc = plane.rate_of_climb(D_inc, V_range).max(axis=0)
    RC_com = plane.rate_of_climb(D_com, V_range).max(axis=0)
    # plot
    plt.plot([i for i in range(0, 14000, 100)], RC_inc, '-b', label='Incompressible')
    plt.plot([i for i in range(0, 14000, 100)], RC_com, '-r', label='Compressible')
    plt.xlim(0, 14000)
    plt.ylim(0, 40)
    # fancy text
    plt.title('R/C max vs Altitude for 777')
    plt.xlabel('Altitude')
    plt.ylabel('Max Rate of Climb [m/s]')
    plt.legend(loc='upper right')
    plt.show()
    # plot % differences
    plt.cla()
    plt.clf()
    plt.plot([i for i in range(0, 14000, 100)], 100 * (RC_inc - RC_com) / RC_inc)
    plt.xlim(0, 14000)
    plt.ylim(0, 40)
    plt.title('% Difference (R/C max values) vs Altitude for 777')
    plt.xlabel('Altitude')
    plt.ylabel('% Difference')
    plt.show()

    """QUESTION 4 MATH ----------------------------------------------------------------------------------------------"""
    # TODO could make this code better by having 'throttle' param in plane class
    plane.set_altitude(9000)  # m
    plane.W_0 = 1870000  # N
    plane.T_a_sl = 0.25 * plane.T_a_sl
    Cd_inc = plane.Cd(plane.Cd_i(plane.Cl(245)))
    D_inc = plane.drag(Cd_inc, 245)
    print('Initial Rate of Descent: {} m/s'.format(plane.rate_of_climb(D_inc, 245)))

    """QUESTION 5 MATH ----------------------------------------------------------------------------------------------"""
    # Part A
    plane.set_altitude(8000)  # m
    T_a = plane.jet_thrust_available() / 2.0  # N
    V_range = np.linspace(40, 300, 140)
    # Part A Numeric
    Cd_inc = plane.Cd(plane.Cd_i(plane.Cl(V_range)))
    D_inc = plane.drag(Cd_inc, V_range)
    print('Can fly steady with 1 engine: {}'.format(V_range[D_inc <= T_a].shape[0] > 0))
    # Part A Graphical
    plt.plot(V_range, D_inc, '-b', label='Thrust Required')
    plt.plot(V_range, [T_a for i in range(140)], '-r', label='Thrust Available')
    plt.title('Thrust vs. Velocity at 9km: 777 with 1 Engine')
    plt.xlabel('Velocity [m/s]')
    plt.ylabel('Thrust [N]')
    plt.legend(loc='upper center')
    plt.show()
    # Part B and C
    # for graphing
    altitudes = []
    distances = []
    plane.T_a_sl = 0  # N
    V_range = np.linspace(1, 300, 150)
    timestep = 10  # seconds
    altitude = 9000  # meters
    distance = 0  # meters
    time = 0  # seconds
    while altitude > 0:
        plane.set_altitude(altitude)

        Cd_inc = plane.Cd(plane.Cd_i(plane.Cl(V_range)))
        D_inc = plane.drag(Cd_inc, V_range)
        RC_inc = plane.rate_of_climb(D_inc, V_range)
        RC_max = RC_inc.max()

        altitude += RC_max * timestep
        distance += V_range[RC_inc.argmax()] * timestep
        time += timestep

        altitudes.append(altitude)
        distances.append(distance)

    plt.plot(distances, altitudes, '-b', label='Keeping Fuel')
    print('Gliding down from 9km, the 777 has a range of {} km'.format(distance/1000))
    print('It will take {} seconds to reach the ground'.format(time))
    print()
    # Part D
    # for graphing
    altitudes = []
    distances = []
    plane.T_a_sl = 0  # N
    plane.W_0 = 1780000  # N
    V_range = np.linspace(1, 300, 150)
    timestep = 10  # seconds
    altitude = 9000  # meters
    distance = 0  # meters
    time = 0  # seconds
    while altitude > 0:
        plane.set_altitude(altitude)

        Cd_inc = plane.Cd(plane.Cd_i(plane.Cl(V_range)))
        D_inc = plane.drag(Cd_inc, V_range)
        RC_inc = plane.rate_of_climb(D_inc, V_range)
        RC_max = RC_inc.max()

        altitude += RC_max * timestep
        distance += V_range[RC_inc.argmax()] * timestep
        time += timestep

        altitudes.append(altitude)
        distances.append(distance)

    plt.plot(distances, altitudes, '-r', label='Dropping Fuel')
    plt.show()
    print('Dumping fuel and gliding down from 9km, the 777 has a range of {} km'.format(distance / 1000))
    print('It will take {} seconds to reach the ground'.format(time))