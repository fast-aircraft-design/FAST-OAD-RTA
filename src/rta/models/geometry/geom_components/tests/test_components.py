from fastoad.testing import run_system
from openmdao.core.indepvarcomp import IndepVarComp
from pytest import approx

from ..fuselage.compute_fuselage import (
    ComputeFuselageGeometryBasic,
    ComputeFuselageGeometryCabinSizing,
)
from ..nacelle.compute_nacelle import ComputeNacelleGeometry
from ..wing.components.compute_toc_wing_rta import ComputeToCWingRTA
from ..wing.components.compute_wet_area_wing_rta import ComputeWetAreaWingRTA


def test_nacelle():
    ivc = IndepVarComp()

    ivc.add_output("data:geometry:propulsion:engine:y_ratio", val=0.3)
    ivc.add_output("data:geometry:wing:span", val=26.84, units="m")
    ivc.add_output("data:propulsion:design_thermal_power", val=2.497e6, units="W")
    ivc.add_output("data:propulsion:electric_systems:design_electric_power", val=0.0, units="W")

    problem = run_system(ComputeNacelleGeometry(), ivc)

    assert problem.get_val("data:geometry:propulsion:nacelle:length", "m") == approx(2.17, rel=1e-3)
    assert problem.get_val("data:geometry:propulsion:nacelle:diameter", "m") == approx(
        0.638, rel=1e-3
    )
    assert problem.get_val("data:geometry:propulsion:nacelle:y", "m") == approx(4.026, rel=1e-3)
    assert problem.get_val("data:geometry:propulsion:nacelle:wetted_area", "m**2") == approx(
        4.349, rel=1e-3
    )


def test_wing_ToC():
    ivc = IndepVarComp()

    ivc.add_output("data:TLAR:cruise_mach", val=0.45)
    ivc.add_output("data:geometry:wing:sweep_25", val=2.3, units="deg")

    problem = run_system(ComputeToCWingRTA(), ivc)

    assert problem.get_val(
        "data:geometry:wing:thickness_ratio",
    ) == approx(0.1407, rel=1e-3)
    assert problem.get_val(
        "data:geometry:wing:root:thickness_ratio",
    ) == approx(0.1875, rel=1e-3)
    assert problem.get_val(
        "data:geometry:wing:kink:thickness_ratio",
    ) == approx(0.1407, rel=1e-3)
    assert problem.get_val(
        "data:geometry:wing:tip:thickness_ratio",
    ) == approx(0.125, rel=1e-3)


def test_wing_wet_area():
    ivc = IndepVarComp()

    ivc.add_output("data:geometry:wing:root:chord", val=2.634, units="m")
    ivc.add_output("data:geometry:wing:root:y", val=1.396, units="m")
    ivc.add_output("data:geometry:wing:area", val=60.07, units="m**2")
    ivc.add_output("data:geometry:wing:thickness_ratio", val=0.1407)

    problem = run_system(ComputeWetAreaWingRTA(), ivc)

    assert problem.get_val("data:geometry:wing:outer_area", "m**2") == approx(52.715, rel=1e-3)
    assert problem.get_val("data:geometry:wing:wetted_area", "m**2") == approx(108.075, rel=1e-3)


def test_fuselage_basic():
    ivc = IndepVarComp()

    ivc.add_output("data:geometry:cabin:NPAX1", val=75)
    ivc.add_output("data:geometry:fuselage:length", val=26.96, units="m")
    ivc.add_output("data:geometry:fuselage:maximum_width", val=2.79, units="m")
    ivc.add_output("data:geometry:fuselage:maximum_height", val=2.93, units="m")
    ivc.add_output("data:geometry:fuselage:front_length", val=4.99, units="m")
    ivc.add_output("data:geometry:fuselage:rear_length", val=10.56, units="m")
    ivc.add_output("data:geometry:fuselage:PAX_length", val=14.47, units="m")

    problem = run_system(ComputeFuselageGeometryBasic(), ivc)

    assert problem.get_val("data:weight:systems:flight_furnishing:CG:x", "m") == approx(
        2.495, rel=1e-3
    )
    assert problem.get_val("data:weight:operational:items:passenger_seats:CG:x", "m") == approx(
        10.055, rel=1e-3
    )
    assert problem.get_val("data:geometry:cabin:length", "m") == approx(21.838, rel=1e-3)
    assert problem.get_val("data:geometry:fuselage:wetted_area", "m**2") == approx(
        206.885, rel=1e-3
    )
    assert problem.get_val(
        "data:geometry:cabin:crew_count:commercial",
    ) == approx(2.0, rel=1e-3)


def test_fuselage_with_cabin_sizing():
    ivc = IndepVarComp()

    ivc.add_output("data:geometry:cabin:seats:economical:width", val=0.4572, units="m")
    ivc.add_output("data:geometry:cabin:seats:economical:length", val=0.762, units="m")
    ivc.add_output("data:geometry:cabin:seats:economical:count_by_row", val=4.0)
    ivc.add_output("data:geometry:cabin:aisle_width", val=0.45, units="m")
    ivc.add_output("data:geometry:cabin:exit_width", val=0.75, units="m")
    ivc.add_output("data:TLAR:NPAX", val=72)
    ivc.add_output("data:geometry:propulsion:engine:count", val=2)

    problem = run_system(ComputeFuselageGeometryCabinSizing(), ivc)

    assert problem.get_val(
        "data:geometry:cabin:NPAX1",
    ) == approx(75, rel=1e-3)
    assert problem.get_val("data:weight:systems:flight_furnishing:CG:x", "m") == approx(
        2.493, rel=1e-3
    )
    assert problem.get_val("data:weight:operational:items:passenger_seats:CG:x", "m") == approx(
        12.219, rel=1e-3
    )
    assert problem.get_val("data:geometry:fuselage:length", "m") == approx(26.96, rel=1e-3)
    assert problem.get_val("data:geometry:fuselage:maximum_width", "m") == approx(2.793, rel=1e-3)
    assert problem.get_val("data:geometry:fuselage:maximum_height", "m") == approx(2.933, rel=1e-3)
    assert problem.get_val("data:geometry:fuselage:front_length", "m") == approx(4.985, rel=1e-3)
    assert problem.get_val("data:geometry:fuselage:rear_length", "m") == approx(10.558, rel=1e-3)
    assert problem.get_val("data:geometry:fuselage:PAX_length", "m") == approx(14.466, rel=1e-3)
    assert problem.get_val("data:geometry:cabin:length", "m") == approx(21.839, rel=1e-3)
    assert problem.get_val("data:geometry:fuselage:wetted_area", "m**2") == approx(207.13, rel=1e-3)
    assert problem.get_val(
        "data:geometry:cabin:crew_count:commercial",
    ) == approx(2.0, rel=1e-3)
