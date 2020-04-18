# Optimization and Testing
### What does this code do?
This code has two main capabilities. (1) It allows you to test whether a given
plane meets the mission criteria listed in the Project Requirements document. (2)
Given a set of criteria and a plane with basic characteristics, it will optimize
the remaining characteristics.

#### Which mission requirements does it test for?
(subject to change and improve)
* Sufficient Payload Capacity
* Sufficient Range at V_cruise=Mach 0.8

#### How will the optimization work?
A set of planes will be placed in the hangar folder. These planes will be like
parents to a population of planes. Each generation will be tested against the
mission requirements. The subset of planes that meet the requirements will then
be judged based on criteria that we define. For example, maybe we are willing
to add a little bit of cost in order to increase our range. The weights that
define our priorities go in that criteria.json file. Based on the criteria, each
plane is given a score. The top N planes then get to "reproduce" - they have baby
planes with slightly different characteristics and different engines (engines come
from the database). The $ price of the baby planes is estimated based on AVG cost
per Newton of structure in other planes. The planes are then judged, just like their
parents. This process repeats until we stop seeing improvements in the criteria
that we set.

### Assumptions
* Assume that V_cruise is V_Carson (see page 521 in Anderson)
* Range is computed using formulas for constant velocity (V_cruise)
* If W_payload isn't defined in plane.json, it will be increased until thrust can no longer overcome drag
* For approach and landing, we assume that flaps & slats can increase Cl_max by 50%
* For all planes, we assume that wings are 4m off the ground for ground effect
* For all planes, we assume that reversible thrust is 30% of total available thrust
* When landing, we assume that the coefficient of rolling friction is twice the nominal value (account for braking)


### What if I just want to test against mission requirements?
* Place your plane file in the hangar
* Run test_all_planes.py

### How can I set up my computer to run Python?
* Download and install [Anaconda]
* Open Terminal on Mac (maybe cmd on Windows. I'm not sure)
* `conda install numpy matplotlib`
* `cd <path-to-AME261-code-folder>/Python/`
* `python test_all_planes.py`


[Anaconda]: https://www.anaconda.com/