import numpy as np
import openmdao.api as om
from fastoad.testing import run_system

from rta.models.propulsion.tests.dummy_components.propulsion_system_omwrapper import (
    PropulsionSystemOMComponent,
)

#  This file is part of FAST-OAD : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2026 ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.


def test_PropulsionSystemOMComponent():
    """Tests PropulsionSystemOMComponent component"""

    engine = PropulsionSystemOMComponent()

    true_airspeed = [15, 30, 60, 90, 120]
    thrusts = [10e3, 7.5e3, 5e3, 2.5e3, 1.0e3]

    propeller_efficiency = 0.85
    gearbox_efficiency = 0.95
    engine_count = 2.0
    psfc = 0.250 / (1000.0 * 3600.0)

    ivc = om.IndepVarComp()
    ivc.add_output("data:propulsion:gearbox:efficiency", gearbox_efficiency)
    ivc.add_output("data:propulsion:propeller:efficiency", propeller_efficiency)
    ivc.add_output("data:propulsion:engine_count", val=engine_count)

    ivc.add_output("data:propulsion:true_airspeed", true_airspeed, units="m/s")
    ivc.add_output("data:propulsion:thrust", thrusts, units="N")

    problem = run_system(engine, ivc)

    # The thrust is distributed equally between each engine
    # Propulsive components don't see the total amount of thrust or power or whatever
    propulsive_power_per_engine = [
        speed * thrust / engine_count for speed, thrust in zip(true_airspeed, thrusts)
    ]
    expected_gearbox_power = [
        prop_power / propeller_efficiency for prop_power in propulsive_power_per_engine
    ]
    expected_TPpower = [
        prop_power / propeller_efficiency / gearbox_efficiency
        for prop_power in propulsive_power_per_engine
    ]
    expected_sfc = [
        TPpower * psfc / (thrust / engine_count)
        for TPpower, thrust in zip(expected_TPpower, thrusts)
    ]

    sfc = problem.get_val("data:propulsion:sfc", units="kg/s/N")
    gear_shaft_power = problem.get_val("data:propulsion:gearbox_shaft_power", units="W")
    tp_shaft_power = problem.get_val("data:propulsion:TPshaft_power", units="W")

    np.testing.assert_allclose(sfc, expected_sfc, rtol=1e-4)
    np.testing.assert_allclose(gear_shaft_power, expected_gearbox_power, rtol=1e-4)
    np.testing.assert_allclose(tp_shaft_power, expected_TPpower, rtol=1e-4)
