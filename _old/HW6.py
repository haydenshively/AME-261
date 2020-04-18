import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

if __name__ == '__main__':
    from haydens_code.atmosphere import std_atm_earth
    from haydens_code.plane import Plane

    # Initialize Cessna CJ-1 plane object
    # plane = Plane(
    #     Cd_0=0.020,
    #     Em=16.9,
    #     e_w=0.81,
    #     chord=29.5 / 16.2,
    #     span=16.2,
    #     Cl_max=1.4,
    #     Lam=25.0,
    #     tc_max=0.11,
    #     W_0=88100,
    #     W_fuel=33200,
    #     cj=0.60,
    #     T_a_sl=32500,
    #     atmosphere=std_atm_earth()
    # )

    # Initialize MD-11 plane object
    plane = Plane(
        Cd_0=0.018,
        Em=None,
        e=0.85,
        chord=339 / 51.8,
        span=51.8,
        Cl_max=1.4,
        Lam=35.0,
        tc_max=0.12,
        W_0=2710000,
        W_fuel=None,
        cj=None,
        T_a_sl=800000,
        atmosphere=std_atm_earth()
    )

    """QUESTION 1 PLOT"""
    plane.set_altitude(0)  # meters
    T_a = plane.jet_thrust_available()  # N
    V_limits = plane.speed_min_max(T_a)  # m/s
    V_range = np.arange(V_limits[0, 0], V_limits[1, 0] + 5, 5)
    Cd_inc = plane.Cd(plane.Cd_i(plane.Cl(V_range)))
    Cd_com = Cd_inc + plane.Cd_c(plane.Cl(V_range), V_range)
    D_inc = plane.drag(Cd_inc, V_range)/1000
    D_com = plane.drag(Cd_com, V_range)/1000

    plt.plot(V_range, D_inc, '-r', label='Drag (incompressible)')
    plt.plot(V_range, D_com, '--r', label='Drag (compressible)')
    plt.plot(V_range, [T_a/1000 for i in range(V_range.shape[0])], '-b', label='Thrust Available')

    plt.xlim(V_range.min() - 10, V_range.max() + 10)
    plt.ylim(D_inc.min() - 50, D_inc.max() + 10)

    plt.title('Drag vs Velocity for MD-11 at Sea Level')
    plt.xlabel('Velocity [m/s]')
    plt.ylabel('Drag, Thrust [kN]')
    plt.legend(loc='lower right')
    plt.show()

    """QUESTION 1 TABLE"""
    # Reformat as Strings
    v_str = ['%d' % i for i in V_range]
    t_str = ['%d' % (T_a/1000) for i in V_range]
    di_str = ['%d' % i for i in D_inc]
    dc_str = ['%d' % i for i in D_com]

    data = [[v, t, di, dc] for v, t, di, dc in zip(v_str, t_str, di_str, dc_str)]

    fig, axs = plt.subplots(1, 1)
    fig.set_size_inches(11, 8.5)

    col_labels = ('V [m/s]', 'Thrust Available [kN]', 'Drag (incompressible) [kN]', 'Drag (compressible) [kN]')
    axs.axis('auto')
    axs.axis('off')

    table = axs.table(cellText=data, colLabels=col_labels, loc='center', cellLoc='center')
    # make headers bold
    for (row, col), cell in table.get_celld().items():
        if (row == 0) or (col == -1):
            cell.set_text_props(fontproperties=FontProperties(weight='bold'))

    # show plot
    plt.show()
    # save as PNG file
    fig.savefig('MD11DragTypes.png', dpi=200, bbox_inches='tight', pad_inches=0.5)

    """QUESTION 2"""
    plane.set_altitude(5000)  # meters
    T_a_5000 = plane.jet_thrust_available()  # N
    V_limits = plane.speed_min_max(T_a_5000)  # m/s
    V_range = np.arange(V_limits[0, 0], 300 + 2, 2)
    Cd_5000 = plane.Cd(plane.Cd_i(plane.Cl(V_range)), plane.Cd_c(plane.Cl(V_range), V_range))
    D_5000 = plane.drag(Cd_5000, V_range) / 1000

    plane.set_altitude(10000)  # meters
    T_a_10000 = plane.jet_thrust_available()  # N
    Cd_10000 = plane.Cd(plane.Cd_i(plane.Cl(V_range)), plane.Cd_c(plane.Cl(V_range), V_range))
    D_10000 = plane.drag(Cd_10000, V_range) / 1000

    plt.plot(V_range, D_5000, '-r', label='Drag @ h=5km')
    plt.plot(V_range, [T_a_5000/1000 for _ in range(V_range.shape[0])], '--r', label='Thrust Available @ h=5km')
    plt.plot(V_range, D_10000, '-b', label='Drag @ h=10km')
    plt.plot(V_range, [T_a_10000 / 1000 for _ in range(V_range.shape[0])], '--b', label='Thrust Available @ h=10km')

    plt.ylim(D_5000.min() - 50, 500)

    plt.title('Drag vs Velocity for MD-11')
    plt.xlabel('Velocity [m/s]')
    plt.ylabel('Drag, Thrust [kN]')
    plt.legend(loc='lower left')
    plt.show()
