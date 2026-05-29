"""
Tests for the PropulsionSystemModule.

This module tests the functionality of the PropulsionSystemModule including
the complete propulsion chain: propeller -> gearbox -> fuel flow -> SFC.
"""
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

import numpy as np
import pandas as pd
import pytest
from fastoad.model_base.flight_point import FlightPoint, _FieldDescriptor

from rta.models.propulsion.tests.dummy_components.gearbox import GearboxComponent
from rta.models.propulsion.tests.dummy_components.propeller import (
    PropellerComponent,
)
from rta.models.propulsion.tests.dummy_components.propulsion_system_module import (
    PropulsionSystemModule,
)


def test_incoherent_input_definition():
    new_input_fields = {
        "thrust": _FieldDescriptor(unit="kN"),
        "true_airspeed": _FieldDescriptor(unit="m/s"),
    }
    propeller = PropellerComponent(input_fields=new_input_fields)
    gearbox = GearboxComponent()

    with pytest.raises(ValueError) as record:
        _ = PropulsionSystemModule(
            propeller=propeller,
            gearbox=gearbox,
        )

    assert (
        "Component 'PropellerPowerCalculator': The following input fields:"
        " thrust asked for the following units : kN" in str(record.value)
    )


def test_propulsion_system_module_compute_single_flight_point():
    """Test compute_flight_points() with a single FlightPoint."""
    propeller = PropellerComponent()
    gearbox = GearboxComponent()

    # Set propeller efficiency to 0.85
    propeller.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85
    # Set gearbox efficiency to 0.95
    gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.95

    module = PropulsionSystemModule(
        propeller=propeller,
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
    propeller = PropellerComponent()
    gearbox = GearboxComponent()

    # Set propeller efficiency to 0.85
    propeller.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85
    # Set gearbox efficiency to 0.90
    gearbox.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.90

    module = PropulsionSystemModule(
        propeller=propeller,
        gearbox=gearbox,
    )

    fp1 = FlightPoint()
    fp1.thrust = 50000.0  # N
    fp1.true_airspeed = 200.0  # m/s

    fp2 = FlightPoint()
    fp2.thrust = 60000.0  # N
    fp2.true_airspeed = 250.0  # m/s

    flight_points = pd.DataFrame([fp1, fp2])
    module.compute_flight_points(flight_points)

    # First flight point
    expected_gearbox_shaft_power1 = (50000.0 * 200.0) / 0.85
    expected_tpshaft_power1 = expected_gearbox_shaft_power1 / 0.90

    # Fuel flow
    psfc_kg_per_w_s = 0.250 / (1000.0 * 3600.0)
    expected_fuel_flow1 = psfc_kg_per_w_s * expected_tpshaft_power1
    # SFC
    expected_sfc1 = expected_fuel_flow1 / 50000.0

    # Second flight point
    expected_gearbox_shaft_power2 = (60000.0 * 250.0) / 0.85
    expected_tpshaft_power2 = expected_gearbox_shaft_power2 / 0.90

    # Fuel flow
    expected_fuel_flow2 = psfc_kg_per_w_s * expected_tpshaft_power2
    # SFC
    expected_sfc2 = expected_fuel_flow2 / 60000.0

    expected_gearbox_shaft_power = [expected_gearbox_shaft_power1, expected_gearbox_shaft_power2]
    expected_tpshaft_power = [expected_tpshaft_power1, expected_tpshaft_power2]
    expected_sfc = [expected_sfc1, expected_sfc2]

    assert np.allclose(
        expected_gearbox_shaft_power, flight_points.gearbox_shaft_power.to_list(), rtol=1e-6
    )
    assert np.allclose(expected_tpshaft_power, flight_points.TPshaft_power.to_list(), rtol=1e-6)
    assert np.allclose(expected_sfc, flight_points.sfc.to_list(), rtol=1e-6)
