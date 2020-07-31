from copy import copy
import numpy as np
from matplotlib import pyplot as plt

def plot_flight_plan(plane):
    plane = copy(plane)
    # average runway length https://ideas.stantec.com/blog/how-long-is-an-airport-s-runway
    runway_d = 2438.4
    # aircraft may make 90, 180, or 270 deg turns after takeoff. take the average (180)
    pattern_d_to = (runway_d * 2) + (2 * 3.1415 * plane.turning_radius(plane.speed_takeoff(), 3.349))
    # unless flying straight in (rare), aircraft turn in an S shape before landing
    # this takes approx. 3 runway lengths
    pattern_d_lo = runway_d * 3 + (2 * 3.1415 * plane.turning_radius(plane.speed_takeoff(), 3.349))
    distance = 1296000

    times = [0]
    altis = [0]
    dist = 0
    dt = 0.2

    v_takeoff_to_pattern = plane.speed_takeoff()
    h_pattern = 304
    drag_takeoff_to_pattern = plane.drag(plane.Cd(plane.Cd_i(plane.Cl(v_takeoff_to_pattern))), v_takeoff_to_pattern)
    roc_takeoff_to_pattern = plane.rate_of_climb(drag_takeoff_to_pattern, v_takeoff_to_pattern)

    vels = [v_takeoff_to_pattern]
    drags = [drag_takeoff_to_pattern]
    weights = [plane.W_fuel]

    while altis[-1] < h_pattern:
        times.append(times[-1] + dt)
        altis.append(altis[-1] + roc_takeoff_to_pattern*dt)
        vels.append(v_takeoff_to_pattern)
        dist += v_takeoff_to_pattern * dt
        drags.append(drag_takeoff_to_pattern)
        plane.W_fuel -= plane.cj * drag_takeoff_to_pattern * dt
        weights.append(plane.W_fuel)

        plane.set_altitude(altis[-1])
        drag_takeoff_to_pattern = plane.drag(plane.Cd(plane.Cd_i(plane.Cl(v_takeoff_to_pattern))), v_takeoff_to_pattern)
        roc_takeoff_to_pattern = plane.rate_of_climb(drag_takeoff_to_pattern, v_takeoff_to_pattern)


    while dist < pattern_d_to:
        times.append(times[-1] + dt)
        altis.append(altis[-1])
        vels.append(v_takeoff_to_pattern)
        dist += v_takeoff_to_pattern * dt
        drags.append(drag_takeoff_to_pattern)
        plane.W_fuel -= plane.cj * drag_takeoff_to_pattern * dt
        weights.append(plane.W_fuel)

    v_pattern_to_cruise = plane.speed_PRmin()
    h_cruise = 12500
    drag_pattern_to_cruise = plane.drag(plane.Cd(plane.Cd_i(plane.Cl(v_pattern_to_cruise))), v_pattern_to_cruise)
    roc_pattern_to_cruise = 17.5229

    while altis[-1] < h_cruise:
        times.append(times[-1] + dt)
        altis.append(altis[-1] + roc_pattern_to_cruise * dt)
        vels.append(v_pattern_to_cruise)
        dist += v_pattern_to_cruise * dt
        drags.append(drag_pattern_to_cruise)
        plane.W_fuel -= plane.cj * drag_pattern_to_cruise * dt
        weights.append(plane.W_fuel)

        plane.set_altitude(altis[-1])
        v_pattern_to_cruise = plane.speed_PRmin()
        drag_pattern_to_cruise = plane.drag(plane.Cd(plane.Cd_i(plane.Cl(v_pattern_to_cruise))), v_pattern_to_cruise)

    v_cruise = 220
    Cl = plane.Cl(v_cruise)
    drag_cruise = plane.drag(plane.Cd(plane.Cd_i(Cl), plane.Cd_c(Cl, v_cruise, True)), v_cruise)
    while dist < distance - 140210:
        times.append(times[-1] + dt)
        altis.append(altis[-1])
        vels.append(v_cruise)
        dist += v_cruise * dt
        drags.append(drag_cruise)
        plane.W_fuel -= plane.cj * drag_cruise * dt
        weights.append(plane.W_fuel)

        Cl = plane.Cl(v_cruise)
        drag_cruise = plane.drag(plane.Cd(plane.Cd_i(Cl), plane.Cd_c(Cl, v_cruise, True)), v_cruise)

    time_cruise_to_pattern = 20 * 60
    ros_cruise_to_pattern = (h_pattern - h_cruise) / time_cruise_to_pattern
    v_pattern_to_landing = plane.speed_landing()
    ros_const_accel = (v_cruise - v_pattern_to_landing) / time_cruise_to_pattern

    v_cruise_to_pattern = v_cruise
    drag_cruise_to_pattern = plane.drag(plane.Cd(plane.Cd_i(plane.Cl(v_cruise_to_pattern))), v_cruise_to_pattern)
    ros_pow_discrep = ros_cruise_to_pattern * plane.W_0
    ros_pow_avail = ros_pow_discrep + plane.pow_required(drag_cruise_to_pattern, v_cruise_to_pattern)
    ros_thrust = ros_pow_avail / v_cruise_to_pattern

    while altis[-1] > h_pattern:
        times.append(times[-1] + dt)
        altis.append(altis[-1] + ros_cruise_to_pattern * dt)
        vels.append(v_cruise_to_pattern)
        dist += v_cruise_to_pattern * dt
        drags.append(drag_cruise_to_pattern)
        plane.W_fuel -= plane.cj * ros_thrust * dt
        weights.append(plane.W_fuel)

        plane.set_altitude(altis[-1])
        v_cruise_to_pattern -= ros_const_accel * dt
        ros_pow_discrep = ros_cruise_to_pattern * plane.W_0
        drag_cruise_to_pattern = plane.drag(plane.Cd(plane.Cd_i(plane.Cl(v_cruise_to_pattern))), v_cruise_to_pattern)
        ros_pow_avail = ros_pow_discrep + plane.pow_required(drag_cruise_to_pattern, v_cruise_to_pattern)
        ros_thrust = max(0, ros_pow_avail / v_cruise_to_pattern)
        if ros_thrust == 0:
            ros_const_accel = 0
        else:
            ros_const_accel = (v_cruise - v_pattern_to_landing) / time_cruise_to_pattern

    drag_pattern_to_landing = plane.drag(plane.Cd(plane.Cd_i(plane.Cl(v_pattern_to_landing))), v_pattern_to_landing)

    da = dist
    while dist - da < pattern_d_lo:
        times.append(times[-1] + dt)
        altis.append(altis[-1])
        vels.append(v_pattern_to_landing)
        dist += v_pattern_to_landing * dt
        drags.append(drag_pattern_to_landing)
        plane.W_fuel -= plane.cj * drag_pattern_to_landing * dt
        weights.append(plane.W_fuel)

    while altis[-1] > 0:
        times.append(times[-1] + dt)
        altis.append(altis[-1] + -11 * dt)
        vels.append(v_pattern_to_landing)
        dist += v_pattern_to_landing * dt
        drags.append(drag_pattern_to_landing)
        weights.append(plane.W_fuel)


    print('\tFlight Time:\t\t\t{} hours'.format(times[-1] / 60 / 60))

    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('Time [minutes]')
    ax1.set_ylabel('Altitude [m]', color=color)
    ax1.plot(np.array(times) / 60, altis, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Velocity [m/s]', color=color)
    ax2.plot(np.array(times) / 60, vels, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    ax1.set_title('Flight Plan (Altitude and Velocity vs Time)')
    fig.tight_layout()
    plt.show()
    plt.clf()
    plt.plot(np.array(times) / 60, altis)
    plt.title('Flight Plan (Altitude vs Time)')
    plt.xlabel('Time [minutes]')
    plt.ylabel('Altitude [m]')
    plt.show()
    plt.clf()
    plt.plot(np.array(times) / 60, np.array(weights) / 1000)
    plt.title('Flight Plan (Fuel Weight vs Time)')
    plt.xlabel('Time [minutes]')
    plt.ylabel('Fuel Weight [kN]')
    plt.show()
    plt.clf()
    plt.plot(np.array(times) / 60, vels)
    plt.title('Flight Plan (Velocity vs Time)')
    plt.xlabel('Time [minutes]')
    plt.ylabel('Velocity [m/s]')
    plt.show()

