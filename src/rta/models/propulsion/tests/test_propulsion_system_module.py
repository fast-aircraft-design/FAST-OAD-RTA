"""
Tests for the PropulsionSystemModule.

This module tests the functionality of the PropulsionSystemModule including
the complete propulsion chain: propeller -> gearbox -> fuel flow -> SFC.
"""

#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2020  ONERA & ISAE-SUPAERO
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

import pytest

from fastoad.model_base.flight_point import FlightPoint

from rta.models.propulsion.tests.dummy_components.gearbox import GearboxComponent
from rta.models.propulsion.tests.dummy_components.propeller_power_calculator import (
    PropellerPowerCalculator,
)
from rta.models.propulsion.tests.dummy_components.propulsion_system_module import (
    PropulsionSystemModule,
)


def test_propulsion_system_module_compute_single_flight_point():
    """Test compute_flight_points() with a single FlightPoint."""
    propeller = PropellerPowerCalculator()
    gearbox = GearboxComponent()

    # Set propeller efficiency to 0.85
    propeller.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85
    # Set gearbox efficiency to 0.95
    gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.95

    module = PropulsionSystemModule(
        propeller_power_calculator=propeller,
        gearbox=gearbox,
    )

    fp = FlightPoint()
    fp.thrust = 50000.0  # N
    fp.true_airspeed = 200.0  # m/s

    module.compute_flight_points(fp)

    # Step 1: Propeller computes gearbox_shaft_power = (thrust * velocity) / efficiency
    # = (50000 * 200) / 0.85 = 11764705.88... W
    expected_gearbox_shaft_power = (50000.0 * 200.0) / 0.85

    # Step 2: Gearbox computes TPshaft_power = gearbox_shaft_power / efficiency
    # = 11764705.88 / 0.95 = 12383901.98... W
    expected_tpshaft_power = expected_gearbox_shaft_power / 0.95

    # Step 3: Fuel flow = PSFC * TPshaft_power
    # PSFC = 0.250 kg/kWh = 0.250 / (1000 * 3600) kg/W/s
    psfc_kg_per_w_s = 0.250 / (1000.0 * 3600.0)
    expected_fuel_flow = psfc_kg_per_w_s * expected_tpshaft_power

    # Step 4: SFC = fuel_flow / thrust
    expected_sfc = expected_fuel_flow / 50000.0

    assert fp.gearbox_shaft_power == pytest.approx(expected_gearbox_shaft_power, rel=1e-6)
    assert fp.TPshaft_power == pytest.approx(expected_tpshaft_power, rel=1e-6)
    assert fp.psfc == pytest.approx(psfc_kg_per_w_s, rel=1e-6)
    assert fp.sfc == pytest.approx(expected_sfc, rel=1e-6)


def test_propulsion_system_module_compute_list_of_flight_points():
    """Test compute_flight_points() with a list of FlightPoints."""
    propeller = PropellerPowerCalculator()
    gearbox = GearboxComponent()

    # Set propeller efficiency to 0.85
    propeller.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85
    # Set gearbox efficiency to 0.90
    gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.90

    module = PropulsionSystemModule(
        propeller_power_calculator=propeller,
        gearbox=gearbox,
    )

    fp1 = FlightPoint()
    fp1.thrust = 50000.0  # N
    fp1.true_airspeed = 200.0  # m/s

    fp2 = FlightPoint()
    fp2.thrust = 60000.0  # N
    fp2.true_airspeed = 250.0  # m/s

    module.compute_flight_points([fp1, fp2])

    # First flight point
    # Propeller: gearbox_shaft_power = (50000 * 200) / 0.85
    expected_gearbox_shaft_power1 = (50000.0 * 200.0) / 0.85
    # Gearbox: TPshaft_power = gearbox_shaft_power / 0.90
    expected_tpshaft_power1 = expected_gearbox_shaft_power1 / 0.90
    # Fuel flow
    psfc_kg_per_w_s = 0.250 / (1000.0 * 3600.0)
    expected_fuel_flow1 = psfc_kg_per_w_s * expected_tpshaft_power1
    # SFC
    expected_sfc1 = expected_fuel_flow1 / 50000.0

    assert fp1.gearbox_shaft_power == pytest.approx(expected_gearbox_shaft_power1, rel=1e-6)
    assert fp1.TPshaft_power == pytest.approx(expected_tpshaft_power1, rel=1e-6)
    assert fp1.sfc == pytest.approx(expected_sfc1, rel=1e-6)

    # Second flight point
    # Propeller: gearbox_shaft_power = (60000 * 250) / 0.85
    expected_gearbox_shaft_power2 = (60000.0 * 250.0) / 0.85
    # Gearbox: TPshaft_power = gearbox_shaft_power / 0.90
    expected_tpshaft_power2 = expected_gearbox_shaft_power2 / 0.90
    # Fuel flow
    expected_fuel_flow2 = psfc_kg_per_w_s * expected_tpshaft_power2
    # SFC
    expected_sfc2 = expected_fuel_flow2 / 60000.0

    assert fp2.gearbox_shaft_power == pytest.approx(expected_gearbox_shaft_power2, rel=1e-6)
    assert fp2.TPshaft_power == pytest.approx(expected_tpshaft_power2, rel=1e-6)
    assert fp2.sfc == pytest.approx(expected_sfc2, rel=1e-6)
