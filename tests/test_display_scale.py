"""Display-policy regressions; no live monitor changes or extra packages."""
import pathlib
import runpy
import unittest

scale_updates = runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1] /
                                  "desktop/.local/bin/vm-display-scale"))["scale_updates"]


def monitor(height, scale, **overrides):
    data = dict(name="Virtual-1", width=3840, height=height, scale=scale,
                refreshRate=60, x=0, y=0)
    return data | overrides


class DisplayScaleTests(unittest.TestCase):
    def test_no_change_when_already_correct(self):
        self.assertEqual(list(scale_updates([monitor(2160, 2)])), [])

    def test_smaller_resolution_returns_to_one(self):
        update, = scale_updates([monitor(1440, 2, width=2560)])
        self.assertEqual(update["scale"], 1)
        self.assertEqual(update["mode"], "2560x1440@60.00000")

    def test_retina_threshold_preserves_layout(self):
        update, = scale_updates([monitor(1800, 1, x=-100, y=20, transform=2)])
        self.assertEqual(update["scale"], 2)
        self.assertEqual(update["position"], "-100x20")
        self.assertEqual(update["transform"], 2)

    def test_odd_dimensions_fall_back_without_invalid_scale(self):
        self.assertEqual(list(scale_updates([monitor(2161, 1)])), [])
        update, = scale_updates([monitor(2160, 2, width=3839)])
        self.assertEqual(update["scale"], 1)

    def test_physical_or_disabled_outputs_are_untouched(self):
        outputs = [monitor(2160, 1, name="DP-1"), monitor(2160, 1, disabled=True)]
        self.assertEqual(list(scale_updates(outputs)), [])


if __name__ == "__main__":
    unittest.main()
