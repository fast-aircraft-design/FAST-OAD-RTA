from typing import Sequence, Union

import numpy as np
from fastoad._utils.arrays import scalarize
from scipy import constants
from scipy.optimize import fsolve
from stdatm import AtmosphereSI


class Propeller(object):
    def select(self, function, fidelity, data, atmosphere, mach, P_T):
        func = getattr(self, function + "_" + fidelity)

        return func(data, atmosphere, mach, P_T)

    def power_to_thrust_ADT(
        self,
        data,
        atmosphere: AtmosphereSI,
        mach: Union[float, Sequence[float]],
        shaft_power: Union[float, Sequence[float]],
    ) -> tuple:
        """
        Computation of propeller thrust given propeller shaft power.

        :param shaft_power: shaft_power in W
        :param atmosphere: Atmosphere instance at intended altitude
        :param mach: Mach number(s)
        :return: thrust (in N)
        """
        shp_prop = shaft_power * data.gearbox_eta / constants.hp  # hp
        a = atmosphere.speed_of_sound

        # inputs
        V_TAS = mach * a  # m/s
        rho = atmosphere.density
        d = data.d_prop
        k_corr = 0.895

        # evaluate thrust from given power
        def P_to_T(T_prop, shp_prop, V_TAS, rho, d):
            return (T_prop * V_TAS / (shp_prop * constants.hp)) - 2 / (
                1 + (1 + (T_prop / (0.5 * rho * constants.pi / 4 * d**2 * V_TAS**2))) ** 0.5
            )

        if mach < 0.2:
            # Formulation for low speed operation

            # static thrust
            eta = 0.0
            T_prop_0 = (
                55000 * shp_prop / (1200 * d / constants.foot) * constants.pound_force
            )  # Skellett, A. M. National Advisory Committee for Aeronautics, Nineteenth Annual Report. Report n447

            # thrust at mach=0.2
            T_prop_ref = fsolve(P_to_T, 1, args=(shp_prop, 0.2 * a, rho, d))[0]
            T_prop_ref = T_prop_ref * k_corr * data.k_prop

            # Interpol while mach is between [0,0.2]
            x = [0, 0.2]
            y = [scalarize(T_prop_0), scalarize(T_prop_ref)]

            T_prop = np.interp(scalarize(mach), x, y)

        else:
            T_prop = fsolve(P_to_T, 1, args=(shp_prop, V_TAS, rho, d))[0]
            T_prop = T_prop * k_corr * data.k_prop
            eta = T_prop * V_TAS / (shp_prop * constants.hp)  # N

        return T_prop, eta

    def thrust_to_power_ADT(
        self,
        data,
        atmosphere: AtmosphereSI,
        mach: Union[float, Sequence[float]],
        thrust: Union[float, Sequence],
    ) -> tuple:
        """
        Computation of propeller shaft power given propeller thrust WITHOUT FR.


        :param atmosphere: Atmosphere instance at intended altitude
        :param mach: Mach number(s)
        :return: thrust (in N)
        """

        a = atmosphere.speed_of_sound
        V_TAS = max(0.1, mach * a)  # m/s
        rho = atmosphere.density
        d = data.d_prop
        k_corr = 0.895

        # evaluate required power from given thrust

        eta = 2 / (1 + (1 + (thrust / (0.5 * rho * constants.pi / 4 * d**2 * V_TAS**2))) ** 0.5)
        eta = k_corr * data.k_prop * eta

        shp_prop = thrust * V_TAS / eta / constants.hp
        shaft_power = (shp_prop * constants.hp) / data.gearbox_eta

        return shaft_power, eta
