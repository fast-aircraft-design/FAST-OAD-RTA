"""
Placeholder hybrid parallel OpenMDAO wrapper.
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

import fastoad.api as oad
from fastoad.model_base.propulsion import FuelEngineSet
from openmdao.core.component import Component

from .hybrid_parallel_module import HybridParallelModule
from ...component_library.battery import BatteryComponent
from ...component_library.electric_motor import ElectricMotorComponent
from ...component_library.gas_turbine import GasTurbineComponent
from ...component_library.geabox_controller import GearboxControllerComponent
from ...component_library.gearbox import GearboxComponent
from ...component_library.inverter import InverterComponent
from ...component_library.propeller import PropellerComponent


@oad.RegisterPropulsion("rta.wrapper.propulsion.hybrid_parallel")
class HybridParallelOMWrapper(oad.IOMPropulsionWrapper):
    """
    Placeholder docstring
    """

    def setup(self, component: Component):
        """
        Placeholder docstring
        """
        # Declare default inputs from PropellerComponent
        propeller_component = PropellerComponent()
        propeller_component.declare_openmdao_inputs(component)

        # Declare inputs from GearboxComponent
        gearbox_component = GearboxComponent()
        gearbox_component.declare_openmdao_inputs(component)

        # Declare inputs from GearboxControllerComponent
        gearbox_controller_component = GearboxControllerComponent()
        gearbox_controller_component.declare_openmdao_inputs(component)

        # Declare inputs from GasTurbineComponent
        gas_turbine_component = GasTurbineComponent()
        gas_turbine_component.declare_openmdao_inputs(component)

        # Declare inputs from ElectricMotorComponent
        electric_motor_component = ElectricMotorComponent()
        electric_motor_component.declare_openmdao_inputs(component)

        # Declare inputs from InverterComponent
        inverter_component = InverterComponent()
        inverter_component.declare_openmdao_inputs(component)

        # Declare inputs from BatteryComponent
        battery_component = BatteryComponent()
        battery_component.declare_openmdao_inputs(component)

        component.add_input("data:geometry:propulsion:engine:count", 2, units="unitless")

    @staticmethod
    def get_model(inputs) -> FuelEngineSet:
        """
        Placeholder docstring
        """

        # Update inputs from the inputs vector
        propeller_component = PropellerComponent()
        propeller_component.update_input_parameters(inputs)

        gearbox_component = GearboxComponent()
        gearbox_component.update_input_parameters(inputs)

        gearbox_controller_component = GearboxControllerComponent()
        gearbox_controller_component.update_input_parameters(inputs)

        gas_turbine_component = GasTurbineComponent()
        gas_turbine_component.update_input_parameters(inputs)

        electric_motor_component = ElectricMotorComponent()
        electric_motor_component.update_input_parameters(inputs)

        inverter_component = InverterComponent()
        inverter_component.update_input_parameters(inputs)

        battery_component = BatteryComponent()
        battery_component.update_input_parameters(inputs)

        # Create the propulsion system module with configured components
        propulsion_system = HybridParallelModule(
            propeller=propeller_component,
            gearbox=gearbox_component,
            gearbox_controller=gearbox_controller_component,
            gas_turbine=gas_turbine_component,
            electric_motor=electric_motor_component,
            inverter=inverter_component,
            battery=battery_component,
        )

        engine_count = inputs["data:propulsion:engine_count"]

        # Return a FuelEngineSet with the propulsion system as engine
        return FuelEngineSet(engine=propulsion_system, engine_count=engine_count)
