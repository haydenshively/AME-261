import os

from ._load import _load

planes = {}
sum_structural_cost = 0
sum_structural_weight = 0
for name in os.listdir('hangar'):
    if not name.endswith('.json'): continue
    path = os.path.join('hangar', name)
    plane = _load(path)
    if plane._cost_struct is not None:
        sum_structural_cost += plane._cost_struct
        sum_structural_weight += plane.W_struct
    planes[name[:-5]] = plane

cost_per_newton_struct = sum_structural_cost / sum_structural_weight
del sum_structural_cost
del sum_structural_weight

for plane_name, plane in planes.items():
    if plane._cost_struct is None:
        plane._cost_struct = plane.W_struct * cost_per_newton_struct
