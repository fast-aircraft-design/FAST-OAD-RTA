"""
OpenMDAO wrapper for the PropulsionSystemModule.

This module provides an OpenMDAO wrapper that wraps the PropulsionSystemModule
for integration with FAST-OAD's OpenMDAO-based workflow.
"""

#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2020  ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from openmdao.core.component import Component

from fastoad.model_base.propulsion import (
    FuelEngineSet,
    IOMPropulsionWrapper,
    BaseOMPropulsionComponent,
)

from .gearbox import GearboxComponent
from .propeller_power_calculator import PropellerPowerCalculator
from .propulsion_system_module import PropulsionSystemModule


class PropulsionSystemOMWrapper(IOMPropulsionWrapper):
    """
    OpenMDAO wrapper for the PropulsionSystemModule.

    This wrapper allows the PropulsionSystemModule to be used within FAST-OAD's
    OpenMDAO-based workflow by:
        1. Declaring all required inputs from propeller and gearbox components in setup()
        2. Instantiating the components and propagating inputs in get_model()

    Usage:
        The wrapper can be used with BaseOMPropulsionComponent or similar
        OpenMDAO components that implement the IOMPropulsionWrapper interface.
    """

    def setup(self, component: Component):
        """
        Declare all required inputs from propeller and gearbox components.

        This method iterates through the inputs of both the PropellerPowerCalculator
        and GearboxComponent classes (not instances) and declares them as OpenMDAO
        input variables using component.add_input().

        Args:
            component: The OpenMDAO component where inputs will be declared.
        """
        # Declare inputs from PropellerPowerCalculator
        for var in PropellerPowerCalculator.inputs:
            component.add_input(var.name, np.nan, units=var.units)

        # Declare inputs from GearboxComponent
        for var in GearboxComponent.inputs:
            component.add_input(var.name, np.nan, units=var.units)

    @staticmethod
    def get_model(inputs) -> FuelEngineSet:
        """
        Create and configure the propulsion system model instance.

        This method:
            1. Instantiates the PropellerPowerCalculator and GearboxComponent
            2. Updates their inputs from the provided inputs vector
            3. Creates a PropulsionSystemModule with the configured components
            4. Returns a FuelEngineSet wrapping the propulsion system module

        Args:
            inputs: OpenMDAO input vector containing the propulsion parameters.

        Returns:
            FuelEngineSet instance with the PropulsionSystemModule as engine.
        """
        # Instantiate the propeller power calculator
        propeller = PropellerPowerCalculator()

        # Instantiate the gearbox
        gearbox = GearboxComponent()

        # Update propeller inputs from the inputs vector
        propeller.inputs.update(inputs, add_variables=False)

        # Update gearbox inputs from the inputs vector
        gearbox.inputs.update(inputs, add_variables=False)

        # Create the propulsion system module with configured components
        propulsion_system = PropulsionSystemModule(
            propeller_power_calculator=propeller,
            gearbox=gearbox,
        )

        # Return a FuelEngineSet with the propulsion system as engine
        # engine_count=1 for a single engine configuration
        return FuelEngineSet(engine=propulsion_system, engine_count=2)


class OMPropulsionSystemComponent(BaseOMPropulsionComponent):
    """
    Parametric engine model as OpenMDAO component. Used for unit and integration tests.

    """

    def setup(self):
        super().setup()
        self.get_wrapper().setup(self)

    def setup_partials(self):
        self.declare_partials("*", "*", method="fd")

    @staticmethod
    def get_wrapper() -> PropulsionSystemOMWrapper:
        return PropulsionSystemOMWrapper()
