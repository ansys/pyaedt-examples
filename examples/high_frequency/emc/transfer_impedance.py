"""
Closed-form transfer impedance models for cable shields.

References
----------
- Schelkunoff, "The electromagnetic theory of coaxial transmission lines and
  cylindrical shields," Bell Syst. Tech. J., 1934.
- Vance, "Shielding effectiveness of braided-wire shields," IEEE Trans. EMC,
  1975.
- Kley, "Optimized single-braided cable shields," IEEE Trans. EMC, 1993.
- Tesche, Ianoz, Karlsson, "EMC Analysis Methods and Computational Models,"
  Wiley, 1997 (Chapter 7).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

MU0 = 4.0e-7 * math.pi          # H/m
EPS = 1.0e-30                   # numerical floor


# --------------------------------------------------------------------------- #
# Common: skin-depth-corrected diffusion impedance of a thin conducting wall  #
# --------------------------------------------------------------------------- #
def _diffusion_impedance(
    sigma: float,
    thickness_m: float,
    freqs_hz: np.ndarray,
) -> np.ndarray:
    """
    Schelkunoff diffusion impedance of a thin conducting sheet, in ohm/square.

    Z_d(f) = R_dc * (gamma*t) / sinh(gamma*t),
    with gamma = (1 + j) / delta and delta = 1/sqrt(pi*f*mu0*sigma).
    """
    f = np.asarray(freqs_hz, dtype=float)
    r_dc = 1.0 / (sigma * thickness_m)                     # ohm/square at DC

    # At f = 0 the formula is indeterminate; force the DC limit.
    safe_f = np.where(f > 0, f, EPS)
    delta = 1.0 / np.sqrt(np.pi * safe_f * MU0 * sigma)    # skin depth, m
    gamma_t = (1.0 + 1.0j) * thickness_m / delta

    # sinh small-argument limit -> gamma_t, so Z_d -> R_dc.
    sinh_gt = np.sinh(gamma_t)
    z_d = r_dc * np.where(
        np.abs(gamma_t) < 1e-6,
        1.0 + 0.0j,
        gamma_t / sinh_gt,
    )
    return z_d


# --------------------------------------------------------------------------- #
# Foil shield with longitudinal seam                                          #
# --------------------------------------------------------------------------- #
@dataclass
class FoilShield:
    """Foil-tape shield (e.g. aluminium-polyester) with longitudinal seam."""

    sigma: float                  # S/m (foil material)
    thickness_m: float            # m (foil thickness)
    cable_radius_m: float         # m (radius of the foil tube)
    seam_inductance_h_per_m: float = 1.0e-9
    # Heuristic: 0.5–2 nH/m for a typical 1 mm longitudinal overlap.
    # Set to 0 for a perfectly seamless tube (idealised reference).

    def transfer_impedance(self, freqs_hz: np.ndarray) -> np.ndarray:
        """
        Z_t(f) of a thin foil tube with a longitudinal seam, in ohm/m.

        Z_t = Z_d(f) / (2*pi*r) + j*omega*L_seam

        where Z_d is the diffusion impedance per square and the geometric
        factor 1/(2*pi*r) converts ohm/square -> ohm/m for a closed tube of
        radius r.
        """
        f = np.asarray(freqs_hz, dtype=float)
        omega = 2.0 * np.pi * f

        z_d = _diffusion_impedance(self.sigma, self.thickness_m, f)
        circumference = 2.0 * np.pi * self.cable_radius_m
        z_diffusion = z_d / circumference

        z_seam = 1.0j * omega * self.seam_inductance_h_per_m
        return z_diffusion + z_seam


# --------------------------------------------------------------------------- #
# Braided wire shield (Vance / Kley simplified)                               #
# --------------------------------------------------------------------------- #
@dataclass
class BraidShield:
    """
    Single-layer braided wire shield.

    Geometry follows the standard braid convention:
        - ``carriers``       : number of carrier groups around the braid
        - ``wires_per_carrier``: strands within one carrier
        - ``wire_diameter_m`` : single-strand diameter
        - ``weave_angle_deg`` : angle of carriers measured FROM the cable axis
        - ``cable_radius_m``  : mean braid radius
    """

    sigma: float
    wire_diameter_m: float
    carriers: int
    wires_per_carrier: int
    weave_angle_deg: float
    cable_radius_m: float

    # ------------------------------------------------------------------ #
    # Derived braid geometry                                             #
    # ------------------------------------------------------------------ #
    @property
    def fill_factor(self) -> float:
        """Fraction of one half-shell covered by carriers in one direction."""
        alpha = math.radians(self.weave_angle_deg)
        n_c = self.carriers
        n_w = self.wires_per_carrier
        d = self.wire_diameter_m
        r = self.cable_radius_m
        # f = N * n * d / (2 * pi * r * cos(alpha))
        return (n_c * n_w * d) / (2.0 * math.pi * r * math.cos(alpha))

    @property
    def optical_coverage(self) -> float:
        """K = 2f - f**2, clipped to [0, 1]."""
        f = self.fill_factor
        return max(0.0, min(1.0, 2.0 * f - f * f))

    @property
    def dc_resistance_per_m(self) -> float:
        """
        DC resistance per metre of the *braid as a whole*, treating all
        carrier wires as parallel conductors of length L/cos(alpha).
        """
        alpha = math.radians(self.weave_angle_deg)
        a_wire = math.pi * (self.wire_diameter_m / 2.0) ** 2
        n_total = self.carriers * self.wires_per_carrier
        # Per-wire resistance per m of cable length:
        r_per_wire = 1.0 / (self.sigma * a_wire * math.cos(alpha))
        return r_per_wire / n_total

    # ------------------------------------------------------------------ #
    # Transfer impedance                                                 #
    # ------------------------------------------------------------------ #
    def _diffusion_term(self, freqs_hz: np.ndarray) -> np.ndarray:
        """
        Diffusion through the round braid wires, expressed as ohm/m of cable.

        Uses the same Schelkunoff form but with an effective wall thickness
        equal to the wire diameter and scaled by the braid DC resistance.
        """
        z_d_per_sq = _diffusion_impedance(
            self.sigma, self.wire_diameter_m, freqs_hz
        )
        # Normalise to per-metre using the braid DC resistance: at f -> 0
        # this returns exactly R_dc, then rolls off with skin effect.
        return self.dc_resistance_per_m * (z_d_per_sq / z_d_per_sq[0].real)

    def _aperture_inductance(self) -> float:
        """
        Vance aperture mutual inductance per metre, in H/m.

        M_12 ~ (mu0 / (pi * N_c)) * (1 - K)**(3/2) * tan(alpha)
        """
        alpha = math.radians(self.weave_angle_deg)
        k = self.optical_coverage
        leakage = (1.0 - k) ** 1.5
        return (MU0 / (math.pi * self.carriers)) * leakage * math.tan(alpha)

    def transfer_impedance(self, freqs_hz: np.ndarray) -> np.ndarray:
        """
        Z_t(f) of a single-braid shield, in ohm/m.

        Z_t(f) = Z_diffusion(f) + j*omega*M_12
        """
        f = np.asarray(freqs_hz, dtype=float)
        omega = 2.0 * np.pi * f
        return self._diffusion_term(f) + 1.0j * omega * self._aperture_inductance()


# --------------------------------------------------------------------------- #
# Sanity-check helper                                                         #
# --------------------------------------------------------------------------- #
def report_zt(name: str, zt: np.ndarray, freqs_hz: np.ndarray,
              checkpoints_hz=(1e3, 1e6, 1e8, 1e9)) -> None:
    """Print |Z_t| in mΩ/m at a few canonical frequencies."""
    print(f"\nTransfer impedance: {name}")
    for fc in checkpoints_hz:
        idx = int(np.argmin(np.abs(freqs_hz - fc)))
        f_actual = freqs_hz[idx]
        mag = abs(zt[idx]) * 1e3      # mΩ/m
        print(f"  f = {f_actual:>8.2e} Hz   |Z_t| = {mag:8.3f} mOhm/m")