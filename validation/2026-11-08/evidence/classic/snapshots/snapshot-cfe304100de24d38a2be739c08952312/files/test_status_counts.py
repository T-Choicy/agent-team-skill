import unittest

from status_counts import tally_statuses


class TallyStatusesTests(unittest.TestCase):
    def test_empty(self):
        result = tally_statuses([])
        self.assertEqual(result, {"pending": 0, "running": 0, "done": 0, "failed": 0})
        self.assertEqual(list(result), ["pending", "running", "done", "failed"])
        self.assertIs(type(result), dict)

    def test_mixed(self):
        statuses = ["pending", "done", "running", "done", "pending", "failed", "done"]
        before = statuses.copy()
        self.assertEqual(
            tally_statuses(statuses),
            {"pending": 2, "running": 1, "done": 3, "failed": 1},
        )
        self.assertEqual(statuses, before)

    def test_missing_statuses(self):
        self.assertEqual(
            tally_statuses(["done", "done"]),
            {"pending": 0, "running": 0, "done": 2, "failed": 0},
        )

    def test_invalid_strings(self):
        for invalid in ["unknown", "", "Done", " done "]:
            with self.subTest(invalid=invalid):
                statuses = ["pending", invalid]
                before = statuses.copy()
                with self.assertRaisesRegex(ValueError, r"\[1\].*pending.*running.*done.*failed"):
                    tally_statuses(statuses)
                self.assertEqual(statuses, before)

    def test_invalid_elements(self):
        for invalid in [None, 1, True, [], {}]:
            with self.subTest(invalid=invalid):
                statuses = ["pending", invalid]
                before = statuses.copy()
                with self.assertRaisesRegex(TypeError, r"\[1\].*string"):
                    tally_statuses(statuses)
                self.assertEqual(statuses, before)

    def test_invalid_containers(self):
        for invalid in [None, "done", ("done",), {"done": 1}, iter(["done"])]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    tally_statuses(invalid)

    def test_first_invalid_entry_controls_error(self):
        with self.assertRaises(ValueError):
            tally_statuses(["done", "unknown", None])
        with self.assertRaises(TypeError):
            tally_statuses(["done", None, "unknown"])

    def test_subclasses(self):
        class StatusList(list):
            pass

        class StatusString(str):
            pass

        self.assertEqual(
            tally_statuses(StatusList([StatusString("running")])),
            {"pending": 0, "running": 1, "done": 0, "failed": 0},
        )

    def test_results_are_independent(self):
        statuses = ["done"]
        first = tally_statuses(statuses)
        first["done"] = 99
        second = tally_statuses(statuses)
        self.assertIsNot(first, second)
        self.assertEqual(second, {"pending": 0, "running": 0, "done": 1, "failed": 0})


if __name__ == "__main__":
    unittest.main()
