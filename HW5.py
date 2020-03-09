import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

def QUESTION_2():
    altitudes = []
    densities = []

    for i in range(0, 10000, 1):
        altitudes.append(i)
        densities.append(atm.density_at(i))

    altitudes = np.asarray(altitudes)
    densities = np.asarray(densities)

    plane.atm_density = densities

    sigma = Plane.sigma(densities, 1.225)
    thrust = plane.jet_thrust_available()
    v_min_max = plane.speed_min_max(thrust)
    v_stall = plane.speed_stall()

    v_min = v_min_max[0]
    v_min = v_min[~np.isnan(v_min)]
    v_max = v_min_max[1]
    v_max = v_max[~np.isnan(v_max)]

    nan_index = v_min.shape[0]
    altitudes = altitudes[:nan_index]
    densities = densities[:nan_index]
    sigma = sigma[:nan_index]
    thrust = thrust[:nan_index]
    v_stall = v_stall[:nan_index]

    ceiling = altitudes.max()

    # PLOTTING h vs. V_stall and h vs. V
    v_envelope = np.hstack((v_min, v_max[::-1]))
    a_envelope = np.hstack((altitudes, altitudes[::-1]))

    import matplotlib.pyplot as plt
    plt.cla()
    plt.clf()

    plt.plot(v_envelope, a_envelope, '-b', label='Flight Envelope')
    plt.plot(v_min.max(), ceiling, marker='o', markersize=5, color='blue', label='Ceiling')
    plt.plot(v_stall, altitudes, '-r', label='V_stall')

    plt.title('Flight Envelope for the F-117')
    plt.xlabel('Velocity, V [m/s]')
    plt.ylabel('Altitude, h [m]')
    plt.legend(loc='lower center')
    plt.show()

    # MAKING TABLE
    q_min = Plane.convert_speed_to_q(densities, v_min)
    q_max = Plane.convert_speed_to_q(densities, v_max)

    from matplotlib.font_manager import FontProperties

    plt.cla()
    plt.clf()
    # Reformat as Strings
    a_str = ['%d' % i for i in altitudes[::1500]] + ['%d' % altitudes[-1]] + ['%d' % i for i in altitudes[::1500][::-1]]
    sigma_str = ['%.3f' % i for i in sigma[::1500]] + ['%.3f' % sigma[-1]] + ['%.3f' % i for i in sigma[::1500][::-1]]
    q_str = ['%.1f' % i for i in q_min[::1500]] + ['%.1f' % q_min[-1]] + ['%.1f' % i for i in q_max[::1500][::-1]]
    stall_str = ['%.2f' % i for i in v_stall[::1500]] + ['%.2f' % v_stall[-1]] + ['%.2f' % i for i in
                                                                                  v_stall[::1500][::-1]]
    v_str = ['%.2f' % i for i in v_min[::1500]] + ['%.2f' % v_min[-1]] + ['%.2f' % i for i in v_max[::1500][::-1]]

    data = [[a, s, q, st, v] for a, s, q, st, v in zip(a_str, sigma_str, q_str, stall_str, v_str)]

    fig, axs = plt.subplots(1, 1)
    fig.set_size_inches(11, 8.5)

    col_labels = (
    'Altitude [m]', '\N{GREEK SMALL LETTER SIGMA}(h)', 'Dynamic Pressure [kg/m/s^2]', 'V_stall [m/s]', 'V [m/s]')
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
    fig.savefig('F117EnvelopeTable.png', dpi=200, bbox_inches='tight', pad_inches=0.5)


def QUESTION_3():
    """QUESTION 3"""
    velocities = np.arange(10, 300, 1)
    # For h = 0 m
    density = atm.density_at(0)
    plane.atm_density = density
    thrust = plane.jet_thrust_available()
    P_a_0 = plane.jet_pow_available(thrust, velocities)
    P_r_0 = plane.pow_required(plane.drag(plane.Cd(plane.Cd_i(plane.Cl(velocities))), velocities), velocities)
    # For h = 4500 m
    density = atm.density_at(4500)
    plane.atm_density = density
    thrust = plane.jet_thrust_available()
    P_a_45 = plane.jet_pow_available(thrust, velocities)
    P_r_45 = plane.pow_required(plane.drag(plane.Cd(plane.Cd_i(plane.Cl(velocities))), velocities), velocities)

    plt.cla()
    plt.clf()

    plt.plot(velocities, P_a_0, '--b', label='P_a @ h = 0m')
    plt.plot(velocities, P_r_0, '-b', label='P_r @ h = 0m')
    plt.plot(velocities, P_a_45, '--r', label='P_a @ h = 4500m')
    plt.plot(velocities, P_r_45, '-r', label='P_r @ h = 4500m')

    plt.title('Power Available and Power Required for the F-117')
    plt.xlabel('Velocity, V [m/s]')
    plt.ylabel('Power [W]')
    plt.legend(loc='upper right')
    plt.show()

if __name__ == '__main__':
    from atmosphere import std_atm_earth
    from plane import Plane

    # Initialize atmosphere object
    atm = std_atm_earth()
    # Initialize F-117 Warthog plane object
    plane = Plane(0.042, None, 0.84, 84.8/13.2, 13.2, 1.2, None, None, 187000, 0.0, None, 96000, atm)
    # plane = Plane(187000, 13.2, 84.8/13.2, 0.042, 0.84, 1.2, 96000)

    QUESTION_2()
    QUESTION_3()
