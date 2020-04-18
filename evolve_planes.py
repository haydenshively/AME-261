if __name__ == '__main__':
    from copy import copy
    from hangar import planes, cost_per_newton_struct
    from engines import engine_db

    # Initial population will consist of each plane in hangar, matched up with
    # each engine in engines.csv. The number of engines will be varied from 1
    # to 6. This means there will be (num_planes*num_engines*6) planes in the
    # initial population.
    population = {}
    for plane_name, plane in planes.items():
        for eng_name, engine in engine_db.items():
            for i in range(1, 6):
                plane.T_a_sl = i * engine['thrust']
                plane._W_engines = i * engine['weight']
                plane.cj = engine['cj']
                plane._cost_engines = i * engine['cost']
                population[plane_name + '_' + eng_name + '_{}'.format(i)] = copy(plane)



    import json
    requirements = {}
    with open('priorities.json') as f:
        requirements = json.load(f)

    vary_AR = True, (3, 16)
    vary_Lam = True, (10, 45)



    generations = 10
    for i in range(generations):
        results = {}
        for name, plane in population.items():

