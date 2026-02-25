"""OpenMDAO wrapping of RubberEngine."""
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

import numpy as np
from fastoad.model_base.propulsion import (
    FuelEngineSet,
    IOMPropulsionWrapper,
    IPropulsion,
)
from fastoad.module_management.service_registry import RegisterPropulsion
from openmdao.core.component import Component

from .ml_tp_l1 import ML_TP_L1

####################################################################################################
# TURBOPROP model
####################################################################################################


@RegisterPropulsion("rta.wrapper.propulsion.ML_TP_L1")
class OMMLTPL1Wrapper(IOMPropulsionWrapper):
    """
    Wrapper class of for metamodel of TP engine L1 model.

    It is made to allow a direct call to :class:`~.turboprop_engine.ML_TP_L1` in an OpenMDAO
    component.

    """

    def setup(self, component: Component):
        component.add_input("data:propulsion:RTO_power", np.nan, units="W")
        component.add_input("data:propulsion:power_offtake", np.nan, units="W")
        component.add_input("data:propulsion:gearbox_eta", np.nan)
        component.add_input("data:geometry:propulsion:propeller:diameter", np.nan, units="m")
        component.add_input("data:geometry:propulsion:engine:count", 2)
        # tuning factors
        component.add_input("tuning:propulsion:k_psfc", np.nan)
        component.add_input("tuning:propulsion:k_prop", np.nan)

        # rating settings
        component.add_input("settings:propulsion:ratings:RTO:k_gb", np.nan)
        component.add_input("settings:propulsion:ratings:NTO:k_gb", np.nan)
        component.add_input("settings:propulsion:ratings:MCL:k_gb", np.nan)
        component.add_input("settings:propulsion:ratings:MCT:k_gb", np.nan)
        component.add_input("settings:propulsion:ratings:MCR:k_gb", np.nan)

    @staticmethod
    def get_model(inputs) -> IPropulsion:
        """

        :param inputs: input parameters that define the engine
        :return: an :class:`ML_TP_L1` instance
        """
        engine_params = {
            "RTO_power": inputs["data:propulsion:RTO_power"],
            "power_offtake": inputs["data:propulsion:power_offtake"],
            "gearbox_eta": inputs["data:propulsion:gearbox_eta"],
            "d_prop": inputs["data:geometry:propulsion:propeller:diameter"],
            "k_gb_RTO": inputs["settings:propulsion:ratings:RTO:k_gb"],
            "k_gb_NTO": inputs["settings:propulsion:ratings:NTO:k_gb"],
            "k_gb_MCL": inputs["settings:propulsion:ratings:MCL:k_gb"],
            "k_gb_MCR": inputs["settings:propulsion:ratings:MCR:k_gb"],
            "k_psfc": inputs["tuning:propulsion:k_psfc"],
            "k_prop": inputs["tuning:propulsion:k_prop"],
        }

        return FuelEngineSet(
            ML_TP_L1(**engine_params), inputs["data:geometry:propulsion:engine:count"]
        )
