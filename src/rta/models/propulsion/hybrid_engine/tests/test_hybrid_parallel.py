import fastoad.api as oad
import pandas as pd
import pytest

from rta.models.propulsion.hybrid_engine.component_library.battery import BatteryComponent
from rta.models.propulsion.hybrid_engine.component_library.electric_motor import (
    ElectricMotorComponent,
)
from rta.models.propulsion.hybrid_engine.component_library.gas_turbine import GasTurbineComponent
from rta.models.propulsion.hybrid_engine.component_library.geabox_controller import (
    GearboxControllerComponent,
)
from rta.models.propulsion.hybrid_engine.component_library.gearbox import GearboxComponent
from rta.models.propulsion.hybrid_engine.component_library.inverter import InverterComponent
from rta.models.propulsion.hybrid_engine.component_library.propeller import (
    PropellerComponent,
)
from rta.models.propulsion.hybrid_engine.propulsion_systems.hybrid_parallel.hybrid_parallel_module import (  # noqa
    HybridParallelModule,
)


@pytest.fixture
def hybrid_parallel_module():
    propeller_component = PropellerComponent()
    gearbox_component = GearboxComponent()
    gearbox_controller_component = GearboxControllerComponent()
    gas_turbine_component = GasTurbineComponent()
    electric_motor_component = ElectricMotorComponent()
    inverter_component = InverterComponent()
    battery_component = BatteryComponent()

    # Initialize propeller input values
    propeller_component.input_parameters["data:propulsion:propeller:efficiency"].value = 0.85
    propeller_component.input_parameters["data:propulsion:propeller:rated_power"].value = 2240.0e3

    # Initialize gearbox input values
    gearbox_component.input_parameters["data:propulsion:gearbox:efficiency"].value = 0.95

    # Nothing is required for the gearbox controller due to its simplicity

    # Initialize gas turbine values
    gas_turbine_component.input_parameters["data:propulsion:gas_turbine:psfc"].value = (
        0.250 / 3600.0 / 1000.0
    )
    gas_turbine_component.input_parameters["data:propulsion:gas_turbine:rto_power"].value = 2000.0e3

    # Initialize electric motor values
    electric_motor_component.input_parameters[
        "data:propulsion:electric_motor:efficiency"
    ].value = 0.95
    electric_motor_component.input_parameters[
        "data:propulsion:electric_motor:rated_power"
    ].value = 500.0e3  # Doesn't matter if it is too high

    # Initialize inverter values
    inverter_component.input_parameters["data:propulsion:inverter:efficiency"].value = 0.95
    inverter_component.input_parameters[
        "data:propulsion:inverter:rated_power"
    ].value = 500.0e3  # Doesn't matter if it is too high

    # Initialize battery values
    battery_component.input_parameters["data:propulsion:battery:rated_energy"].value = 3e5
    battery_component.input_parameters["data:propulsion:battery:rated_power"].value = 1e6

    return HybridParallelModule(
        propeller=propeller_component,
        gearbox=gearbox_component,
        gearbox_controller=gearbox_controller_component,
        gas_turbine=gas_turbine_component,
        electric_motor=electric_motor_component,
        inverter=inverter_component,
        battery=battery_component,
    )


def test_propulsion_system_module_compute_single_flight_point_backward(hybrid_parallel_module):
    """Test compute_flight_points() with a single FlightPoint."""

    fp = oad.FlightPoint()
    fp.thrust = 7000.0  # N
    fp.true_airspeed = 140.0  # m/s
    fp.thrust_is_regulated = 1

    hybrid_parallel_module.compute_flight_points(fp)

    assert fp.propeller_shaft_power == pytest.approx(1152941.0, rel=1e-6)
    assert fp.thermal_shaft_power == pytest.approx(1092260.0, rel=1e-6)
    assert fp.psfc == pytest.approx(6.94444e-8, rel=1e-6)
    assert fp.sfc == pytest.approx(1.083591e-5, rel=1e-6)  # tsfc
    assert fp.thrust_rate == pytest.approx(
        0.4089111, rel=1e-6
    )  # Given how it has been computed, not really trustworthy

    assert fp.gas_turbine_power_rate == pytest.approx(0.546130, rel=1e-6)
    assert fp.battery_power_rate == pytest.approx(0.1344734, rel=1e-6)


def test_propulsion_system_module_compute_multiple_flight_point_backward(hybrid_parallel_module):
    """Test compute_flight_points() with a single FlightPoint."""

    fp1 = oad.FlightPoint()
    fp1.thrust = 7000.0  # N
    fp1.true_airspeed = 140.0  # m/s
    fp1.thrust_is_regulated = 1

    fp2 = oad.FlightPoint()
    fp2.thrust = 10000.0  # N
    fp2.true_airspeed = 155.0  # m/s
    fp2.thrust_is_regulated = 1

    flight_points = pd.DataFrame([fp1, fp2])

    hybrid_parallel_module.compute_flight_points(flight_points)

    assert flight_points.propeller_shaft_power.to_list() == pytest.approx(
        [1152941.0, 1823529.0], rel=1e-6
    )
    assert flight_points.thermal_shaft_power.to_list() == pytest.approx(
        [1092260.0, 1727554.0], rel=1e-6
    )
    assert flight_points.psfc.to_list() == pytest.approx([6.94444e-8, 6.94444e-8], rel=1e-6)
    assert flight_points.sfc.to_list() == pytest.approx([1.083591e-5, 1.199690e-5], rel=1e-6)

    assert flight_points.gas_turbine_power_rate.to_list() == pytest.approx(
        [0.546130, 0.863777], rel=1e-6
    )
    assert flight_points.battery_power_rate.to_list() == pytest.approx(
        [0.1344734, 0.2126874], rel=1e-6
    )


def test_propulsion_system_module_compute_single_flight_point_forward(hybrid_parallel_module):
    """Test compute_flight_points() with a single FlightPoint."""

    fp = oad.FlightPoint()
    fp.true_airspeed = 140.0  # m/s
    fp.thrust_is_regulated = 0
    fp.thrust_rate = 0.8

    hybrid_parallel_module.compute_flight_points(fp)

    assert fp.propeller_shaft_power == pytest.approx(2205900.0, rel=1e-6)
    assert fp.thermal_shaft_power == pytest.approx(1600000.0, rel=1e-6)
    assert fp.psfc == pytest.approx(6.94444e-8, rel=1e-6)
    assert fp.sfc == pytest.approx(8.296229e-6, rel=1e-6)  # tsfc
    assert fp.thrust == pytest.approx(13392.96, rel=1e-6)

    assert fp.gas_turbine_power_rate == pytest.approx(
        0.8, rel=1e-6
    )  # Specific to our "control strategy"
    assert fp.battery_power_rate == pytest.approx(0.8, rel=1e-6)


def test_propulsion_system_module_compute_multiple_flight_point_forward(hybrid_parallel_module):
    """Test compute_flight_points() with a single FlightPoint."""

    fp1 = oad.FlightPoint()
    fp1.true_airspeed = 140.0  # m/s
    fp1.thrust_is_regulated = 0
    fp1.thrust_rate = 0.8

    fp2 = oad.FlightPoint()
    fp2.true_airspeed = 155.0  # m/s
    fp2.thrust_is_regulated = 0
    fp2.thrust_rate = 0.85

    flight_points = pd.DataFrame([fp1, fp2])

    hybrid_parallel_module.compute_flight_points(flight_points)

    assert flight_points.propeller_shaft_power.to_list() == pytest.approx(
        [2205900.0, 2343768.75], rel=1e-6
    )
    assert flight_points.thermal_shaft_power.to_list() == pytest.approx(
        [1600000.0, 1700000.0], rel=1e-6
    )
    assert flight_points.psfc.to_list() == pytest.approx([6.94444e-8, 6.94444e-8], rel=1e-6)
    assert flight_points.sfc.to_list() == pytest.approx(
        [8.296229e-6, 9.185111e-6], rel=1e-6
    )  # tsfc
    assert flight_points.thrust.to_list() == pytest.approx([13392.96, 12852.92], rel=1e-6)

    assert flight_points.gas_turbine_power_rate.to_list() == pytest.approx(
        [0.8, 0.85], rel=1e-6
    )  # Specific to our "control strategy"
    assert flight_points.battery_power_rate.to_list() == pytest.approx([0.8, 0.85], rel=1e-6)


def test_propulsion_system_module_compute_multiple_flight_point_mix(hybrid_parallel_module):

    fp1 = oad.FlightPoint()
    fp1.thrust = 7000.0  # N
    fp1.true_airspeed = 140.0  # m/s
    fp1.thrust_is_regulated = 1

    fp2 = oad.FlightPoint()
    fp2.true_airspeed = 155.0  # m/s
    fp2.thrust_is_regulated = 0
    fp2.thrust_rate = 0.85

    flight_points = pd.DataFrame([fp1, fp2])

    hybrid_parallel_module.compute_flight_points(flight_points)

    assert flight_points.propeller_shaft_power.to_list() == pytest.approx(
        [1152941.0, 2343768.75], rel=1e-6
    )
    assert flight_points.thermal_shaft_power.to_list() == pytest.approx(
        [1092260.0, 1700000.0], rel=1e-6
    )
    assert flight_points.psfc.to_list() == pytest.approx([6.94444e-8, 6.94444e-8], rel=1e-6)
    assert flight_points.sfc.to_list() == pytest.approx(
        [1.083591e-5, 9.185111e-6], rel=1e-6
    )  # tsfc
    assert flight_points.thrust.to_list() == pytest.approx([7000.00, 12852.92], rel=1e-6)
    assert flight_points.thrust_rate.to_list() == pytest.approx([0.4089111, 0.85], rel=1e-6)

    assert flight_points.gas_turbine_power_rate.to_list() == pytest.approx(
        [0.546130, 0.85], rel=1e-6
    )  # Specific to our "control strategy"
    assert flight_points.battery_power_rate.to_list() == pytest.approx([0.1344734, 0.85], rel=1e-6)
