"""Native SPICE framing, resize validation, and clipboard relay regressions."""
import asyncio
import json
from pathlib import Path
import runpy
import struct
import unittest
from unittest.mock import patch

bridge = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                           'desktop/.local/bin/vm-spice-display-agent'))
HEADER = bridge['HEADER']


def config(width=2560, height=1440, count=16, flags=1):
    records = [struct.pack('=IIIii', height, width, 32, 0, 0)]
    records += [bytes(20)] * (count - 1)
    return struct.pack('=II', count, flags) + b''.join(records)


class ProtocolTests(unittest.TestCase):
    def test_sparse_utm_monitor_config(self):
        self.assertEqual(bridge['parse_layout'](config()), (2560, 1440, 0, 0))

    def test_non_sparse_config(self):
        self.assertEqual(bridge['parse_layout'](config(3456, 2160, 1)),
                         (3456, 2160, 0, 0))

    def test_rejects_truncated_oversized_unknown_flags(self):
        for payload in (b'', config()[:-1], config(width=99999), config(flags=8)):
            with self.assertRaises(ValueError):
                bridge['parse_layout'](payload)

    def test_multiple_active_monitors_rejected(self):
        payload = struct.pack('=II', 2, 1) + config(count=1)[8:] * 2
        with self.assertRaises(ValueError):
            bridge['parse_layout'](payload)

    def test_physical_size_extension(self):
        payload = config(count=1, flags=3) + struct.pack('=HH', 340, 600)
        self.assertEqual(bridge['parse_layout'](payload), (2560, 1440, 0, 0))

    def test_external_monitor_gets_one_and_retina_two(self):
        monitor = dict(name='Virtual-1', scale=2, refreshRate=60, x=0, y=0)
        rule, target = bridge['resize_rule'](monitor, (2560, 1440, 0, 0))
        self.assertEqual(target, (2560, 1440, 1))
        self.assertEqual(rule['mode'], '2560x1440@60.00000')
        monitor['scale'] = 1
        self.assertEqual(bridge['resize_rule'](monitor, (3456, 2160, 0, 0))[1],
                         (3456, 2160, 2))

    def test_retina_odd_window_keeps_scale_with_one_pixel_margin(self):
        monitor = dict(name='Virtual-1', scale=2, refreshRate=60, x=0, y=0)
        self.assertEqual(bridge['resize_rule'](monitor, (3001, 2001, 0, 0))[1],
                         (3000, 2000, 2))


class StreamTests(unittest.IsolatedAsyncioTestCase):
    async def test_fragmented_frame(self):
        reader = asyncio.StreamReader()
        packet = HEADER.pack(1, 0, 0, len(config())) + config()
        task = asyncio.create_task(bridge['read_frame'](reader))
        for byte in packet:
            reader.feed_data(bytes([byte]))
            await asyncio.sleep(0)
        kind, header, payload = await task
        self.assertEqual(kind, 1)
        self.assertEqual(payload, config())

    async def test_oversized_frame_rejected_before_reading_body(self):
        reader = asyncio.StreamReader()
        reader.feed_data(HEADER.pack(4, 0, 0, bridge['MAX_MESSAGE'] + 1))
        with self.assertRaises(ValueError):
            await bridge['read_frame'](reader)

    async def test_clipboard_bytes_pass_through_monitor_is_intercepted(self):
        class Writer:
            def __init__(self):
                self.data = b''
            def write(self, data):
                self.data += data
            async def drain(self):
                pass
        reader = asyncio.StreamReader()
        clipboard = HEADER.pack(4, 0, 1, 5) + b'hello'
        reader.feed_data(HEADER.pack(1, 0, 0, len(config())) + config() + clipboard)
        reader.feed_eof()
        writer = Writer()
        handler = bridge['ResizeHandler']()
        with self.assertRaises(asyncio.IncompleteReadError):
            await bridge['relay'](reader, writer, handler)
        self.assertEqual(writer.data, clipboard)
        self.assertEqual(handler.pending, (2560, 1440, 0, 0))

    async def test_burst_uses_latest_request_and_duplicate_is_noop(self):
        handler = bridge['ResizeHandler']()
        monitor = dict(name='Virtual-1', width=2560, height=1440, scale=1,
                       refreshRate=60, x=0, y=0)
        calls = []
        async def fake_command(*args):
            calls.append(args)
            return json.dumps([monitor]).encode()
        with patch.dict(bridge['ResizeHandler'].run.__globals__, command=fake_command):
            task = asyncio.create_task(handler.run())
            handler.request((3456, 2160, 0, 0))
            await asyncio.sleep(.05)
            handler.request((2560, 1440, 0, 0))
            await asyncio.sleep(1.1)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertEqual(calls, [('hyprctl', '-j', 'monitors')])

    async def test_verification_waits_for_async_mode_change_without_reapplying(self):
        handler = bridge['ResizeHandler']()
        monitor = dict(name='Virtual-1', width=3456, height=2160, scale=2,
                       refreshRate=60, x=0, y=0)
        calls = []
        reads = 0
        async def fake_command(*args):
            nonlocal reads
            calls.append(args)
            if args[1] == 'eval':
                return b'ok'
            reads += 1
            if reads >= 3:
                monitor.update(width=2560, height=1440, scale=1)
            return json.dumps([monitor]).encode()
        with patch.dict(bridge['ResizeHandler'].run.__globals__, command=fake_command):
            task = asyncio.create_task(handler.run())
            handler.request((2560, 1440, 0, 0))
            await asyncio.sleep(1.6)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertEqual(len([c for c in calls if c[1] == 'eval']), 1)
        self.assertEqual(reads, 3)


if __name__ == '__main__':
    unittest.main()
