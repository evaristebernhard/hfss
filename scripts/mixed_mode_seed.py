#!/usr/bin/env python3
"""Small mixed-mode algebra helper for the four-way magic-tee tree."""

from __future__ import annotations

import numpy as np


U = 0.5 * np.array(
    [
        [1.0, 1.0, 1.0, 1.0],
        [np.sqrt(2.0), -np.sqrt(2.0), 0.0, 0.0],
        [0.0, 0.0, np.sqrt(2.0), -np.sqrt(2.0)],
        [1.0, 1.0, -1.0, -1.0],
    ],
    dtype=complex,
)


def modal_to_port_reflection(gamma_modes):
    """
    gamma_modes = [Gamma_Sigma, Gamma_Delta1, Gamma_Delta2, Gamma_Delta3]
    returns the 4x4 port reflection/coupling block.
    """
    gm = np.asarray(gamma_modes, dtype=complex)
    if gm.shape != (4,):
        raise ValueError("gamma_modes must contain exactly four values")
    return U.conj().T @ np.diag(gm) @ U


def combining_efficiency(a):
    """Ideal lossless coherent-combining efficiency for four inputs."""
    a = np.asarray(a, dtype=complex)
    if a.shape != (4,):
        raise ValueError("a must contain exactly four complex input waves")
    denom = 4.0 * np.sum(np.abs(a) ** 2)
    if denom == 0.0:
        return 0.0
    return float(np.abs(np.sum(a)) ** 2 / denom)


def mode_amplitudes(a):
    a = np.asarray(a, dtype=complex)
    return U @ a


def main():
    print("U^H U =")
    print(np.round(U.conj().T @ U, 12))

    rho25 = 10.0 ** (-25.0 / 20.0)
    # Deliberately assign different phases to show that modal reflection
    # directly maps back into ordinary port reflection/coupling.
    gamma_modes = rho25 * np.exp(
        1j * np.deg2rad([0.0, 40.0, -65.0, 110.0])
    )
    rport = modal_to_port_reflection(gamma_modes)

    print("\nExample with every modal |Gamma| = -25 dB:")
    print("max |port reflection/coupling| =", np.max(np.abs(rport)))
    print("matrix magnitude =")
    print(np.round(np.abs(rport), 5))

    equal = np.ones(4, dtype=complex)
    print("\nEqual coherent inputs:")
    print("mode amplitudes =", np.round(mode_amplitudes(equal), 8))
    print("ideal combining efficiency =", combining_efficiency(equal))

    phase_error = np.exp(
        1j * np.deg2rad([0.0, 2.0, -2.0, 3.0])
    )
    print("\nExample small phase errors:")
    print("mode amplitudes =", np.round(mode_amplitudes(phase_error), 8))
    print("ideal combining efficiency =", combining_efficiency(phase_error))


if __name__ == "__main__":
    main()
