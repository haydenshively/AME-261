import numpy as np
import matplotlib.pyplot as plt

def plot_flight_envelope(plane):
    print()
    plane.set_altitude_range(0, 25000, 10)

    thrust = plane.jet_thrust_available()
    v_min_max = plane.speed_min_max(thrust)
    v_stall = plane.speed_stall()

    v_min = v_min_max[0]
    v_min = v_min[~np.isnan(v_min)]
    v_max = v_min_max[1]
    v_max = v_max[~np.isnan(v_max)]

    nan_index = v_min.shape[0]
    altitudes = np.arange(0, 25000, 10)[:nan_index]
    v_stall = v_stall[:nan_index]

    ceiling = altitudes.max()
    plane.set_altitude(ceiling)

    # PLOTTING h vs. V_stall and h vs. V
    v_envelope = np.hstack((v_min, v_max[::-1]))
    a_envelope = np.hstack((altitudes, altitudes[::-1]))

    plt.cla()
    plt.clf()

    plt.plot(v_envelope, a_envelope, '-b', label='Flight Envelope')
    plt.plot(v_min.max(), ceiling, marker='o', markersize=5, color='blue', label='Ceiling')
    plt.plot(v_stall, altitudes, '-r', label='V_stall')

    plt.title('Flight Envelope')
    plt.xlabel('Velocity, V [m/s]')
    plt.ylabel('Altitude, h [m]')
    plt.legend(loc='lower center')
    plt.show()