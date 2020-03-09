if __name__ == '__main__':
    from atmosphere import std_atm_earth
    from plane import Plane

    # Initialize atmosphere object
    atm = std_atm_earth()
    # Initialize B-2 Spirit plane object
    plane = Plane(1420000, 52.4, 9.1, 0.0090, 0.92, 1.22)

    # Generate data at requested altitudes
    altitudes = []
    speed_const_Cl = []
    speed_stall = []
    drag_const_Cl = []
    drag_210 = []

    for i in range(0, 20001, 500):
        altitudes.append(i)
        density = atm.density_at(i)

        speed_stall.append(plane.speed_stall(density))

        speed = plane.speed(plane.Cl_min_drag, density)
        speed_const_Cl.append(speed)
        Cd_min = plane.Cd(plane.Cd_i(plane.Cl_min_drag))
        drag_const_Cl.append(plane.drag(Cd_min, density, speed))

        speed = 210  # m/s
        Cd = plane.Cd(plane.Cd_i(plane.Cl(density, speed)))
        drag_210.append(plane.drag(Cd, density, speed))

    # Reformat as Strings
    alt_str = ['%d' % i for i in altitudes]
    v_const_Cl_str = ['%.1f' % i for i in speed_const_Cl]
    d_const_Cl_str = ['%.2f' % (i/1000.0) for i in drag_const_Cl]
    d_210_str = ['%.2f' % (i/1000.0) for i in drag_210]

    data = [[a, v_Cl, d_Cl, d_210] for a, v_Cl, d_Cl, d_210 in zip(alt_str, v_const_Cl_str, d_const_Cl_str, d_210_str)]

    # Start working with matplotlib to view data in a table
    from matplotlib import pyplot as plt
    from matplotlib.font_manager import FontProperties

    fig, axs = plt.subplots(1, 1)
    fig.set_size_inches(11, 8.5)

    col_labels = ('Altitude, h [m]', 'V_c | Cl=const [m/s]', 'D(V_c) | Cl=const [kN]', 'D(V_inf = 210 m/s) [kN]')
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
    fig.savefig('DragConditions.png', dpi=200, bbox_inches='tight', pad_inches=0.5)
    # -------------------------------------------------------------------
    plt.cla()
    plt.clf()
    plt.plot(altitudes, speed_const_Cl, '-b', label='V_c | Cl=const')
    plt.plot(altitudes, speed_stall, '-r', label='V_stall')
    plt.plot(altitudes, [210 for a in altitudes], '-g', label='V_inf')
    plt.title('Velocities vs. Altitude')
    plt.xlabel('Altitude [m]')
    plt.ylabel('Velocity [m/s]')
    plt.legend(loc='upper left')
    plt.show()
    # -------------------------------------------------------------------
    plt.cla()
    plt.clf()
    plt.plot(altitudes, drag_const_Cl, '-b', label='D(V_c) | Cl=const')
    plt.plot(altitudes, drag_210, '-r', label='D(V_inf = 210 m/s)')
    plt.title('Drags vs. Altitude')
    plt.xlabel('Altitude [m]')
    plt.ylabel('Drag [N]')
    plt.legend(loc='upper right')
    plt.show()
    # -------------------------------------------------------------------
    plt.cla()
    plt.clf()
    plt.plot([-2,0,2,4,6,8,10,12], [-16.7,25,58.3,85.7,100,105,114,105])
    plt.title('L/D vs. Cl')
    plt.xlabel('Cl')
    plt.ylabel('L/D')
    plt.show()
