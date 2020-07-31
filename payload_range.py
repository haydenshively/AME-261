from copy import copy
import numpy as np
import matplotlib.pyplot as plt

def plot_payload_range(plane):
    plane = copy(plane)
    original_payload = plane.W_payload
    original_fuel = plane.W_fuel
    max_payload_if_fuel_full = 424298# a structural limitation
    max_fuel_in_tanks = 54.74 * 1000 * 0.811 * 9.8# Netwons, a tank volume limitation

    plane.set_altitude_range(0, 18120, 100)
    altitudes = np.arange(0, 18120, 100)
    payloads = [p for p in range(0, max_payload_if_fuel_full, 10)] + [max_payload_if_fuel_full]
    ranges = np.zeros((len(payloads), altitudes.shape[0]))

    # assume structural load factor is 2.23
    for i, payload in enumerate(payloads):
        plane.W_payload = payload
        potential_fuel = original_fuel + max_payload_if_fuel_full - payload
        plane.W_fuel = min(potential_fuel, max_fuel_in_tanks)
        r = plane.max_range_const_speed(220, plane.Cd_c(plane.Cl(220), 220, True))
        ranges[i] = r

    ranges[-1] = 0

    plt.plot(ranges[:, 125]/1000, np.array(payloads)/1000, '-b', label='Aircraft Limit')
    plt.plot([0, 16000], 2*[original_payload/1000], '--g', label='Mission Payload')
    plt.xlabel('Range [km]')
    plt.ylabel('Payload [kN]')
    plt.title('Payload Range Chart @ h=12.5km')
    plt.legend()
    plt.show()
    print(np.array(payloads).shape)
    print(ranges.shape)
