# # CAT6A S/STP cable: HFSS S-parameter extraction and Nexxim EFT transient
#
# This example replaces the original Cable-Harness-Modeling workflow with a
# fully explicit faceted 3D HFSS model of a CAT6A S/STP 4x2 AWG25/7 cable,
# extracts an N-port S-parameter model, and then drives it from a Circuit
# (Nexxim) transient schematic with an IEC 61000-4-4 EFT pulse and
# user-defined terminations.
#
# The geometry, materials, route, ports, EFT source and terminations are
# all read from a single YAML file (``cat6a_sstp_awg25.yaml``) so that the
# same script can model variants of the cable without code changes.
#
# Keywords: **HFSS**, **Circuit**, **Nexxim**, **EMC**, **cable**, **CAT6A**,
# **EFT**, **transient**, **S-parameters**.

# ## Perform imports and define constants

# +
from __future__ import annotations

import math
import os
import tempfile
import time
from pathlib import Path
from typing import Any
import transfer_impedance as ti

import numpy as np
import yaml

import ansys.aedt.core
from ansys.aedt.core import Circuit, Hfss
# -

AEDT_VERSION = "2025.2"
NG_MODE = False
YAML_FILE = Path(__file__).parent / "_static" / "cat6a_sstp_awg25.yaml"

# ## Create a temporary working directory

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
project_path = Path(temp_folder.name) / "cat6a_eft_transient.aedt"

# ## Load the YAML cable definition

cfg = yaml.safe_load(YAML_FILE.read_text())

UNITS         = cfg.get("units", "mm")
SIM = cfg["simulation"]
GEOM = SIM["geometry"]
PORT_CFG  = SIM["ports"]
TERM_CFG = SIM.get("terminations", {}) or {}
TRAN_CFG = SIM["transient"]
TRANSIENT_SOURCE_CFG = TRAN_CFG["source"]
FACETS = int(GEOM.get("facets", 8))
SAMPLES_PER_PITCH = int(GEOM.get("samples_per_pitch", 8))
LIGHT_GREY = (200, 200, 200)   # RGB tuple for rendering outer braid shield.

# ## Launch AEDT and create the HFSS design

hfss = Hfss(
    project=project_path,
    design="CAT6A_3D",
    solution_type="DrivenTerminal",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
)
hfss.modeler.model_units = UNITS
hfss.change_material_override(material_override=True)
hfss.change_automatically_use_causal_materials(lossy_dielectric=True)

# ## Helper functions
#
# Small, self-contained helpers for vector math, faceted sweeps and twisted
# centerlines. They are kept inside the example rather than imported so the
# notebook stays self-documenting.

# +
def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        raise ValueError("Zero-length vector.")
    return v / n


def _normal_basis(tangent: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    t = _unit(tangent)
    ref = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(t, ref)) > 0.90:
        ref = np.array([0.0, 1.0, 0.0])
    n1 = _unit(np.cross(t, ref))
    n2 = _unit(np.cross(t, n1))
    return n1, n2


def _rotate_about_axis(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    """Rotate vector ``v`` around unit ``axis`` by ``angle`` (rad)."""
    c, s = math.cos(angle), math.sin(angle)
    return v * c + np.cross(axis, v) * s + axis * np.dot(axis, v) * (1.0 - c)


def _transport_normal_basis(
    t_prev: np.ndarray,
    t_next: np.ndarray,
    n1_prev: np.ndarray,
    n2_prev: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Parallel-transport local normals from ``t_prev`` to ``t_next``."""
    a = _unit(t_prev)
    b = _unit(t_next)
    cross = np.cross(a, b)
    s = float(np.linalg.norm(cross))
    c = float(np.dot(a, b))

    if s < 1e-12:
        if c > 0.0:
            n1, n2 = n1_prev, n2_prev
        else:
            # 180-degree turn: rebuild and align with previous orientation.
            n1, n2 = _normal_basis(b)
            if float(np.dot(n1, n1_prev)) < 0.0:
                n1, n2 = -n1, -n2
    else:
        axis = cross / s
        angle = math.atan2(s, c)
        n1 = _rotate_about_axis(n1_prev, axis, angle)
        n2 = _rotate_about_axis(n2_prev, axis, angle)

    n1 = n1 - float(np.dot(n1, b)) * b
    n1 = _unit(n1)
    n2 = _unit(np.cross(b, n1))
    return n1, n2


def _route_point_frames(
    route_points: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-route-point tangent and transported local basis."""
    pts = np.asarray(route_points, dtype=float)
    if len(pts) < 2:
        raise ValueError("Route must contain at least two points.")

    seg_tangents = np.array([_unit(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)])
    point_tangents = np.zeros_like(pts)
    point_tangents[0] = seg_tangents[0]
    point_tangents[-1] = seg_tangents[-1]
    for i in range(1, len(pts) - 1):
        t_sum = seg_tangents[i - 1] + seg_tangents[i]
        point_tangents[i] = _unit(t_sum) if np.linalg.norm(t_sum) > 1e-12 else seg_tangents[i]

    n1_pts = np.zeros_like(pts)
    n2_pts = np.zeros_like(pts)
    n1, n2 = _normal_basis(point_tangents[0])
    n1_pts[0], n2_pts[0] = n1, n2
    for i in range(1, len(pts)):
        n1, n2 = _transport_normal_basis(point_tangents[i - 1], point_tangents[i], n1, n2)
        n1_pts[i], n2_pts[i] = n1, n2
    return point_tangents, n1_pts, n2_pts


def _segment_basis_at_u(
    seg_tangent: np.ndarray,
    n1_start: np.ndarray,
    n1_end: np.ndarray,
    u: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Interpolate local basis along one segment at normalized position ``u``."""
    n1 = (1.0 - u) * n1_start + u * n1_end
    n1 = n1 - float(np.dot(n1, seg_tangent)) * seg_tangent
    if np.linalg.norm(n1) < 1e-12:
        n1, _ = _normal_basis(seg_tangent)
    else:
        n1 = _unit(n1)
    n2 = _unit(np.cross(seg_tangent, n1))
    return n1, n2


def _offset_route_points(
    route_points: np.ndarray,
    offset_xy: np.ndarray,
    n1_pts: np.ndarray,
    n2_pts: np.ndarray,
) -> np.ndarray:
    """Apply a cross-section offset [x_local, y_local] along the full route."""
    ox, oy = float(offset_xy[0]), float(offset_xy[1])
    pts = np.asarray(route_points, dtype=float)
    return np.array(
        [p + ox * n1 + oy * n2 for p, n1, n2 in zip(pts, n1_pts, n2_pts)]
    )


def _ensure_materials(hfss: Hfss, materials: dict[str, Any]) -> None:
    for name, props in materials.items():
        mat = (
            hfss.materials[name]
            if name in hfss.materials.material_keys
            else hfss.materials.add_material(name)
        )
        if "conductivity" in props:
            mat.conductivity = props["conductivity"]
        if "relative_permittivity" in props:
            mat.permittivity = props["relative_permittivity"]
        if "loss_tangent" in props:
            mat.dielectric_loss_tangent = props["loss_tangent"]


def _twisted_centerline(
    route_points: np.ndarray,
    pair_center_xy: np.ndarray,
    n1_pts: np.ndarray,
    n2_pts: np.ndarray,
    radius: float,
    pitch: float,
    phase: float,
    samples_per_pitch: int = 12,
) -> np.ndarray:
    """Helical centerline along a piecewise-linear route with transported frame."""
    cx, cy = float(pair_center_xy[0]), float(pair_center_xy[1])
    out, s_acc = [], 0.0
    for i in range(len(route_points) - 1):
        p0, p1 = route_points[i], route_points[i + 1]
        seg = p1 - p0
        L = float(np.linalg.norm(seg))
        seg_tangent = _unit(seg)
        n = max(2, int(samples_per_pitch * L / pitch))
        for j in range(n):
            if i > 0 and j == 0:
                continue
            u = j / (n - 1)
            s = s_acc + u * L
            th = 2.0 * math.pi * s / pitch + phase
            base = p0 + u * seg
            n1, n2 = _segment_basis_at_u(seg_tangent, n1_pts[i], n1_pts[i + 1], u)
            pair_offset = cx * n1 + cy * n2
            twist_offset = radius * math.cos(th) * n1 + radius * math.sin(th) * n2
            out.append(base + pair_offset + twist_offset)
        s_acc += L
    return np.array(out)


def _create_faceted_sweep(
    hfss: Hfss,
    path_points: np.ndarray,
    radius: float,
    facets: int,
    name: str,
    material: str | None,
    *,
    closed_solid: bool,
):
    """Sweep a regular polygon along a 3D polyline. Solid if ``closed_solid``."""
    start = path_points[0]
    tangent = _unit(path_points[1] - path_points[0])
    n1, n2 = _normal_basis(tangent)

    profile_pts = [
        (start
         + radius * math.cos(2 * math.pi * i / facets) * n1
         + radius * math.sin(2 * math.pi * i / facets) * n2).tolist()
        for i in range(facets)
    ]

    profile = hfss.modeler.create_polyline(
        points=profile_pts + [profile_pts[0]],
        name=f"{name}_profile",
        close_surface=closed_solid,
        cover_surface=closed_solid,
        material=material if closed_solid else None,
    )
    path = hfss.modeler.create_polyline(
        points=path_points.tolist(), name=f"{name}_path"
    )
    hfss.modeler.sweep_along_path(profile, path)
    profile.name = name
    if material and closed_solid:
        profile.material_name = material
    return profile

def _end_face_of(obj, target_point: np.ndarray):
    """Return the face of `obj` whose centroid is closest to `target_point`."""
    target = np.asarray(target_point, dtype=float)
    return min(
        obj.faces,
        key=lambda f: float(np.linalg.norm(np.array(f.center) - target)),
    )

def _nearest_edge(edges, target_point: np.ndarray):
    """Return the edge whose midpoint is closest to `target_point`."""
    target = np.asarray(target_point, dtype=float)
    return min(
        edges,
        key=lambda e: float(np.linalg.norm(np.array(e.midpoint) - target)),
    )

def find_pin(component, *needles: str):
    """
    Return the first pin whose name contains every substring in `needles`.
    Raises a clear LookupError listing all available pins if nothing matches.
    """
    for p in component.pins:
        if all(n in p.name for n in needles):
            return p
    available = ", ".join(repr(p.name) for p in component.pins)
    raise LookupError(
        f"No pin on {component.name!r} matches all of {needles!r}.\n"
        f"Available pins: {available}"
    )


def _pin_xy(pin) -> np.ndarray:
    return np.asarray(pin.location, dtype=float)


def _nearest_component_pin(component, target_point: np.ndarray):
    target = np.asarray(target_point, dtype=float)
    return min(
        component.pins,
        key=lambda p: float(np.linalg.norm(_pin_xy(p) - target)),
    )


def _other_two_pin(component, pin):
    pins = list(component.pins)
    if len(pins) == 2:
        pin_name = getattr(pin, "name", None)
        if pin_name == pins[0].name:
            return pins[1]
        if pin_name == pins[1].name:
            return pins[0]
        target = _pin_xy(pin)
        d0 = float(np.linalg.norm(_pin_xy(pins[0]) - target))
        d1 = float(np.linalg.norm(_pin_xy(pins[1]) - target))
        return pins[1] if d0 <= d1 else pins[0]
    raise ValueError(f"{component.name!r} does not appear to be a two-pin component.")


def _extend_route_ends(route_pts: np.ndarray, extension: float) -> np.ndarray:
    """Extend the polyline by `extension` (model units) at both ends along the
    tangent of the first and last segments."""
    pts = np.asarray(route_pts, dtype=float).copy()
    head_tan = _unit(pts[1]  - pts[0])
    tail_tan = _unit(pts[-1] - pts[-2])
    pts[0]  = pts[0]  - extension * head_tan
    pts[-1] = pts[-1] + extension * tail_tan
    return pts

def _check_pair_shield_interference(xsec, pair_shield_r, tol=1e-6):
    """Raise if any two pair-shield tubes overlap."""
    locs = {name: np.array(d["center"], dtype=float)
            for name, d in xsec["pair_locations"].items()}
    names = list(locs)
    issues = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = float(np.linalg.norm(locs[a] - locs[b]))
            min_d = 2.0 * pair_shield_r
            if d + tol < min_d:
                issues.append(
                    f"  {a} <-> {b}: distance={d:.3f} mm, "
                    f"required >= {min_d:.3f} mm  (overlap {min_d - d:.3f} mm)"
                )
    if issues:
        raise ValueError(
            "Pair-shield interference detected:\n" + "\n".join(issues) +
            "\nReduce 'geometry.pair_shield_radius' or spread "
            "'cross_section.pair_locations'."
        )
def _create_zt_dataset(hfss, name: str, freqs_hz: list[float],
                      r_ohm_sq: list[float]) -> str:
    hfss.create_dataset(
        name, freqs_hz, r_ohm_sq,
        is_project_dataset=False, x_unit="Hz", y_unit="ohm",
    )
    return name


def _assign_transfer_impedance(hfss, sheet_name, ds_name, name):
    """Frequency-dependent impedance boundary on a sheet."""
    return hfss.assign_impedance_to_sheet(
        sheet_name,
        name=name,
        resistance=f"pwl({ds_name}, Freq)",
        reactance=0,
    )
# -

# ## Register materials and resolve the active route

_ensure_materials(hfss, cfg.get("materials", {}))

route_name = next(iter(cfg["routes"]))
route_pts = np.array(cfg["routes"][route_name]["points"], dtype=float)
_, route_n1_pts, route_n2_pts = _route_point_frames(route_pts)

# ## Build the conductors, insulation and pair shields
#
# Each twisted pair is built as two helical solid conductors (copper) wrapped
# in a faceted insulation tube (PE foam). A faceted **sheet** tube around the
# pair represents the foil shield and later receives a Perfect-E boundary.

# +
conductors  = cfg["conductors"]
ins_def     = cfg["insulation"]["wire_insulation"]
pairs       = cfg["pairs"]
xsec        = cfg["cross_section"]
bundle_def  = cfg["bundle"]["ethernet_cat6a_sstp"]

wire_ins_r       = float(ins_def["outer_radius"])
pair_wire_r      = float(GEOM["pair_wire_center_offset"])
pair_shield_r    = float(GEOM["pair_shield_radius"])
overall_shield_r = float(GEOM["overall_shield_radius"])
jacket_r         = float(bundle_def["jacket"]["outer_radius"])

_check_pair_shield_interference(xsec, pair_shield_r)  # Make sure there are no collisions.

created: dict[str, list[str]] = {
    "conductors": [], "insulation": [], "pair_shields": [],
    "overall_shield": [], "jacket": [], "boundaries": [], "ports": [],
}

# --- YAML-driven end extension and PMC assignment -----------------------------
# Recommended margin: a few × the radial gap between the wires and the tube ID.
END_EXTENSION = float(
    GEOM.get("tube_end_extension",
             5.0 * max(overall_shield_r - wire_ins_r, 1.0))
)

extended_route = _extend_route_ends(route_pts, END_EXTENSION)  # Clearance to avoid short-circuiting wires.

# Map "conductor name" -> stored centerline (used later to position ports).
conductor_paths: dict[str, np.ndarray] = {}
freqs_hz = np.logspace(3, 10, 71)

for pair_name, pair_def in pairs.items():
    cx, cy = xsec["pair_locations"][pair_name]["center"]
    pair_center_xy = np.array([cx, cy], dtype=float)
    twist_pitch = float(pair_def["twist_pitch"])
    for idx, cname in enumerate(pair_def["members"]):
        phase = 0.0 if idx == 0 else math.pi
        centerline = _twisted_centerline(
            route_pts, pair_center_xy, route_n1_pts, route_n2_pts,
            radius=pair_wire_r, pitch=twist_pitch, phase=phase,
            samples_per_pitch=SAMPLES_PER_PITCH,
        )
        conductor_paths[cname] = centerline

        cond_r = float(conductors[cname].get("conductor_equivalent_radius") or
                        conductors[cname].get("conductor_radius", 0.227)
                    )

        cu = _create_faceted_sweep(
            hfss, centerline, cond_r, FACETS,
            name=f"cat6a_{cname}_cu", material="copper",
            closed_solid=True,
        )
        created["conductors"].append(cu.name)

        ins = _create_faceted_sweep(
            hfss, centerline, wire_ins_r, FACETS,
            name=f"cat6a_{cname}_ins",
            material=ins_def.get("material", "pe_foam"),
            closed_solid=True,
        )
        created["insulation"].append(ins.name)

    # Foil shield around the pair (sheet, not solid).
    shield_path = _offset_route_points(
        route_pts,
        pair_center_xy,
        route_n1_pts,
        route_n2_pts,
    )
    sh = _create_faceted_sweep(
        hfss, shield_path, pair_shield_r, FACETS,
        name=f"cat6a_{pair_name}_foil_shield",
        material=None, closed_solid=False,
    )
    created["pair_shields"].append(sh.name)


# --- Per-pair foil shields ---
for pair_name, pair_def in pairs.items():
    sh = pair_def["shield"]
    sigma = float(cfg["materials"][sh["material"]]["conductivity"])

    foil = ti.FoilShield(
        sigma=sigma,
        thickness_m=float(sh["thickness"]) * 1e-3,            # mm -> m
        cable_radius_m=pair_shield_r * 1e-3,
        seam_inductance_h_per_m=float(
            sh.get("construction", {}).get("seam_inductance", 1.0e-9)
        ),
    )
    zt = foil.transfer_impedance(freqs_hz)
    ti.report_zt(f"foil ({pair_name})", zt, freqs_hz)

    ds = _create_zt_dataset(
        hfss, f"ZT_{pair_name}", freqs_hz.tolist(), np.abs(zt).tolist()
    )
    created["boundaries"].append(
        _assign_transfer_impedance(
            hfss, f"cat6a_{pair_name}_foil_shield", ds, name=f"Zt_{pair_name}"
        ).name
    )

# --- Overall braid ---
ob = bundle_def["overall_shield"]
sigma_braid = float(cfg["materials"][ob["material"]]["conductivity"])
braid_mdl = ti.BraidShield(
    sigma=sigma_braid,
    wire_diameter_m=float(ob["construction"]["wire_diameter"]) * 1e-3,
    carriers=int(ob["construction"]["carriers"]),
    wires_per_carrier=int(ob["construction"]["wires_per_carrier"]),
    weave_angle_deg=float(ob["construction"]["weave_angle"]),
    cable_radius_m=overall_shield_r * 1e-3,
)

# -

# ## Overall braid shield and PVC jacket

# +

braid = _create_faceted_sweep(
    hfss, extended_route, overall_shield_r, FACETS,
    name="cat6a_overall_braid", material=None, closed_solid=False,
)
created["overall_shield"].append(braid.name)

zt_braid = braid_mdl.transfer_impedance(freqs_hz)

print(f"  Computed optical coverage:  {braid_mdl.optical_coverage:.3f}")
print(f"  Computed DC resistance:     {braid_mdl.dc_resistance_per_m*1e3:.3f} mOhm/m")
ti.report_zt("overall braid", zt_braid, freqs_hz)

ds = _create_zt_dataset(
    hfss, "ZT_overall_braid", freqs_hz.tolist(), np.abs(zt_braid).tolist()
)
created["boundaries"].append(
    _assign_transfer_impedance(hfss, braid.name, ds, name="Zt_overall_braid").name
)
jacket = _create_faceted_sweep(
    hfss, extended_route, jacket_r, FACETS,
    name="cat6a_pvc_jacket",
    material=bundle_def["jacket"].get("material", "pvc"),
    closed_solid=True,
)
created["jacket"].append(jacket.name)

for obj in (braid, jacket):
    obj.transparency = 0.8
    obj.color = LIGHT_GREY

# -

# ## Create lumped ports at both ends of every conductor
#
# Each conductor receives a lumped port between its end face and the chosen
# reference (the overall braid shield by default). The reference object is
# resolved once and re-used for every port.

# +


PORT_Z0 = float(PORT_CFG.get("impedance", 50))
ref_name = (
    braid.name
    if PORT_CFG.get("reference", "overall_shield") == "overall_shield"
    else "ground_plane"
)
ref_obj = hfss.modeler[ref_name]

port_pairs: dict[str, tuple[str, str]] = {}

for cname, centerline in conductor_paths.items():
    cond_obj = hfss.modeler[f"cat6a_{cname}_cu"]

    for end_idx, label in ((0, "in"), (-1, "out")):
        target = np.asarray(centerline[end_idx], dtype=float)

        # Signal edge: pick the conductor's end face, then any edge of it.
        cond_face = _end_face_of(cond_obj, target)
        cond_edge = cond_face.edges[0]

        # Reference edge: braid is a sheet tube, its "end" is an edge loop —
        # search edges directly rather than faces.
        ref_edge = _nearest_edge(ref_obj.edges, target)

        port_name = f"P_{cname}_{label}"
        hfss.circuit_port(
            assignment=cond_edge,        # positive terminal
            reference=ref_edge,          # negative terminal
            impedance=PORT_Z0,
            name=port_name,
            renormalize=True,
            renorm_impedance=str(PORT_Z0),
        )
        created["ports"].append(port_name)

    port_pairs[cname] = (f"P_{cname}_in", f"P_{cname}_out")

# -

# > **Note on ports.** Lumped ports on faceted 3D conductors typically need
# > a small rectangular cap sheet between the conductor end and the reference.
# > The call above asks PyAEDT to auto-build that sheet; on some geometries
# > you may have to create the cap explicitly with ``modeler.create_rectangle``
# > and pass it to ``hfss.lumped_port(assignment=cap, ...)``. The rest of the
# > workflow is unchanged.

# ## HFSS solution setup (frequency-domain S-parameter extraction)
#
# The transient analysis happens in Circuit, so HFSS only needs a broadband
# S-parameter sweep. The bandwidth comes from the YAML ``simulation.frequency_range``.

# +

fmin = float(SIM["frequency_range"]["start"])
fmax = float(SIM["frequency_range"]["stop"])

setup = hfss.create_setup(
    name="Sparam",
    Frequency=f"{fmax/2:.3e}Hz",
    MaximumPasses=8,
    MinimumConvergedPasses=1,
    DeltaS=0.02,
)
setup.create_frequency_sweep(
    unit="Hz",
    name="Broadband",
    start_frequency=fmin,
    stop_frequency=fmax,
    num_of_freq_points=401,
    sweep_type="Interpolating",
)

hfss.save_project()

# Uncomment to solve. Meshing a multi-conductor cable can take a long time.
# hfss.analyze()
# -

# ## Build the Circuit (Nexxim) schematic for the EFT transient run
#
# A Circuit design is added to the same project, the HFSS design is dropped
# in as a dynamic-link N-port, then a PWL voltage source and resistive
# terminations are wired up exactly as the YAML describes.

# +
circuit = Circuit(
    project=hfss.project_name,
    design="CAT6A_EFT_TRAN",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=False,
)
circuit.modeler.schematic_units = "mil"

# Drop the HFSS design in as a dynamic link sub-circuit.

nport = circuit.modeler.schematic.add_subcircuit_dynamic_link(
    pyaedt_app=hfss,
    solution_name="Sparam : Broadband",
    name="CAT6A_3D_link",
)
nport.location = [4000.0, 2500.0]

print("Dynamic-link pins:")
for p in nport.pins:
    print(f"  {p.name!r}")

# -

# ### Source end - EFT PWL on the driven conductor, matched loads on the rest

# +
driven = TERM_CFG["driven_conductor"]
src_imp = float(TRANSIENT_SOURCE_CFG["source_impedance"])
default_z = float(TERM_CFG.get("other_conductors_default", 50.0))
PIN_BRANCH_DX = 700.0
SOURCE_BRANCH_DX = 1300.0
GND_DY = -250.0

# PWL voltage source: zip the time/amplitude lists from YAML.
pwl_t = TRANSIENT_SOURCE_CFG["time"]
pwl_v = TRANSIENT_SOURCE_CFG["amplitude"]
pwl_pairs = list(zip(pwl_t, pwl_v))

driven_in_pin  = find_pin(nport, driven, "in")
in_pins = [find_pin(nport, cname, "in") for cname in port_pairs]
out_pins = [find_pin(nport, cname, "out") for cname in port_pairs]
_in_pin_x = {cname: _pin_xy(in_pins[i])[0] for i, cname in enumerate(port_pairs)}
_out_pin_x = {cname: _pin_xy(out_pins[i])[0] for i, cname in enumerate(port_pairs)}
pin_split_x = float(np.mean(list(_in_pin_x.values()) + list(_out_pin_x.values())))
in_side_sign = {cname: (-1.0 if _in_pin_x[cname] <= pin_split_x else 1.0) for cname in port_pairs}
out_side_sign = {cname: (-1.0 if _out_pin_x[cname] <= pin_split_x else 1.0) for cname in port_pairs}

# Stagger components away from the dynamic link so rows at different y-positions
# don't land on the same x-column. Lower rows (smaller y) get a larger offset.
# Ranking is performed independently on each side (left/right).
STAGGER_DX = 300.0  # mil per rank step
_in_pin_y  = {cname: _pin_xy(in_pins[i])[1]  for i, cname in enumerate(port_pairs)}
_out_pin_y = {cname: _pin_xy(out_pins[i])[1]  for i, cname in enumerate(port_pairs)}
in_stagger = {}
out_stagger = {}
for side in (-1.0, 1.0):
    _in_sorted = sorted((c for c in port_pairs if in_side_sign[c] == side), key=lambda c: _in_pin_y[c], reverse=True)
    _out_sorted = sorted((c for c in port_pairs if out_side_sign[c] == side), key=lambda c: _out_pin_y[c], reverse=True)
    for rank, cname in enumerate(_in_sorted):
        in_stagger[cname] = rank * STAGGER_DX
    for rank, cname in enumerate(_out_sorted):
        out_stagger[cname] = rank * STAGGER_DX

driven_in_xy = _pin_xy(driven_in_pin)
r_src = circuit.modeler.schematic.create_resistor(
    name="R_src",
    value=f"{src_imp}ohm",
    location=[driven_in_xy[0] + in_side_sign[driven] * (PIN_BRANCH_DX + in_stagger[driven]), driven_in_xy[1]],
)
eft_src = circuit.modeler.schematic.create_voltage_pwl(
    name="V_EFT",
    time_list=[t for t, _ in pwl_pairs],
    voltage_list=[v for _, v in pwl_pairs],
    location=[driven_in_xy[0] + in_side_sign[driven] * (SOURCE_BRANCH_DX + in_stagger[driven]), driven_in_xy[1]],
)

r_to_nport = _nearest_component_pin(r_src, driven_in_xy)
r_to_source = _other_two_pin(r_src, r_to_nport)
src_to_res = _nearest_component_pin(eft_src, _pin_xy(r_to_source))
src_return = _other_two_pin(eft_src, src_to_res)

# Wire dynamic-link driven input -> R_src -> EFT source; ground source return.
driven_in_pin.connect_to_component(assignment=r_to_nport, use_wire=True)
r_to_source.connect_to_component(assignment=src_to_res, use_wire=True)
gnd_src = circuit.modeler.schematic.create_gnd(
    location=[src_return.location[0], src_return.location[1] + GND_DY]
)
src_return.connect_to_component(assignment=gnd_src.pins[0], use_wire=True)

# Matched terminations on every other input pin.
for cname in port_pairs:
    if cname == driven:
        continue

    pin = find_pin(nport, f"P_{cname}_in")     # substring match → tolerates "_T1"
    pin_xy = _pin_xy(pin)
    r = circuit.modeler.schematic.create_resistor(
        name=f"R_in_{cname}", value=f"{default_z}ohm",
        location=[pin_xy[0] + in_side_sign[cname] * (PIN_BRANCH_DX + in_stagger[cname]), pin_xy[1]],
        angle=90,
    )
    r_to_pin = _nearest_component_pin(r, pin_xy)
    r_to_gnd = _other_two_pin(r, r_to_pin)
    pin.connect_to_component(assignment=r_to_pin, use_wire=True)
    gnd = circuit.modeler.schematic.create_gnd(
        location=[r_to_gnd.location[0], r_to_gnd.location[1] + GND_DY]
    )
    r_to_gnd.connect_to_component(assignment=gnd.pins[0], use_wire=True)

# -

# ### Load end - user-specified loads, defaults for the rest

# +
load_map = TERM_CFG.get("load_end", {}) or {}

for cname in port_pairs:
    z = float(load_map.get(cname, default_z))
    pin = find_pin(nport, f"P_{cname}_out")
    pin_xy = _pin_xy(pin)
    r = circuit.modeler.schematic.create_resistor(
        name=f"R_out_{cname}", value=f"{z}ohm",
        location=[pin_xy[0] + out_side_sign[cname] * (PIN_BRANCH_DX + out_stagger[cname]), pin_xy[1]],
        angle=90,
    )
    r_to_pin = _nearest_component_pin(r, pin_xy)
    r_to_gnd = _other_two_pin(r, r_to_pin)
    pin.connect_to_component(assignment=r_to_pin, use_wire=True)
    gnd = circuit.modeler.schematic.create_gnd(
        location=[r_to_gnd.location[0], r_to_gnd.location[1] + GND_DY]
    )
    r_to_gnd.connect_to_component(assignment=gnd.pins[0], use_wire=True)

# -

# ### Transient analysis setup

# +
tran_setup = circuit.create_setup(
    name="EFT_Transient",
    setup_type="NexximTransient",
)
tran_setup.props["TransientData"] = (
    f"{TRAN_CFG['time_step']}s",
    f"{TRAN_CFG['stop_time']}s",
)
tran_setup.props["MinStepSize"] = f"{TRAN_CFG['initial_step']}s"
tran_setup.update()

# Uncomment to run once the HFSS solve has produced the S-parameter file.
# circuit.analyze()
# -

# ## Save and release

# +
circuit.save_project()
circuit.release_desktop(close_projects=False, close_desktop=True)
time.sleep(3)
# -

# ## Clean up the temporary directory

temp_folder.cleanup()