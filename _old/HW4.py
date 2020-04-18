import sys
sys.path.append('..')

if __name__ == '__main__':
    from haydens_code.atmosphere import std_atm_earth
    from haydens_code.plane import Plane

    # Initialize atmosphere object
    atm = std_atm_earth()
    # Initialize A-10 Warthog plane object
    plane = Plane(145000, 17.6, 2.676, 0.032, 0.87, 1.2, 80000)

    """QUESTION 1 - PART A"""
    altitude = 11500  # m
    plane.set_altitude(altitude)
    density = atm.density_at(altitude)
    thrust_avail = plane.jet_thrust_available()

    # Generate data at requested velocities
    speeds = []
    lift_coeffs = []
    drag_coeffs = []
    drags = []

    for speed in range(20, 301, 5):
        Cl = plane.Cl(speed)
        Cd = plane.Cd(plane.Cd_i(plane.Cl(speed)))
        drag = plane.drag(Cd, speed)

        speeds.append(speed)
        lift_coeffs.append(Cl)
        drag_coeffs.append(Cd)
        drags.append(drag)

    # Start working with matplotlib to view data
    from matplotlib import pyplot as plt
    from matplotlib.font_manager import FontProperties

    plt.plot(speeds, drags, '-r', label='T_r')
    # plt.title('Drag vs. Velocity at 500m')
    plt.xlabel('Velocity [m/s]')
    plt.ylabel('Drag (T_r) [N]')
    # plt.show()

    """QUESTION 1 - PART B"""
    plt.cla()
    plt.clf()
    # Reformat as Strings
    speed_str = ['%d' % i for i in speeds]
    cl_str = ['%.3f' % i for i in lift_coeffs]
    cd_str = ['%.3f' % i for i in drag_coeffs]
    l_d_str = ['%.2f' % (l/d) for l, d in zip(lift_coeffs, drag_coeffs)]
    thrust_str = ['%d' % i for i in drags]

    data = [[v, cl, cd, ld, tr] for v, cl, cd, ld, tr in zip(speed_str, cl_str, cd_str, l_d_str, thrust_str)]

    # Start working with matplotlib to view data in a table
    from matplotlib import pyplot as plt
    from matplotlib.font_manager import FontProperties

    fig, axs = plt.subplots(1, 1)
    fig.set_size_inches(11, 8.5)

    col_labels = ('V_inf [m/s]', 'Cl', 'Cd', 'L/D', 'T_r [N]')
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
    fig.savefig('ThrustRequired.png', dpi=200, bbox_inches='tight', pad_inches=0.5)

    """QUESTION 2"""
    plt.plot(speeds, [thrust_avail for _ in speeds], '-b', label='T_a')
    plt.title('Thrusts vs. Velocity at 500m')
    plt.legend(loc='upper right')
    plt.show()

    """QUESTION 4"""
    Cl_min_drag = plane.Cl_min_drag
    Cd_i_min = plane.Cd_i(Cl_min_drag)
    Cd_min = plane.Cd(Cd_i_min)
    D_min = plane.drag(Cd_min, density, plane.speed(Cl_min_drag))
    print("Minimum Drag @ 500 m: {}".format(D_min))
    print("T_a/D_min: {}".format(thrust_avail/D_min))

    altitudes = []
    stall_drags = []
    T_a_Drag_min_Ratios = []

    for i in range(0, 20001, 500):
        altitudes.append(i)
        density = atm.density_at(i)

        speed = plane.speed(plane.Cl_min_drag)
        Cd_min = plane.Cd(plane.Cd_i(plane.Cl_min_drag))
        drag_min = plane.drag(Cd_min, speed)

        thrust_avail = plane.jet_thrust_available()

        thrust_drag_ratio = thrust_avail/drag_min
        T_a_Drag_min_Ratios.append(thrust_drag_ratio)

        speed_stall = plane.speed_stall()
        Cl_stall = plane.Cl(speed_stall)
        Cd_stall = plane.Cd(plane.Cd_i(Cl_stall))
        stall_drags.append(plane.drag(Cd_stall, speed_stall))

    plt.cla()
    plt.clf()
    plt.plot(altitudes, T_a_Drag_min_Ratios)
    plt.title('T_a/D_min Ratio vs. Altitude')
    plt.xlabel('Altitude [m]')
    plt.ylabel('T_a/D_min Ratio')
    plt.show()

    """QUESTION 5"""
    plt.cla()
    plt.clf()
    plt.plot(altitudes, stall_drags)
    plt.title('Drag @ Stall vs. Altitude')
    plt.xlabel('Altitude [m]')
    plt.ylabel('Drag [N]')
    plt.show()

    # # -------------------------------------------------------------------
    # plt.cla()
    # plt.clf()
    # plt.plot(altitudes, drag_const_Cl, '-b', label='D(V_c) | Cl=const')
    # plt.plot(altitudes, drag_210, '-r', label='D(V_inf = 210 m/s)')
    # plt.title('Drags vs. Altitude')
    # plt.xlabel('Altitude [m]')
    # plt.ylabel('Drag [N]')
    # plt.legend(loc='upper right')
    # plt.show()
    # # -------------------------------------------------------------------
    # plt.cla()
    # plt.clf()
    # plt.plot([-2,0,2,4,6,8,10,12], [-16.7,25,58.3,85.7,100,105,114,105])
    # plt.title('L/D vs. Cl')
    # plt.xlabel('Cl')
    # plt.ylabel('L/D')
    # plt.show()
