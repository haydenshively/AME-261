import json

from haydens_code.plane import Plane
from haydens_code.atmosphere import std_atm_earth
from engines import engine_db

def _load(path, atmosphere=std_atm_earth()):
    data = {}
    with open(path) as f:
        data = json.load(f)

    engine = data.get('engine', {})
    engine_name = engine.get('name', None)
    # If name is specified, look for it in the engine database
    # Then fall-back on database values if they're not given in the plane.json file
    engine_in_db = engine_db.get(engine_name, {}) if engine_name is not None else {}

    T_a_sl = engine.get('thrust', engine_in_db.get('thrust', None))
    cost_engines = engine.get('cost', engine_in_db.get('cost', None))
    engine_count = data.get('engine_count', 1)
    if T_a_sl is not None: T_a_sl *= engine_count
    if cost_engines is not None: cost_engines *= engine_count

    weight = data.get('weight', {'struct': 0, 'fuel': 0, 'payload': 0})
    W_struct = weight.get('struct', 0)
    W_fuel = weight.get('fuel', 0)
    W_payload = weight.get('payload', 0)
    W_engines = engine.get('weight', engine_in_db.get('weight', 0)) * engine_count
    cost_struct = data.get('cost', None)
    if (cost_struct is not None) and (cost_engines is not None): cost_struct -= cost_engines

    plane = Plane(
        data.get('Cd_0', None),
        data.get('e_w', None),
        data.get('S', None),
        data.get('b', None),
        data.get('Cl_max', None),
        data.get('Lam', None),
        data.get('tc_max', None),
        W_struct,
        W_fuel,
        W_engines,
        W_payload,
        engine.get('cj', engine_in_db.get('cj', None)),
        T_a_sl,
        data.get('n_struct', None),
        atmosphere,
    )
    plane._description = data.get('description', None)

    plane._cost_engines = cost_engines
    plane._cost_struct = cost_struct
    return plane
