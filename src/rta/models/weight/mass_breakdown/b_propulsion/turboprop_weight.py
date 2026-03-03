# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 10:12:50 2020

@author: LA202059
"""

import numpy as np
from fastoad.module_management.service_registry import RegisterSubmodel
from openmdao.core.explicitcomponent import ExplicitComponent
from scipy import constants

from rta.models.weight.mass_breakdown.b_propulsion.constants import (
    SERVICE_TURBOPROP_MASS,
)


@RegisterSubmodel(SERVICE_TURBOPROP_MASS, "rta.submodel.weight.mass.propulsion.turboprop.legacy")
class TurbopropWeight(ExplicitComponent):
    """
    Weight estimation for turboprop propulsion systems
    Ref. Teeuwen, Y., “Propeller Design for Conceptual Turboprop Aircraft,”
    Master’s thesis, Delft University of Technology, 2017.


    """

    def setup(self):
        self.add_input("data:propulsion:RTO_power", val=np.nan, units="W")
        self.add_input("data:geometry:propulsion:engine:count", val=np.nan)
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m")
        self.add_input("data:geometry:propulsion:propeller:diameter", val=np.nan, units="m")
        self.add_input("data:geometry:propulsion:propeller:B", val=np.nan)
        self.add_input("tuning:weight:propulsion:engine:mass:k", val=1.0)
        self.add_input("tuning:weight:propulsion:engine_controls_instrumentation:mass:k", val=1.0)
        self.add_input("tuning:weight:propulsion:propeller:mass:k", val=1.0)

        self.add_input("data:propulsion:propeller:max_power", val=np.nan, units="kW")

        self.add_output("data:weight:propulsion:engine:mass", units="kg")
        self.add_output("data:weight:propulsion:engine_controls_instrumentation:mass", units="kg")
        self.add_output("data:weight:propulsion:propeller:mass", units="kg")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        design_electric_power = inputs["data:propulsion:RTO_power"]
        n_eng = inputs["data:geometry:propulsion:engine:count"]
        l_fus = inputs["data:geometry:fuselage:length"]
        k_eng = inputs["tuning:weight:propulsion:engine:mass:k"]
        k_ec = inputs["tuning:weight:propulsion:engine_controls_instrumentation:mass:k"]
        k_prop = inputs["tuning:weight:propulsion:propeller:mass:k"]
        D_prop = inputs["data:geometry:propulsion:propeller:diameter"]
        n_blades = inputs["data:geometry:propulsion:propeller:B"]
        design_electric_power_prop = inputs["data:propulsion:propeller:max_power"] * 1000

        m_eng = (
            0.758 * (design_electric_power / constants.hp) ** 0.803
        )  # mass of dry engine and gearbox

        m_prop = 0.5 * ((D_prop * design_electric_power_prop * (n_blades) ** 0.5) / 227.2) ** 0.52
        m_ec = 0.454 * (5 * n_eng + 2.63 * l_fus)
        m_ess = 22.31 * ((m_eng * n_eng) / 453.59) ** 0.541
        m_osc = 0.07 * m_eng

        m_eng_installed = (m_eng + m_osc) * n_eng + m_ess

        outputs["data:weight:propulsion:engine:mass"] = m_eng_installed * k_eng
        outputs["data:weight:propulsion:engine_controls_instrumentation:mass"] = m_ec * k_ec
        outputs["data:weight:propulsion:propeller:mass"] = m_prop * n_eng * k_prop
