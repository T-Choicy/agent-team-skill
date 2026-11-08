"""Velocity Verlet for a dimensionless harmonic oscillator."""

import math


def solve(dt, steps):
    """Solve x''=-x with x(0)=1, v(0)=0 using velocity Verlet.

    dt must be a built-in int or float (excluding bool), finite and 0<dt<2.
    steps must be a nonnegative built-in int (excluding bool). Invalid types
    raise TypeError; invalid values raise ValueError before integration.
    Return steps+1 (t, x, v) tuples, including the initial state, with t=n*dt.
    Time and memory use are O(steps).
    """
    if type(dt) not in (int, float):
        raise TypeError("dt must be a built-in int or float")
    if not 0 < dt < 2 or not math.isfinite(dt):
        raise ValueError("dt must be finite and satisfy 0 < dt < 2")
    if type(steps) is not int:
        raise TypeError("steps must be a built-in int")
    if steps < 0:
        raise ValueError("steps must be nonnegative")

    x, v = 1.0, 0.0
    samples = [(0.0, x, v)]
    for n in range(1, steps + 1):
        x_new = x + dt * v - 0.5 * dt * dt * x
        v = v - 0.5 * dt * (x + x_new)
        x = x_new
        samples.append((n * dt, x, v))
    return samples
