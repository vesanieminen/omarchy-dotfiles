"""Display-policy regressions; no live monitor changes or extra packages."""
import pathlib
import runpy
import subprocess
import unittest

policy = runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1] /
                           "desktop/.local/bin/vm-display-scale"))
scale_updates = policy["scale_updates"]


def monitor(height, scale, **overrides):
    return dict(name="Virtual-1", width=3840, height=height, scale=scale,
                refreshRate=60, x=0, y=0) | overrides


def settle(samples):
    sequence = iter(samples)
    return policy["settled_monitors"](read=lambda: next(sequence), sleep=lambda _: None)


class DisplayScaleTests(unittest.TestCase):
    def test_no_change_when_already_correct(self):
        self.assertEqual(list(scale_updates([monitor(2160, 2)])), [])

    def test_smaller_resolution_returns_to_one(self):
        update, = scale_updates([monitor(1080, 2, width=1920)])
        self.assertEqual(update["scale"], 1)

    def test_hysteresis_holds_both_scales_near_old_boundary(self):
        for height in (1602, 1798, 1800, 1802, 1898):
            for scale in (1, 2):
                self.assertEqual(list(scale_updates([monitor(height, scale)])), [])
        self.assertEqual(list(scale_updates([monitor(1900, 1)]))[0]["scale"], 2)
        self.assertEqual(list(scale_updates([monitor(1600, 2)]))[0]["scale"], 1)

    def test_odd_dimensions_hold_both_scales(self):
        for scale in (1, 2):
            for output in (monitor(2161, scale), monitor(2160, scale, width=3839)):
                self.assertEqual(list(scale_updates([output])), [])

    def test_physical_disabled_sleeping_and_zero_outputs_are_untouched(self):
        outputs = [monitor(2160, 1, name="DP-1"), monitor(2160, 1, disabled=True),
                   monitor(2160, 1, dpmsStatus=False), monitor(0, 2),
                   monitor(2160, 1, width=0)]
        self.assertEqual(list(scale_updates(outputs)), [])

    def test_fullscreen_to_windowed_waits_for_final_size(self):
        fullscreen = [monitor(2160, 2)]
        odd = [monitor(1801, 2, width=3001)]
        windowed = [monitor(1080, 2, width=1920)]
        result = settle([fullscreen, odd, windowed, windowed, windowed])
        self.assertEqual(result, windowed)
        self.assertEqual(list(scale_updates(result))[0]["scale"], 1)

    def test_continuous_resize_is_deferred(self):
        self.assertEqual(settle([[monitor(1900 + 2 * i, 1)] for i in range(11)]), [])

    def test_focus_changes_do_not_restart_debounce(self):
        samples = [[monitor(2160, 1, focused=focus)] for focus in (True, False, True)]
        self.assertEqual(len(settle(samples)), 1)

    def test_resume_does_not_apply_sleeping_state(self):
        asleep = [monitor(2160, 1, dpmsStatus=False)]
        awake = [monitor(1080, 2, width=1920)]
        self.assertEqual(settle([asleep, awake, awake, awake]), awake)

    def test_stale_resize_is_guarded_and_layout_read_inside_compositor(self):
        update, = scale_updates([monitor(2160, 1)])
        code = policy["lua_update"](update)
        self.assertIn("m.width == 3840", code)
        self.assertIn("m.height == 2160", code)
        self.assertIn("m.scale == 1", code)
        self.assertIn("m.dpms_status", code)
        self.assertIn("m.refresh_rate", code)
        self.assertIn("m.x, m.y", code)


class CompositorRuleTests(unittest.TestCase):
    def lua(self, source):
        subprocess.run(["lua", "-"], input=source, text=True, check=True,
                       capture_output=True, timeout=3)

    def test_stale_resize_is_rejected_in_compositor(self):
        update, = scale_updates([monitor(2160, 1)])
        self.lua('''local calls = 0
hl = { get_monitor = function() return {width=1920,height=1080,scale=1,dpms_status=true} end,
       monitor = function() calls = calls + 1 end }
''' + policy["lua_update"](update) + "\nassert(calls == 0)")

    def test_apply_uses_live_refresh_position_and_transform(self):
        update, = scale_updates([monitor(2160, 1)])
        self.lua('''hl = {
  get_monitor = function() return {width=3840,height=2160,scale=1,dpms_status=true,
                                 refresh_rate=59.94,x=-200,y=30,transform=2} end,
  monitor = function(spec)
    assert(spec.mode == "3840x2160@59.94000")
    assert(spec.position == "-200x30" and spec.transform == 2 and spec.scale == 2)
    applied = true
  end }
''' + policy["lua_update"](update) + "\nassert(applied)")

    def config(self, monitors, assertions):
        path = pathlib.Path(__file__).resolve().parents[1] / "desktop/.config/hypr/monitors.lua"
        self.lua("local specs = {}\n" +
                 "hl = {env=function() end, on=function() end, " +
                 "get_monitors=function() return " + monitors + " end, " +
                 "monitor=function(spec) table.insert(specs,spec) end}\n" +
                 "dofile(" + repr(str(path)) + ")\n" + assertions)

    def test_cold_start_fits_macbook_utm_fullscreen(self):
        self.config("{}", 'assert(#specs == 2 and specs[2].mode == "3456x2160@60" and specs[2].scale == 2)')

    def test_reload_keeps_windowed_mode(self):
        self.config('{ {name="Virtual-1",width=1920,height=1080,refresh_rate=60,'
                    'x=0,y=0,scale=1,transform=0} }',
                    'assert(#specs == 2 and specs[2].mode == "1920x1080@60.00000" '
                    'and specs[2].scale == 1)')

    def test_physical_display_has_no_forced_virtual_rule(self):
        self.config('{ {name="DP-1",width=1920,height=1080} }', 'assert(#specs == 1)')


if __name__ == "__main__":
    unittest.main()
