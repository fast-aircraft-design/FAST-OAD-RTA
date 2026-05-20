"""
Estimation of other components center of gravities
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
import numpy as np
from fastoad.module_management.service_registry import RegisterSubmodel
from fastoad_cs25.models.weight.cg.constants import SERVICE_OTHERS_CG
from openmdao.core.explicitcomponent import ExplicitComponent

RegisterSubmodel.active_models[SERVICE_OTHERS_CG] = "rta.submodel.weight.cg.others.legacy"


@RegisterSubmodel(SERVICE_OTHERS_CG, "rta.submodel.weight.cg.others.legacy")
class ComputeOthersCG(ExplicitComponent):
    # TODO: Document equations. Cite sources
    """Other components center of gravities estimation"""

    def setup(self):  # noqa
        self.add_input("data:geometry:wing:MAC:leading_edge:x:local", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:root:chord", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:length", val=np.nan, units="m")
        self.add_input("data:geometry:wing:MAC:at25percent:x", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:front_length", val=np.nan, units="m")
        self.add_input("data:geometry:fuselage:rear_length", val=np.nan, units="m")
        self.add_input("data:weight:propulsion:engine:CG:x", val=np.nan, units="m")
        self.add_input("data:weight:fuel_tank:CG:x", val=np.nan, units="m")

        self.add_input("data:weight:operational:items:passenger_seats:CG:x", val=np.nan, units="m")
        self.add_input("data:weight:propulsion:engine:mass", val=np.nan, units="kg")
        self.add_input("data:geometry:cabin:NPAX1", val=np.nan)
        self.add_input("data:geometry:cabin:seats:economical:count_by_row", val=np.nan)
        self.add_input("data:geometry:cabin:seats:economical:length", val=np.nan, units="m")

        self.add_input("settings:geometry:fuselage:CG:ratio", val=0.45, units="unitless")

        # TODO: add description of these CGs
        self.add_output("data:weight:airframe:fuselage:CG:x", units="m")
        self.add_output("data:weight:airframe:landing_gear:front:CG:x", units="m")
        self.add_output("data:weight:propulsion:engine_controls_instrumentation:CG:x", units="m")
        self.add_output("data:weight:propulsion:fuel_lines:CG:x", units="m")

        self.add_output("data:weight:systems:auxiliary_power_unit:CG:x", units="m")
        self.add_output("data:weight:systems:electric_systems:electric_generation:CG:x", units="m")
        self.add_output(
            "data:weight:systems:electric_systems:electric_common_installation:CG:x",
            units="m",
        )
        self.add_output("data:weight:systems:hydraulic_systems:CG:x", units="m")

        self.add_output("data:weight:systems:fire_protection:CG:x", units="m")
        self.add_output("data:weight:systems:automatic_flight_system:CG:x", units="m")
        self.add_output("data:weight:systems:communications:CG:x", units="m")
        self.add_output("data:weight:systems:ECS:CG:x", units="m")
        self.add_output("data:weight:systems:de-icing:CG:x", units="m")
        self.add_output("data:weight:systems:navigation:CG:x", units="m")

        self.add_output("data:weight:furniture:furnishing:CG:x", units="m")
        self.add_output("data:weight:furniture:water:CG:x", units="m")
        self.add_output("data:weight:furniture:interior_integration:CG:x", units="m")
        self.add_output("data:weight:furniture:insulation:CG:x", units="m")
        self.add_output("data:weight:furniture:cabin_lighting:CG:x", units="m")
        self.add_output("data:weight:furniture:seats_crew_accommodation:CG:x", units="m")
        self.add_output("data:weight:furniture:oxygen:CG:x", units="m")

        self.add_output("data:weight:operational:items:documents_toolkit:CG:x", units="m")
        self.add_output("data:weight:operational:items:galley_structure:CG:x", units="m")
        self.add_output("data:weight:operational:equipment:others:CG:x", units="m")
        self.add_output("data:weight:operational:equipment:crew:CG:x", units="m")
        self.add_output("data:weight:operational:items:unusable_fuel:CG:x", units="m")

        self.add_output("data:weight:payload:PAX:CG:x", units="m")
        self.add_output("data:weight:payload:rear_fret:CG:x", units="m")
        self.add_output("data:weight:payload:front_fret:CG:x", units="m")

        self.declare_partials(
            "data:weight:airframe:fuselage:CG:x",
            "data:geometry:fuselage:length",
            method="fd",
        )
        self.declare_partials(
            "data:weight:airframe:landing_gear:front:CG:x",
            "data:geometry:fuselage:front_length",
            method="fd",
        )

        self.declare_partials(
            [
                "data:weight:propulsion:engine_controls_instrumentation:CG:x",
                "data:weight:systems:electric_systems:electric_generation:CG:x",
                "data:weight:systems:electric_systems:electric_common_installation:CG:x",
                "data:weight:systems:hydraulic_systems:CG:x",
                "data:weight:furniture:insulation:CG:x",
                "data:weight:furniture:cabin_lighting:CG:x",
                "data:weight:systems:communications:CG:x",
                "data:weight:systems:fire_protection:CG:x",
                "data:weight:systems:automatic_flight_system:CG:x",
                "data:weight:furniture:water:CG:x",
                "data:weight:operational:items:galley_structure:CG:x",
                "data:weight:operational:equipment:crew:CG:x",
            ],
            "data:geometry:fuselage:length",
            method="fd",
        )
        self.declare_partials(
            [
                "data:weight:systems:ECS:CG:x",
                "data:weight:furniture:seats_crew_accommodation:CG:x",
                "data:weight:furniture:oxygen:CG:x",
                "data:weight:furniture:furnishing:CG:x",
                "data:weight:furniture:interior_integration:CG:x",
                "data:weight:operational:items:documents_toolkit:CG:x",
            ],
            "data:weight:operational:items:passenger_seats:CG:x",
            method="fd",
        )
        self.declare_partials(
            "data:weight:systems:de-icing:CG:x",
            ["data:geometry:wing:MAC:at25percent:x", "data:geometry:wing:MAC:length"],
            method="fd",
        )
        self.declare_partials(
            "data:weight:operational:equipment:others:CG:x",
            [
                "data:weight:propulsion:engine:mass",
                "data:weight:propulsion:engine:CG:x",
                "data:geometry:cabin:NPAX1",
                "data:weight:operational:items:passenger_seats:CG:x",
            ],
            method="fd",
        )
        self.declare_partials(
            [
                "data:weight:systems:navigation:CG:x",
            ],
            "data:geometry:fuselage:front_length",
            method="fd",
        )

        self.declare_partials(
            "data:weight:payload:PAX:CG:x",
            "data:weight:operational:items:passenger_seats:CG:x",
            method="fd",
        )

        self.declare_partials(
            "data:weight:payload:rear_fret:CG:x",
            [
                "data:geometry:fuselage:rear_length",
                "data:geometry:wing:MAC:length",
                "data:geometry:wing:MAC:leading_edge:x:local",
                "data:geometry:wing:root:chord",
                "data:geometry:cabin:seats:economical:count_by_row",
                "data:geometry:cabin:seats:economical:length",
                "data:geometry:wing:MAC:at25percent:x",
                "data:geometry:fuselage:length",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:weight:payload:front_fret:CG:x",
            [
                "data:geometry:fuselage:front_length",
                "data:geometry:wing:MAC:length",
                "data:geometry:wing:MAC:leading_edge:x:local",
                "data:geometry:wing:MAC:at25percent:x",
            ],
            method="fd",
        )
        self.declare_partials(
            "data:weight:propulsion:fuel_lines:CG:x",
            "data:weight:fuel_tank:CG:x",
            method="fd",
        )
        self.declare_partials(
            "data:weight:operational:items:unusable_fuel:CG:x",
            "data:weight:fuel_tank:CG:x",
            method="fd",
        )

    def compute(self, inputs, outputs):  # noqa
        x0_wing = inputs["data:geometry:wing:MAC:leading_edge:x:local"]
        l0_wing = inputs["data:geometry:wing:MAC:length"]
        l2_wing = inputs["data:geometry:wing:root:chord"]
        fus_length = inputs["data:geometry:fuselage:length"]
        fa_length = inputs["data:geometry:wing:MAC:at25percent:x"]
        lav = inputs["data:geometry:fuselage:front_length"]
        lar = inputs["data:geometry:fuselage:rear_length"]
        x_cg_b1 = inputs["data:weight:propulsion:engine:CG:x"]
        x_cg_d2 = inputs["data:weight:operational:items:passenger_seats:CG:x"]
        weight_engines = inputs["data:weight:propulsion:engine:mass"]
        npax1 = inputs["data:geometry:cabin:NPAX1"]
        front_seat_number_eco = inputs["data:geometry:cabin:seats:economical:count_by_row"]
        ls_eco = inputs["data:geometry:cabin:seats:economical:length"]
        x_cg_tank = inputs["data:weight:fuel_tank:CG:x"]

        fuselage_cg_ratio = inputs["settings:geometry:fuselage:CG:ratio"]

        x_cg_a2 = fuselage_cg_ratio * fus_length

        # Assume cg of nose landing gear is at 75% of lav
        x_cg_a52 = lav * 0.75
        x_cg_b4 = lav * 0.5

        # APU is installed after the pressure bulkhead, and pressurized area is
        # about 80% of fuselage length
        x_cg_c11 = 0.95 * fus_length
        x_cg_c12 = 0.25 * fus_length  # modified
        x_cg_c13 = 0.5 * fus_length
        x_cg_c21 = fuselage_cg_ratio * fus_length
        x_cg_c22 = x_cg_d2
        x_cg_c23 = fa_length - 0.15 * l0_wing
        x_cg_c24 = fuselage_cg_ratio * fus_length
        x_cg_c25 = x_cg_d2
        x_cg_c26 = x_cg_d2
        x_cg_c27 = (0.01 * weight_engines * x_cg_b1 + 2.3 * npax1 * x_cg_d2) / (
            0.01 * weight_engines + 2.3 * npax1
        )
        x_cg_c3 = lav * 0.8
        x_cg_c4 = 0.25 * fus_length  # modified
        x_cg_c52 = x_cg_d2

        length_front_fret = fa_length - 0.25 * l0_wing - x0_wing - lav
        x_cg_front_fret = lav + length_front_fret * 0.5

        length_rear_fret = (
            fus_length
            - lar
            + (front_seat_number_eco - 5) * ls_eco
            - (lav + length_front_fret + 0.8 * l2_wing)
        )

        x_cg_rear_fret = lav + length_front_fret + 0.8 * l2_wing + length_rear_fret * 0.5

        x_cg_pl = x_cg_d2

        x_cg_e1 = fuselage_cg_ratio * fus_length
        x_cg_e3 = fuselage_cg_ratio * fus_length
        x_cg_e4 = 0.8 * fus_length
        x_cg_e5 = 0.9 * x_cg_d2
        x_cg_e7 = x_cg_d2
        x_cg_e8 = 0.7 * fus_length
        x_cg_e9 = 0.3 * fus_length

        outputs["data:weight:airframe:fuselage:CG:x"] = x_cg_a2
        outputs["data:weight:airframe:landing_gear:front:CG:x"] = x_cg_a52

        outputs["data:weight:propulsion:engine_controls_instrumentation:CG:x"] = x_cg_b4
        outputs["data:weight:propulsion:fuel_lines:CG:x"] = 0.977 * x_cg_tank

        outputs["data:weight:systems:auxiliary_power_unit:CG:x"] = x_cg_c11
        outputs["data:weight:systems:electric_systems:electric_generation:CG:x"] = x_cg_c12
        outputs["data:weight:systems:electric_systems:electric_common_installation:CG:x"] = x_cg_c12
        outputs["data:weight:systems:hydraulic_systems:CG:x"] = x_cg_c13

        outputs["data:weight:furniture:insulation:CG:x"] = x_cg_c21
        outputs["data:weight:systems:ECS:CG:x"] = x_cg_c22
        outputs["data:weight:systems:de-icing:CG:x"] = x_cg_c23
        outputs["data:weight:furniture:cabin_lighting:CG:x"] = x_cg_c24
        outputs["data:weight:furniture:seats_crew_accommodation:CG:x"] = x_cg_c25
        outputs["data:weight:furniture:oxygen:CG:x"] = x_cg_c26

        outputs["data:weight:operational:equipment:others:CG:x"] = x_cg_c27
        outputs["data:weight:systems:navigation:CG:x"] = x_cg_c3
        outputs["data:weight:systems:communications:CG:x"] = x_cg_c4
        outputs["data:weight:furniture:furnishing:CG:x"] = x_cg_c52

        outputs["data:weight:systems:fire_protection:CG:x"] = x_cg_e1
        outputs["data:weight:systems:automatic_flight_system:CG:x"] = x_cg_e3
        outputs["data:weight:furniture:water:CG:x"] = x_cg_e4
        outputs["data:weight:furniture:interior_integration:CG:x"] = x_cg_e5
        outputs["data:weight:operational:items:documents_toolkit:CG:x"] = x_cg_e7
        outputs["data:weight:operational:items:galley_structure:CG:x"] = x_cg_e8

        outputs["data:weight:operational:items:unusable_fuel:CG:x"] = x_cg_tank
        outputs["data:weight:operational:equipment:crew:CG:x"] = x_cg_e9

        outputs["data:weight:payload:PAX:CG:x"] = x_cg_pl
        outputs["data:weight:payload:rear_fret:CG:x"] = x_cg_rear_fret
        outputs["data:weight:payload:front_fret:CG:x"] = x_cg_front_fret
