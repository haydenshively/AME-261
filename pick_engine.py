def max_payload(plane, speed):
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
    return plane.W_payload


if __name__ == '__main__':
    import sys
    import json
    from copy import copy
    import numpy as np
    from hangar import planes
    from engines import engine_db

    requirements = {}
    with open('requirements.json') as f:
        requirements = json.load(f)
        print('Mission Requirements:')
        print(json.dumps(requirements, indent=2))
        print('')
    occupant = requirements['occupant']
    occupant_count = requirements['occupant_count']
    required_payload = occupant_count * (occupant['weight'] + occupant['baggage_weight'])
    required_range = requirements['range']
    required_V_approach = requirements['landing']['approach_speed']
    required_d_runway = requirements['runway_length']

    priorities = {}
    with open('priorities.json') as f:
        priorities = json.load(f)
        print('Design Priorities:')
        print(json.dumps(priorities, indent=2))
        print('')
    priorities = np.array([
        -priorities['minimize_cost'],
        +priorities['maximize_V_cruise'],
        +priorities['maximize_payload'],
        +priorities['maximize_range'],
        -priorities['minimize_runway_length'],
        -priorities['minimize_pattern_radius'],
        +priorities['maximize_efficiency']
    ])

    if len(sys.argv) > 1:
        planes = {sys.argv[1]: planes[sys.argv[1]]}
    # Create a giant list of each plane in hangar, matched up with engine in
    # engines.csv. The number of engines will be varied from 1 to 5. This
    # means there will be (num_planes*num_engines*5) potential combinations
    for plane_name, plane in planes.items():
        results = []
        result_names = []
        result_reqs_met = []
        for eng_name, engine in engine_db.items():
            for i in range(1, 6):
                experiment = copy(plane)
                experiment.T_a_sl = i * engine['thrust']
                experiment.W_engines = i * engine['weight']
                experiment.cj = engine['cj']/60/60# convert to seconds
                experiment._cost_engines = i * engine['cost']

                cost = experiment._cost_engines + experiment._cost_struct

                # assume we're cruising at 10km
                # also assume that the Carson speed is within our V profile
                experiment.set_altitude(14000)
                V_cruise = experiment.speed_carson()
                # solve for max payload, and run the rest of the
                # calculations assuming the plane is 100% full
                payload = max_payload(experiment, V_cruise)
                if payload > required_payload:
                    experiment.W_payload = required_payload

                d_range = experiment.max_range_const_speed(V_cruise)
                # assume that...
                # our airport is at sea level
                # no flaps/slats are used during takeoff
                # wings are 4m off the ground
                # rolling coefficient is 0.02
                # these assumptions aren't terribly important since
                # we're just worried about maximizing things
                experiment.set_altitude(0)
                d_takeoff = experiment.d_takeoff(0.02, 4)
                # assume that Cl_max increases by 50% because of
                # flaps/slats during landing
                experiment.Cl_max *= 1.5
                # make sure all computations use the appropriate weight
                experiment.W_fuel = 0
                V_approach = experiment.speed_landing()
                # ignore n_struct, since we don't know it
                n_cl_max = experiment.n_cl_max(V_approach)
                n_thrust = experiment.n_thrust(V_approach)
                n = min(n_cl_max, n_thrust)
                if n**2 - 1 <= 0:
                    r_pattern = 0
                else:
                    r_pattern = experiment.turning_radius(V_approach, n)
                # assume we can deliver 30% reverse thrust
                d_landing = experiment.d_landing(0.02, 4, 0.30)
                """
                NOW WE HAVE RESULTS:
                cost
                V_cruise
                payload
                range
                d_takeoff
                d_landing
                r_pattern
                """
                d_runway = max(d_takeoff, d_landing)
                # Ensure the plane meets the requirements
                reqs_met = [
                    payload > required_payload,
                    d_range > required_range,
                    d_runway < required_d_runway,
                    V_approach < required_V_approach
                ]
                # Uncomment this line to keep engine in the race even though it doesn't meet requirements
                if sum(reqs_met) < len(reqs_met): continue
                result_reqs_met.append(reqs_met)
                # Save results to judge based on priorities later on
                results.append([
                    cost,
                    V_cruise,
                    payload,
                    d_range,
                    d_runway,
                    r_pattern,
                    1.0/experiment.cj,
                ])
                result_names.append(plane_name + '_' + eng_name + '_{}'.format(i))

        if len(results) > 0:
            # convert to numpy and make everything dimensionless
            results_np = np.array(results)
            results_np /= results_np.max(axis=0)
            # put avg value at 0
            results_np -= results_np.mean(axis=0)
            # judge each plane based on priorities
            scores = (results_np * priorities).sum(axis=1)
            winner = scores.argmax()

            print('Finished testing ' + plane_name + ':')
            print('  There are {} combinations that meet requirements'.format(len(results)))
            # print top 5 engine combinations
            print('  These are the best engine combinations:')
            for i in range(5):
                winner = scores.argmax()
                scores[winner] = scores.min()
                winner_name = result_names[winner][len(plane_name)+1:]
                engine_count = winner_name[-1]
                winner_name = winner_name[:-2]
                print('    [{}] '.format(i+1) + engine_count + ' x ' + winner_name)
                print('      Plane Cost: {}'.format(results[winner][0]))
                print('      Sufficient Payload: {}'.format(result_reqs_met[winner][0]))
                print('      Sufficient Range: {}'.format(result_reqs_met[winner][1]))
                print('      Satisfactory Runway: {}'.format(result_reqs_met[winner][2]))
                print('      Satisfactory Approach: {}'.format(result_reqs_met[winner][3]))

            if len(sys.argv) > 2 and sys.argv[2] == 'a':
                print('  These are all possible engine combinations:')
                for i in range(len(results)):
                    config_name = result_names[i][len(plane_name) + 1:]
                    engine_count = config_name[-1]
                    config_name = config_name[:-2]
                    print('    [{}] '.format(i + 1) + engine_count + ' x ' + config_name)
                    print('      Plane Cost: {}'.format(results[i][0]))
                    print('      Sufficient Payload: {}'.format(result_reqs_met[i][0]))
                    print('      Sufficient Range: {}'.format(result_reqs_met[i][1]))
                    print('      Satisfactory Runway: {}'.format(result_reqs_met[i][2]))
                    print('      Satisfactory Approach: {}'.format(result_reqs_met[i][3]))
        else:
            print(plane_name + ' cannot meet requirements, regardless of engine')
        print('')
