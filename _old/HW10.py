import sys
sys.path.append('..')

if __name__ == '__main__':
    from haydens_code.atmosphere import std_atm_earth
    from haydens_code.plane import Plane

    F_22 = Plane(
        Cd_0=0.022,
        Em=None,
        e_w=0.86,
        S=78.0,
        b=13.6,
        Cl_max=1.4,
        Lam=None,
        tc_max=None,
        W_0=222000,
        W_1=None,
        cj=None,
        T_a_sl=300000,
        n_struct=9.0,
        atmosphere=std_atm_earth(),
    )

    Su_27 = Plane(
        Cd_0=0.027,
        Em=None,
        e_w=0.88,
        S=62.0,
        b=14.7,
        Cl_max=1.6,
        Lam=None,
        tc_max=None,
        W_0=178000,
        W_1=None,
        cj=None,
        T_a_sl=150000,
        n_struct=9.5,
        atmosphere=std_atm_earth(),
    )

    # The F-22 is being chased by a Su-27 at an elevation of 6000m.
    F_22.set_altitude(6000)
    Su_27.set_altitude(6000)
    # The F-22's throttle is maxed out. It's flying at 240m/s.
    # Which plane can make a tighter turn?
    # Is there any velocity range in which the Su-27 can make a tighter turn than the F-22?
    print('F-22 can turn with radius \t{}m'.format(F_22.turning_radius(240, F_22.n_thrust(240))))
    print('Su-27 can turn with radius \t{}m'.format(Su_27.turning_radius(240, Su_27.n_thrust(240))))
    # Compute the turning limitations for both planes due to n_struct, Cl_max, and thrust.
    # Plot all data on one chart for a turning radius up to 1800m over the range 0 -> q -> 25000N/m^2
    # Ignore compressibility!

    import numpy as np
    import matplotlib.pyplot as plt

    q = np.linspace(0, 25000, 2500)
    v = Plane.convert_q_to_speed(F_22.atm_density, q)

    envelope_struct_f22 = F_22.turning_radius(v, F_22.n_struct)
    envelope_cl_max_f22 = F_22.turning_radius(v, F_22.n_cl_max(v))
    envelope_thrust_f22 = F_22.turning_radius(v, F_22.n_thrust(v))

    envelope_struct_su27 = Su_27.turning_radius(v, Su_27.n_struct)
    envelope_cl_max_su27 = Su_27.turning_radius(v, Su_27.n_cl_max(v))
    envelope_thrust_su27 = Su_27.turning_radius(v, Su_27.n_thrust(v))

    # # Fill regions where they can both fly with purple
    # plt.fill_between(q, envelope_cl_max_f22, 1800, where=q<5620, color=(1.0,0.0,1.0,0.9))
    # plt.fill_between(q, envelope_thrust_su27, 1800, where=q>5620, color=(1.0,0.0,1.0,0.9))
    # # Fill regions where only Su-27 can fly with red
    # plt.fill_between(q, envelope_cl_max_su27, envelope_cl_max_f22, where=q<4410, color=(1.0,0.0,0.0,0.9))
    # plt.fill_between(q, envelope_thrust_su27, envelope_cl_max_f22, where=(q>4410)*(q<5620), color=(1.0,0.0,0.0,0.9))
    # # Fill regions where only F-22 can fly with blue
    # plt.fill_between(q, envelope_cl_max_f22, envelope_thrust_su27, where=(q>5620)*(q<6300), color=(0.0,0.0,1.0,0.9))
    # plt.fill_between(q, envelope_thrust_f22, envelope_thrust_su27, where=q>6300, color=(0.0,0.0,1.0,0.9))

    plt.plot(q, envelope_struct_f22, '-b', label='F-22 n_struct')
    plt.plot(q, envelope_cl_max_f22, '--b', label='F-22 n_cl_max')
    plt.plot(q, envelope_thrust_f22, ':b', label='F-22 n_thrust')

    plt.plot(q, envelope_struct_su27, '-r', label='Su-27 n_struct')
    plt.plot(q, envelope_cl_max_su27, '--r', label='Su-27 n_cl_max')
    plt.plot(q, envelope_thrust_su27, ':r', label='Su-27 n_thrust')

    plt.xlim(0, 25000)
    plt.ylim(0, 1800)
    plt.title('Turning Envelope at 6000m for F-22 and Su-27')
    plt.xlabel('Dynamic Pressure [N/m^2]')
    plt.ylabel('Turning Radius [m]')
    plt.legend(loc='lower right')
    plt.show()

    # 4a numerical solve
    speed = 100
    thrust = F_22.jet_thrust_available() / 2.0
    drag = 0
    while drag < thrust:
        speed += 0.1
        drag = F_22.drag(F_22.Cd(F_22.Cd_i(F_22.Cl(speed))), speed)

    print(speed)
    print(Plane.convert_speed_to_q(F_22.atm_density, speed))
