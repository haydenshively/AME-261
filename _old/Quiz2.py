if __name__ == '__main__':
    from haydens_code.atmosphere import std_atm_earth
    from haydens_code.plane import Plane

    q3 = Plane(
        Cd_0=0.020,
        Em=None,
        e=0.9,
        chord=1.0,  # MAC
        span=8.0,
        Cl_max=None,
        Lam=None,
        tc_max=None,
        W_0=1.0,
        W_1=None,
        cj=None,
        T_a_sl=0.2,
        n_struct=None,
        atmosphere=std_atm_earth(),
    )

    print(q3.Cd_0)
    print(q3.AR)
    print(q3.e_w)
    print(q3.T_a_sl/q3.W_0)
    print('')
    print('n_aero: {}'.format(q3.n_aero))
    print('')

    q4 = Plane(
        Cd_0=0.020,
        Em=None,
        e=0.8,
        chord=20 / (200.0**0.5),  # MAC
        span=200.0**0.5,
        Cl_max=1.5,
        Lam=None,
        tc_max=None,
        W_0=10000,
        W_1=None,
        cj=None,
        T_a_sl=3000,
        n_struct=3.0,
        atmosphere=std_atm_earth(),
    )

    q4.set_altitude(0)

    print(q4.S)
    print(q4.W_0)
    print(q4.n_struct)
    print(q4.Cl_max)
    print(q4.T_a_sl)
    print(q4.Cd_0)
    print(q4.AR)
    print(q4.e_w)
    print('')
    n = Plane.n_for_bank(60)
    print(n)
    print(q4.turning_rate(100, n))
    print('')
    print('r_struct: {}'.format(q4.turning_radius(60, q4.n_struct)))
    print('r_thrust: {}'.format(q4.turning_radius(60, q4.n_thrust(60))))
    print('r_cl_max: {}'.format(q4.turning_radius(60, q4.n_cl_max(60))))
