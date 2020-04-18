def check_range(plane, speed, target):
    if plane.cj != None:
        r = plane.max_range_const_speed(speed)
        print('\tSufficient Range:\t\t{} ({} km)'.format(r > target, r // 1000))
    else:
        print('\tSufficient Range:\t\tUnknown - please define cj')


def check_payload(plane, speed, target):
    if plane.W_payload == 0:
        # this code will adjust W_0, W_1, and _max_payload if there's enough thrust to increase them
        # --> Tested with B-2 and got within 0.001% of actual payload value
        # V should end up around Mach 0.8
        Cl = plane.Cl(speed)
        Cd_c = plane.Cd_c(Cl, speed) if (plane.tc_max is not None) and (plane.Lam is not None) else 0
        drag = plane.drag(plane.Cd(plane.Cd_i(Cl), Cd_c), speed)
        T_a = plane.jet_thrust_available()
        while T_a > drag:
            plane.W_payload += 100
            Cl = plane.Cl(speed)
            Cd_c = plane.Cd_c(Cl, speed) if (plane.tc_max is not None) and (plane.Lam is not None) else 0
            drag = plane.drag(plane.Cd(plane.Cd_i(Cl), Cd_c), speed)
            T_a = plane.jet_thrust_available()

    print('\tSufficient Payload:\t\t{} ({} N)'.format(plane.W_payload > target, plane.W_payload))


def check_approach(plane, target):
    # Assume that flaps and slats can increase Cl_max by around 50%
    print('\tSatisfactory Approach Speed: \t{} ({} m/s)'.format(plane.speed_landing() < target, plane.speed_landing()//1.0))


def check_takeoff_d(plane, rolling_coeff, target):
    plane.set_altitude(0)
    # assume wing height = 4m off the ground
    return plane.d_takeoff(rolling_coeff, 4)

def check_landing_d(plane, rolling_coeff, target):
    plane.set_altitude(0)
    # assume wing height = 4m off the ground
    # assume reversible thrust is 30% of thrust available
    return plane.d_landing(rolling_coeff, 4, 0.30)

if __name__ == '__main__':
    import sys
    import json
    from copy import copy
    from hangar import planes

    data = {}
    with open('requirements.json') as f:
        data = json.load(f)

    # Parse Weight Requirements
    occupant = data.get('occupant', {})
    occupant_count = data.get('occupant_count', 0)
    W_payload = occupant_count * (occupant.get('weight', 0) + occupant.get('baggage_weight', 0))

    # Parse Range Requirements
    range = data.get('range', 0)

    # Parse Takeoff and Landing Requirements
    takeoff = data.get('takeoff', {})
    takeoff_obstacle = takeoff.get('obstacle', 0)
    takeoff_balanced = takeoff.get('balanced', False)
    approach_speed = data.get('landing', {}).get('approach_speed', None)

    # Parse Runway Requirements
    runway_length = data.get('runway_length', 0)
    runway_coeffs = data.get('runway_coeffs', {})

    if len(sys.argv) > 1:
        planes = {sys.argv[1]: planes[sys.argv[1]]}
    for name, plane in planes.items():
        print('\n' + name)
        plane.set_altitude(0)
        takeoffRoC = plane.rate_of_climb(plane.drag(plane.Cd(plane.Cd_i(plane.Cl(plane.speed_takeoff()))), plane.speed_takeoff()), plane.speed_takeoff())
        # for now, assume we're cruising at 10km
        plane.set_altitude(14000)
        V_cruise = plane.speed_carson()
        print('\tThrust Avail:\t\t\t{} N'.format(plane.T_a_sl//1.0))
        print('\tCruise Speed:\t\t\t{} m/s'.format(V_cruise//1.0))
        print('\tStall Speed:\t\t\t{} m/s'.format(plane.speed_stall()//1.0))
        print('\tRate of Climb:\t\t\t{} m/s'.format(takeoffRoC))
        # perform tests
        check_payload(plane, V_cruise, W_payload)
        if plane.W_payload > W_payload:
            plane.W_payload = W_payload
        check_range(plane, V_cruise, range)
        print('\tEngine Weight:\t\t\t{} N'.format(plane.W_engines))
        print('\tTakeoff Weight:\t\t\t{} N'.format(plane.W_0))

        for surface in runway_coeffs.keys():
            states = runway_coeffs[surface]
            for state in states.keys():
                coeff = states[state]
                d = check_takeoff_d(plane, coeff, runway_length)
                print('\tTakeoff, on {} {}:\t{} ({} m)'.format(state, surface, d < runway_length, d//1.0))

        plane.Cl_max = plane.Cl_max * 1.5
        print('\tTakeoff Speed:\t\t\t{} m/s'.format(plane.speed_takeoff()))
        check_approach(plane, approach_speed)
        for surface in runway_coeffs.keys():
            states = runway_coeffs[surface]
            for state in states.keys():
                coeff = states[state]
                # assume that breaks double the coefficient
                d = check_landing_d(plane, coeff*2, runway_length)
                print('\tLanding, on {} {}:\t{} ({} m)'.format(state, surface, d < runway_length, d//1.0))

        # TODO add in balanced field check
        # TODO add in takeoff obstacle check





