"""
Tests for the AbstractPropulsiveComponent base class.

This module tests the functionality of the AbstractPropulsiveComponent including FlightPoint
field expansion, compute_single_point_forward() and compute_single_point_backward() methods,
and VariableList updates.
"""

import pytest
from fastoad.model_base.flight_point import FlightPoint, _FieldDescriptor
from fastoad.openmdao.variables import Variable, VariableList

from rta.models.propulsion.tests.dummy_components.propeller import (
    PropellerComponent,
)


def test_flight_point_fields_expanded_at_instantiation():
    """Test that FlightPoint fields are expanded when component is instantiated."""
    # Before instantiation, check that the output field doesn't exist
    # We use a fresh FlightPoint to verify the field is added
    _ = PropellerComponent()

    # After instantiation, the output field should be available on FlightPoint
    fp = FlightPoint()
    assert hasattr(fp, "gearbox_shaft_power"), (
        "FlightPoint should have gearbox_shaft_power attribute after component instantiation"
    )
    assert fp.is_cumulative("gearbox_shaft_power"), (
        'The added field should have metadata "is_cumulative"=True'
    )

    # Now lets try to redefine at instantiation

    # test the input / output fields can be modified at instantiation
    new_input_fields = {"overdrive_power": _FieldDescriptor(unit="GW", is_cumulative=False)}
    new_output_fields = {"overdrive_waste_heat": _FieldDescriptor(unit="PW", is_cumulative=True)}

    prop = PropellerComponent(input_fields=new_input_fields, output_fields=new_output_fields)

    fp = FlightPoint()

    assert "overdrive_power" in prop.input_fields, (
        "The instance has not been initialised with 'new_input_fields'."
    )
    assert "thrust" not in prop.input_fields, (
        "The instance has been initialised with 'new_input_fields',"
        " but the default ones are still present."
    )

    assert hasattr(fp, "overdrive_waste_heat"), (
        "FlightPoint should have 'overdrive_waste_heat' attribute after component instantiation."
    )
    assert fp.is_cumulative("overdrive_waste_heat"), (
        'The added field should have metadata "is_cumulative"=True'
    )


def test_flight_point_expansion_only_once():
    """Test that FlightPoint fields are only added once (not duplicated)."""
    # Create first component - should add fields without warning
    _ = PropellerComponent()

    # Create second component of same type - should trigger warning for redundant field
    with pytest.warns(UserWarning) as record:
        _ = PropellerComponent()

    # Verify that a warning was issued about redundant declarations
    assert len(record) == 1
    assert "redundant declarations" in str(record[0].message)
    assert "gearbox_shaft_power" in str(record[0].message)


def test_compute_single_point_backward():
    """Test compute_single_point_backward() with a single FlightPoint."""
    component = PropellerComponent()

    fp = FlightPoint()
    fp.thrust = 50000.0  # N
    fp.true_airspeed = 200.0  # m/s
    component.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85

    component.compute_single_point_backward(fp)

    # Expected: (50000 * 200) / 0.85 = 11764705.88...
    expected_power = (50000.0 * 200.0) / 0.85
    assert fp.gearbox_shaft_power == pytest.approx(expected_power, rel=1e-6)


def test_compute_single_point_forward():
    """Test compute_single_point_forward() with a single FlightPoint."""
    component = PropellerComponent()

    fp = FlightPoint()
    fp.gearbox_shaft_power = 11764705.88  # W
    fp.true_airspeed = 200.0  # m/s
    component.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85

    component.compute_single_point_forward(fp)

    # Expected: (50000 * 200) / 0.85 = 11764705.88 * 0.85 / 200 = 50000
    expected_thrust = 11764705.88 * 0.85 / 200
    assert fp.thrust == pytest.approx(expected_thrust, rel=1e-6)


def test_inputs_can_be_updated_using_update():
    """Test that inputs can be updated using VariableList.update()."""
    component = PropellerComponent()

    # Create new input variables to add
    new_inputs = VariableList()
    new_inputs.append(Variable("data:propulsion:propeller:efficiency", units="unitless", val=0.5))

    # Update inputs
    component.input_parameters.update(new_inputs)

    # Verify
    assert component.input_parameters["data:propulsion:propeller:efficiency"].get_val() == 0.5


def test_inputs_units_incorrect():
    """Test  _check_input_unit function"""

    new_input_fields = {
        "thrust": _FieldDescriptor(unit="kN"),
        "true_airspeed": _FieldDescriptor(unit="m/s"),
    }
    propeller = PropellerComponent(input_fields=new_input_fields)

    with pytest.raises(ValueError) as record:
        propeller._check_input_fields()

    assert (
        "Component 'PropellerPowerCalculator': The following input fields:"
        " thrust asked for the following units : kN" in str(record.value)
    )
