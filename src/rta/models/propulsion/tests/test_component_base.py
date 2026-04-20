"""
Tests for the AbstractPropulsiveComponent base class.

This module tests the functionality of the AbstractPropulsiveComponent
including FlightPoint field expansion, compute_perfo() method, and
VariableList updates.
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
from fastoad.openmdao.variables import VariableList, Variable

from rta.models.propulsion.tests.dummy_components.propeller_power_calculator import (
    PropellerPowerCalculator,
)


def test_flight_point_fields_expanded_at_instantiation():
    """Test that FlightPoint fields are expanded when component is instantiated."""
    # Before instantiation, check that the output field doesn't exist
    # We use a fresh FlightPoint to verify the field is added
    _ = PropellerPowerCalculator()

    # After instantiation, the output field should be available on FlightPoint
    fp = FlightPoint()
    assert hasattr(
        fp, "gearbox_shaft_power"
    ), "FlightPoint should have gearbox_shaft_power attribute after component instantiation"


def test_flight_point_expansion_only_once():
    """Test that FlightPoint fields are only added once (not duplicated)."""
    # Create first component - should add fields without warning
    _ = PropellerPowerCalculator()

    # Create second component of same type - should trigger warning for redundant field
    with pytest.warns(UserWarning) as record:
        _ = PropellerPowerCalculator()

    # Verify that a warning was issued about redundant declarations
    assert len(record) == 1
    assert "redondant declarations" in str(record[0].message)
    assert "gearbox_shaft_power" in str(record[0].message)


def test_compute_perfo_single_flight_point():
    """Test compute_perfo() with a single FlightPoint."""
    component = PropellerPowerCalculator()

    fp = FlightPoint()
    fp.thrust = 50000.0  # N
    fp.true_airspeed = 200.0  # m/s
    component.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85

    component.compute_perfo(fp)

    # Expected: (50000 * 200) / 0.85 = 11764705.88...
    expected_power = (50000.0 * 200.0) / 0.85
    assert fp.gearbox_shaft_power == pytest.approx(expected_power, rel=1e-6)


def test_compute_perfo_list_of_flight_points():
    """Test compute_perfo() with a list of FlightPoints."""
    component = PropellerPowerCalculator()

    component.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85

    fp1 = FlightPoint()
    fp1.thrust = 50000.0
    fp1.true_airspeed = 200.0

    fp2 = FlightPoint()
    fp2.thrust = 60000.0
    fp2.true_airspeed = 250.0

    flightpoints = [fp1, fp2]
    component.compute_perfo(flightpoints)

    # First result: (50000 * 200) / 0.85
    expected_power1 = (50000.0 * 200.0) / 0.85
    assert flightpoints[0].gearbox_shaft_power == pytest.approx(expected_power1, rel=1e-6)

    # Second result: (60000 * 250) / 0.90
    expected_power2 = (60000.0 * 250.0) / 0.85
    assert flightpoints[1].gearbox_shaft_power == pytest.approx(expected_power2, rel=1e-6)


def test_inputs_can_be_updated_using_update():
    """Test that inputs can be updated using VariableList.update()."""
    component = PropellerPowerCalculator()

    # Create new input variables to add
    new_inputs = VariableList()
    new_inputs.append(Variable("data:propulsion:propeller:efficiency", units="unitless", val=0.5))

    # Update inputs
    component.input_parameters.update(new_inputs)

    # Verify
    assert component.input_parameters["data:propulsion:propeller:efficiency"].get_val() == 0.5
