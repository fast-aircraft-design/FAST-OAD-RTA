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

from fastoad.model_base.propulsion import (
    FuelEngineSet,
    IOMPropulsionWrapper,
)
from openmdao.core.component import Component

from .hybrid_parallel_module import HybridParallelModule
from ...component_library.battery import BatteryComponent
from ...component_library.electric_motor import ElectricMotorComponent
from ...component_library.gas_turbine import GasTurbineComponent
from ...component_library.geabox_controller import GearboxControllerComponent
from ...component_library.gearbox import GearboxComponent
from ...component_library.inverter import InverterComponent
from ...component_library.propeller import PropellerComponent


class HybridParallelOMWrapper(IOMPropulsionWrapper):
    """
    Placeholder docstring
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.propeller_component = PropellerComponent()
        self.gearbox_component = GearboxComponent()
        self.gearbox_controller_component = GearboxControllerComponent()
        self.gas_turbine_component = GasTurbineComponent()
        self.electric_motor_component = ElectricMotorComponent()
        self.inverter_component = InverterComponent()
        self.battery_component = BatteryComponent()

    def setup(self, component: Component):
        """
        Placeholder docstring
        """
        # Declare default inputs from PropellerComponent
        self.propeller_component.declare_openmdao_inputs(component)

        # Declare inputs from GearboxComponent
        self.gearbox_component.declare_openmdao_inputs(component)

        # Declare inputs from GearboxControllerComponent
        self.gearbox_controller_component.declare_openmdao_inputs(component)

        # Declare inputs from GasTurbineComponent
        self.gas_turbine_component.declare_openmdao_inputs(component)

        # Declare inputs from ElectricMotorComponent
        self.electric_motor_component.declare_openmdao_inputs(component)

        # Declare inputs from InverterComponent
        self.inverter_component.declare_openmdao_inputs(component)

        # Declare inputs from BatteryComponent
        self.battery_component.declare_openmdao_inputs(component)

    def get_model(self, inputs) -> FuelEngineSet:
        """
        Placeholder docstring
        """

        # Update inputs from the inputs vector
        self.propeller_component.update_input_parameters(inputs)
        self.gearbox_component.update_input_parameters(inputs)
        self.gearbox_controller_component.update_input_parameters(inputs)
        self.gas_turbine_component.update_input_parameters(inputs)
        self.electric_motor_component.update_input_parameters(inputs)
        self.inverter_component.update_input_parameters(inputs)
        self.battery_component.update_input_parameters(inputs)

        # Create the propulsion system module with configured components
        propulsion_system = HybridParallelModule(
            propeller=self.propeller_component,
            gearbox=self.gearbox_component,
            gearbox_controller=self.gearbox_controller_component,
            gas_turbine=self.gas_turbine_component,
            electric_motor=self.electric_motor_component,
            inverter=self.inverter_component,
            battery=self.battery_component,
        )

        engine_count = inputs["data:propulsion:engine_count"]

        # Return a FuelEngineSet with the propulsion system as engine
        return FuelEngineSet(engine=propulsion_system, engine_count=engine_count)
