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


    if len(sys.argv) > 1:
        planes = {sys.argv[1]: planes[sys.argv[1]]}
    # Create a giant list of each plane in hangar, matched up with engine in
    # engines.csv. The number of engines will be varied from 1 to 5. This
    # means there will be (num_planes*num_engines*5) potential combinations
    for plane_name, plane in planes.items():

        x = np.linspace(500, 1200, 1400)
        y = np.linspace(40, 70, 60)
        xv, yv = np.meshgrid(x, y)

        results = np.zeros((y.shape[0], x.shape[0], 4))
        for i in range(x.shape[0]):
            for j in range(y.shape[0]):
                experiment = copy(plane)
                experiment.S = x[i]
                experiment.b = y[j]
                experiment.W_payload = required_payload

                h = 0
                experiment.set_altitude(h)
                V_cruise = experiment.speed_carson()
                roc = plane.rate_of_climb(plane.drag(plane.Cd(plane.Cd_i(plane.Cl(V_cruise))), V_cruise), V_cruise)
                while roc > 0:
                    h += 500
                    experiment.set_altitude(h)
                    V_cruise = experiment.speed_carson()
                    roc = plane.rate_of_climb(plane.drag(plane.Cd(plane.Cd_i(plane.Cl(V_cruise))), V_cruise), V_cruise)

                # solve for max payload, and run the rest of the
                # calculations assuming the plane is 100% full
                # payload = max_payload(experiment, V_cruise)
                # if payload > required_payload:
                #     experiment.W_payload = required_payload

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

                # Save results to judge based on priorities later on
                results[j, i] = np.array([
                    V_cruise,
                    d_range,
                    d_runway,
                    r_pattern,
                ])


        print(results.shape)

        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        print(xv.shape)
        print(yv.shape)
        print(results.shape)

        ax.set_xlabel('Surface Area [m^2]')
        ax.set_ylabel('Span [m]')
        ax.set_zlabel('Range [km]')

        ax.plot_wireframe(X=xv, Y=yv, Z=results[:,:,1]/1000)
        plt.show()
        # if len(results) > 0:
        #     # convert to numpy and make everything dimensionless
        #     results_np = np.array(results)
        #     results_np /= results_np.max(axis=0)
        #     # put avg value at 0
        #     results_np -= results_np.mean(axis=0)
        #     # judge each plane based on priorities
        #     scores = (results_np * priorities).sum(axis=1)
        #     winner = scores.argmax()
        #
        #     print('Finished testing ' + plane_name + ':')
        #     print('  There are {} combinations that meet requirements'.format(len(results)))
        #     # print top 5 engine combinations
        #     print('  These are the best engine combinations:')
        #     for i in range(5):
        #         winner = scores.argmax()
        #         scores[winner] = scores.min()
        #         winner_name = result_names[winner][len(plane_name)+1:]
        #         engine_count = winner_name[-1]
        #         winner_name = winner_name[:-2]
        #         print('    [{}] '.format(i+1) + engine_count + ' x ' + winner_name)
        #         print('      Plane Cost: {}'.format(results[winner][0]))
        #         print('      Sufficient Payload: {}'.format(result_reqs_met[winner][0]))
        #         print('      Sufficient Range: {}'.format(result_reqs_met[winner][1]))
        #         print('      Satisfactory Runway: {}'.format(result_reqs_met[winner][2]))
        #         print('      Satisfactory Approach: {}'.format(result_reqs_met[winner][3]))
        #
        #     if len(sys.argv) > 2 and sys.argv[2] == 'a':
        #         print('  These are all possible engine combinations:')
        #         for i in range(len(results)):
        #             config_name = result_names[i][len(plane_name) + 1:]
        #             engine_count = config_name[-1]
        #             config_name = config_name[:-2]
        #             print('    [{}] '.format(i + 1) + engine_count + ' x ' + config_name)
        #             print('      Plane Cost: {}'.format(results[i][0]))
        #             print('      Sufficient Payload: {}'.format(result_reqs_met[i][0]))
        #             print('      Sufficient Range: {}'.format(result_reqs_met[i][1]))
        #             print('      Satisfactory Runway: {}'.format(result_reqs_met[i][2]))
        #             print('      Satisfactory Approach: {}'.format(result_reqs_met[i][3]))
        # else:
        #     print(plane_name + ' cannot meet requirements, regardless of engine')
        # print('')
