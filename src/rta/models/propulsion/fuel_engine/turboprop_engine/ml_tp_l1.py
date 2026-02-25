"""Parametric turboprop engine."""
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

import logging
from typing import Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from fastoad.constants import FlightPhase
from fastoad.model_base.flight_point import FlightPoint
from fastoad_cs25.models.propulsion.fuel_propulsion.rubber_engine.exceptions import (
    FastRubberEngineInconsistentInputParametersError,
)
from scipy import constants
from stdatm import AtmosphereSI

from .base import AbstractFuelPropulsion
from .engine_components.propeller import Propeller

# Logger for this module
_LOGGER = logging.getLogger(__name__)


class ML_TP_L1(AbstractFuelPropulsion):
    def __init__(
        self,
        RTO_power: float,
        power_offtake: float,
        gearbox_eta: float,
        d_prop: float,
        k_gb_RTO: float,
        k_gb_NTO: float,
        k_gb_MCL: float,
        k_gb_MCR: float,
        k_psfc: float,
        k_prop: float,
    ):
        """
        Parametric turboprop engine.

        It computes engine characteristics using analytical model from following
        sources:

        Vincenzo Palladino, "Methode de conception pluridisciplinaire appliquee a
        un avion regional a faibles emissions" phd thesis, p72

        The power ratings (k_gb_TRO/NTO/MCR/MCL) are based on:
        O. Majeed, ‘Parametric specific fuel consumtption analysis of the PW120A Turboprop engine’,
        Specific Range Solutions Ltd., Technical Report SRS-TSD-002 rev 1, Jul. 2009.


        """

        self.RTO_power = RTO_power
        self.power_offtake = power_offtake
        self.gearbox_eta = gearbox_eta
        self.d_prop = d_prop

        self.k_gb_RTO = k_gb_RTO
        self.k_gb_NTO = k_gb_NTO
        self.k_gb_MCL = k_gb_MCL
        self.k_gb_MCR = k_gb_MCR

        self.k_psfc = k_psfc
        self.k_prop = k_prop

    def compute_flight_points(self, flight_points: Union[FlightPoint, pd.DataFrame]):
        """
        Same as :meth:`compute_flight_points`
        """

        Prop_fid = "ADT"
        mach = np.asarray(flight_points.mach)
        altitude = np.asarray(flight_points.altitude)
        disa = np.asarray(flight_points.isa_offset)
        thrust_rate = np.asarray(flight_points.thrust_rate)
        thrust = np.asarray(flight_points.thrust)
        phase = flight_points.engine_setting
        thrust_is_regulated = flight_points.thrust_is_regulated
        atmosphere = AtmosphereSI(altitude, delta_t=disa)

        if thrust_is_regulated is not None:
            thrust_is_regulated = np.asarray(np.round(thrust_is_regulated, 0), dtype=bool)

        thrust_is_regulated, thrust_rate, thrust = self._check_thrust_inputs(
            thrust_is_regulated, thrust_rate, thrust
        )
        thrust_is_regulated = np.asarray(np.round(thrust_is_regulated, 0), dtype=bool)
        max_shaft_power, max_thermo_power, gearbox_limit_power = self.max_power(
            atmosphere, mach, phase
        )

        T_prop, eta = Propeller().select(
            "power_to_thrust", Prop_fid, self, atmosphere, mach, max_shaft_power
        )
        FR = self.compute_engine_point(mach, T_prop=T_prop)

        max_thrust = T_prop + FR

        if not thrust_is_regulated:
            if thrust_rate == 1:
                power_rate = 1
                shaft_power = max_shaft_power
                thrust = thrust_rate * max_thrust
            else:
                thrust = thrust_rate * max_thrust
                shaft_power, eta = Propeller().select(
                    "thrust_to_power", Prop_fid, self, atmosphere, mach, thrust
                )

                power_rate = shaft_power / max_shaft_power
        else:
            power_rate = thrust_rate
            shaft_power, eta = Propeller().select(
                "thrust_to_power", Prop_fid, self, atmosphere, mach, thrust
            )

        thrust_rate = np.asarray(thrust_rate)
        thrust = np.asarray(thrust)

        shaft_power = np.asarray(shaft_power)
        power_rate = np.asarray(power_rate)

        # We compute thrust values from thrust rates when needed
        idx = np.logical_not(thrust_is_regulated)
        if np.size(max_thrust) == 1:  # se scalare
            maximum_thrust = max_thrust
            maximum_shaft_power = max_shaft_power
            out_thrust_rate = thrust_rate
            out_thrust = thrust
            out_power_rate = power_rate
            out_power = shaft_power
        else:  # se vettore
            out_thrust_rate = (
                np.full(np.shape(max_thrust), thrust_rate.item())
                if np.size(thrust_rate) == 1
                else thrust_rate
            )
            out_power_rate = (
                np.full(np.shape(max_shaft_power), power_rate.item())
                if np.size(power_rate) == 1
                else power_rate
            )
            out_thrust = (
                np.full(np.shape(max_thrust), thrust.item()) if np.size(thrust) == 1 else thrust
            )
            out_power = (
                np.full(np.shape(max_shaft_power), shaft_power.item())
                if np.size(shaft_power) == 1
                else shaft_power
            )

            maximum_thrust = max_thrust[idx]
            maximum_shaft_power = max_shaft_power[idx]

        out_thrust[idx] = out_thrust_rate[idx] * maximum_thrust
        out_power[idx] = out_power_rate[idx] * maximum_shaft_power

        out_thrust_rate = out_thrust / max_thrust
        out_power_rate = out_power / max_shaft_power

        # Now SFC can be computed
        psfc = self.psfc(atmosphere, mach, out_power_rate, phase) * self.k_psfc  # kg/hp/hr
        ff = psfc / constants.hour * out_power / constants.hp  # Kg/s
        tsfc = ff / out_thrust

        flight_points.psfc = psfc / constants.hour / constants.hp
        flight_points.thrust_rate = out_thrust_rate
        flight_points.thrust = out_thrust
        flight_points.TPshaft_power = out_power
        flight_points.TP_power_rate = out_power_rate
        flight_points.thermo_power = max_thermo_power
        flight_points.TP_residual_thrust = FR
        flight_points.sfc = tsfc

    @staticmethod
    def _check_thrust_inputs(
        thrust_is_regulated: Optional[Union[float, Sequence]],
        thrust_rate: Optional[Union[float, Sequence]],
        thrust: Optional[Union[float, Sequence]],
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Checks that inputs are consistent and return them in proper shape.

        Some of the inputs can be None, but outputs will be proper numpy arrays.

        :param thrust_is_regulated:
        :param thrust_rate:
        :param thrust:
        :return: the inputs, but transformed in numpy arrays.
        """
        # Ensure they are numpy array
        if thrust_is_regulated is not None:
            # As OpenMDAO may provide floats that could be slightly different
            # from 0. or 1., a rounding operation is needed before converting
            # to booleans
            thrust_is_regulated = np.asarray(np.round(thrust_is_regulated, 0), dtype=bool)
        if thrust_rate is not None:
            thrust_rate = np.asarray(thrust_rate)
        if thrust is not None:
            thrust = np.asarray(thrust)

        # Check inputs: if use_thrust_rate is None, we will use the provided input between
        # thrust_rate and thrust
        if thrust_is_regulated is None:
            if thrust_rate is not None:
                thrust_is_regulated = False
                thrust = np.empty_like(thrust_rate)
            elif thrust is not None:
                thrust_is_regulated = True
                thrust_rate = np.empty_like(thrust)
            else:
                raise FastRubberEngineInconsistentInputParametersError(
                    "When use_thrust_rate is None, either thrust_rate or thrust should be provided."
                )

        elif np.size(thrust_is_regulated) == 1:
            # Check inputs: if use_thrust_rate is a scalar, the matching input(thrust_rate or
            # thrust) must be provided.
            if thrust_is_regulated:
                if thrust is None:
                    raise FastRubberEngineInconsistentInputParametersError(
                        "When thrust_is_regulated is True, thrust should be provided."
                    )
                thrust_rate = np.empty_like(thrust)
            else:
                if thrust_rate is None:
                    raise FastRubberEngineInconsistentInputParametersError(
                        "When thrust_is_regulated is False, thrust_rate should be provided."
                    )
                thrust = np.empty_like(thrust_rate)

        else:
            # Check inputs: if use_thrust_rate is not a scalar, both thrust_rate and thrust must be
            # provided and have the same shape as use_thrust_rate
            if thrust_rate is None or thrust is None:
                raise FastRubberEngineInconsistentInputParametersError(
                    "When thrust_is_regulated is a sequence, both thrust_rate and thrust should be "
                    "provided."
                )
            if np.shape(thrust_rate) != np.shape(thrust_is_regulated) or np.shape(
                thrust
            ) != np.shape(thrust_is_regulated):
                raise FastRubberEngineInconsistentInputParametersError(
                    "When use_thrust_rate is a sequence, both thrust_rate and thrust should have "
                    "same shape as use_thrust_rate"
                )

        return thrust_is_regulated, thrust_rate, thrust

    def psfc(
        self,
        atmosphere: AtmosphereSI,
        mach: Union[float, Sequence[float]],
        power_rate: Union[float, Sequence[float]],
        phase: Union[FlightPhase, Sequence],
    ) -> np.ndarray:
        """
        :param atmosphere: Atmosphere instance at intended altitude (should be <=20km)
        :param mach: Mach number(s) (should be between 0.05 and 1.0)
        :param phase: Flight phase which influences engine rating (max mechanical power)
        :param power_rate: The power rate [0,1.0]
        :return: SFC ratio
        """
        altitude = atmosphere.get_altitude(altitude_in_feet=True)
        if phase == 1:
            power_rate = 1.0

        c0 = 0.9533
        c1 = -1.4739e-5
        c2 = -1.285e-1
        c3 = -2.257
        c4 = 1.887e-10
        c5 = -4.882e-8
        c6 = 2.685e-5
        c7 = -2.707e-1
        c8 = 4.479e-1
        c9 = 2.511
        c10 = -2.497e-15
        c11 = 1.132e-10
        c12 = -9.598e-11
        c13 = -1.182e-6
        c14 = -3.861e-6
        c15 = -1.471e-5
        c16 = 6.02e-2
        c17 = 2.522e-1
        c18 = -3.248e-1
        c19 = -9.402e-1

        psfc = (
            c0
            + c1 * altitude
            + c2 * mach
            + c3 * power_rate
            + c4 * altitude**2
            + c5 * altitude * mach
            + c6 * altitude * power_rate
            + c7 * mach**2
            + c8 * mach * power_rate
            + c9 * power_rate**2
            + c10 * altitude**3
            + c11 * altitude**2 * mach
            + c12 * altitude**2 * power_rate
            + c13 * altitude * mach**2
            + c14 * altitude * mach * power_rate
            + c15 * altitude * power_rate**2
            + c16 * mach**3
            + c17 * mach**2 * power_rate
            + c18 * mach * power_rate**3
            + c19 * power_rate**3
        )

        return psfc

    def max_power(
        self,
        atmosphere: AtmosphereSI,
        mach: Union[float, Sequence[float]],
        phase: Union[FlightPhase, Sequence],
    ) -> tuple:
        """
        Computation of maximum available power.

        :param atmosphere: Atmosphere instance at intended altitude (should be <=20km)
        :param mach: Mach number(s) (should be between 0.05 and 1.0)
        :param phase: flight phase which influences engine rating (max mechanical power)
        :return: (m)aximum shaft power, maximum thermal power, maximum rated power) (in W)
        """
        """
        TAXI_IN = 0
        TAKEOFF = 1 : k_gb_nto
        CLIMB = 2   : k_gb_mcl
        CRUISE = 3  : k_gb_mcr
        DESCENT = 5 : k_gb_mcl
        """
        altitude = atmosphere.get_altitude(altitude_in_feet=True)
        mach = np.asarray(mach)

        if phase == 2:  # 'MCL'
            max_power_rating = self.k_gb_MCL * self.RTO_power / constants.hp  # *1.05

        elif phase == 1:  # 'TO'
            max_power_rating = self.k_gb_NTO * self.RTO_power / constants.hp

        elif phase == 3:  # 'CRZ'
            max_power_rating = self.k_gb_MCR * self.RTO_power / constants.hp

        elif phase == 8:  # 'RTO'
            max_power_rating = self.k_gb_RTO * self.RTO_power / constants.hp  # Watt =2400. hp

        else:
            max_power_rating = self.RTO_power / constants.hp

        c0 = 1.015
        c1 = -2.806e-6
        c2 = -8.498e-2
        c3 = -8.928e-10
        c4 = 2.253e-5
        c5 = 1.943e-1
        c6 = 1.914e-14
        c7 = -8.816e-10
        c8 = 1.919e-5
        c9 = -3.257e-1

        K_powerlapse = (
            c0
            + c1 * altitude
            + c2 * mach
            + c3 * altitude**2
            + c4 * altitude * mach
            + c5 * mach**2
            + c6 * altitude**3
            + c7 * altitude**2 * mach
            + c8 * altitude * mach**2
            + c9 * mach**3
        )

        # Correction coefficient to account for DISA (Mattingly)
        # Assumes the surrogate model behaves as P ~ (rho / rho_0)**0.7
        # Compares two ratios (rho_ISA0 / rho_0_ISA0) and (rho_ISA / rho_0_ISA0)
        # If the ratios differ, then k_isa represent the correction to apply
        density_isa0 = AtmosphereSI(altitude=atmosphere.altitude, delta_t=0).density
        density_ground_isa0 = AtmosphereSI(altitude=0, delta_t=0).density

        density_ratio_isa0 = (density_isa0 / density_ground_isa0) ** 0.7
        density_ratio = (atmosphere.density / density_ground_isa0) ** 0.7
        k_isa = (density_ratio / density_ratio_isa0) ** 0.7

        max_thermo_power = max_power_rating * K_powerlapse * k_isa

        if max_thermo_power > max_power_rating:
            max_shaft_power = max_power_rating  # hp #gearbox mechanical limit
        else:
            max_shaft_power = max_thermo_power

        return (
            max_shaft_power * constants.hp,
            max_thermo_power * constants.hp,
            max_power_rating * constants.hp,
        )

    def compute_engine_point(
        self,
        mach: Union[float, Sequence[float]],
        T_prop=1,
    ) -> np.ndarray:
        """Based on correlation provided by J. D. Anderson, Aircraft Performance and Design p183"""

        # With: ratio = Tjet/(Tjet+Tprop)
        ratio = np.interp(mach, [0, 0.5], [0.02, 0.06])

        Tjet = T_prop * ratio / (1 - ratio)
        return Tjet
