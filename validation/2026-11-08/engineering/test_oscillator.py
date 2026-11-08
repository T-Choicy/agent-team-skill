import math
import unittest
from decimal import Decimal

from oscillator import solve


class OscillatorTests(unittest.TestCase):
    def test_zero_steps(self):
        self.assertEqual(solve(0.1, 0), [(0.0, 1.0, 0.0)])

    def test_one_step(self):
        samples = solve(0.1, 1)
        self.assertEqual(len(samples), 2)
        self.assertEqual(samples[0], (0.0, 1.0, 0.0))
        t, x, v = samples[1]
        self.assertEqual(t, 0.1)
        self.assertAlmostEqual(x, 0.995, delta=1e-14)
        self.assertAlmostEqual(v, -0.09975, delta=1e-14)

    def test_analytic_trajectory_and_times(self):
        h = 0.1
        samples = solve(h, 100)
        self.assertEqual(len(samples), 101)
        for n, (t, x, v) in enumerate(samples):
            self.assertEqual(t, n * h)
        self.assertLess(max(abs(x - math.cos(t)) for t, x, v in samples), 0.01)
        self.assertLess(max(abs(v + math.sin(t)) for t, x, v in samples), 0.01)

    def test_finite_duration_energy_bound(self):
        h = 0.1
        for t, x, v in solve(h, 20000):
            energy = 0.5 * (x * x + v * v)
            self.assertGreaterEqual(energy, 0.5 - h * h / 8 - 1e-10)
            self.assertLessEqual(energy, 0.5 + 1e-10)

    def test_second_order_endpoint_convergence(self):
        errors = []
        for h, steps in ((0.2, 50), (0.1, 100), (0.05, 200)):
            t, x, v = solve(h, steps)[-1]
            self.assertEqual(t, 10.0)
            errors.append(math.hypot(x - math.cos(10), v + math.sin(10)))
        for error in errors:
            self.assertGreater(error, 0)
        for coarse, fine in zip(errors, errors[1:]):
            self.assertGreater(coarse, fine)
            self.assertGreaterEqual(coarse / fine, 3.5)
            self.assertLessEqual(coarse / fine, 4.5)

    def test_invalid_inputs(self):
        for dt in (True, "0.1", None, 0.1j, Decimal("0.1")):
            with self.subTest(dt=dt):
                with self.assertRaises(TypeError):
                    solve(dt, 1)
        for dt in (0, -0.1, 2, 3, float("nan"), float("inf"), -float("inf")):
            with self.subTest(dt=dt):
                with self.assertRaises(ValueError):
                    solve(dt, 1)
        for steps in (True, 1.0, "1", None):
            with self.subTest(steps=steps):
                with self.assertRaises(TypeError):
                    solve(0.1, steps)
        with self.assertRaises(ValueError):
            solve(0.1, -1)

    def test_integer_dt(self):
        self.assertEqual(solve(1, 1), [(0.0, 1.0, 0.0), (1, 0.5, -0.75)])


if __name__ == "__main__":
    unittest.main()
