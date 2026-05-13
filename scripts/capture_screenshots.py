# File version: 2.1; date: 2026-05-12

"""Capture Windows screenshots of the Tkinter app without external packages."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path
import struct
import sys
import zlib


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT / "docs" / "screenshots"
sys.path.insert(0, str(ROOT))

from intervention_sample_planner import StudyConfig  # noqa: E402
from intervention_sample_planner.gui import PlannerApp  # noqa: E402


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _write_png(path: Path, width: int, height: int, bgra: bytes) -> None:
    rows = []
    stride = width * 4
    for y in range(height):
        source = bgra[y * stride : (y + 1) * stride]
        rgb = bytearray()
        for x in range(width):
            base = x * 4
            blue, green, red = source[base], source[base + 1], source[base + 2]
            rgb.extend((red, green, blue))
        rows.append(b"\x00" + bytes(rgb))
    payload = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            _png_chunk(b"IDAT", zlib.compress(b"".join(rows), 9)),
            _png_chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(payload)


def _capture_window(hwnd: int, path: Path) -> None:
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32

    rect = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise RuntimeError("GetWindowRect failed.")
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    if width < 400 or height < 300:
        raise RuntimeError(f"Unexpected screenshot size {width}x{height}.")

    source_dc = user32.GetWindowDC(hwnd)
    memory_dc = gdi32.CreateCompatibleDC(source_dc)
    bitmap = gdi32.CreateCompatibleBitmap(source_dc, width, height)
    old_object = gdi32.SelectObject(memory_dc, bitmap)
    try:
        rendered = user32.PrintWindow(hwnd, memory_dc, 2)
        if not rendered:
            gdi32.BitBlt(memory_dc, 0, 0, width, height, source_dc, 0, 0, 0x00CC0020)

        bitmap_info = BITMAPINFO()
        bitmap_info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bitmap_info.bmiHeader.biWidth = width
        bitmap_info.bmiHeader.biHeight = -height
        bitmap_info.bmiHeader.biPlanes = 1
        bitmap_info.bmiHeader.biBitCount = 32
        bitmap_info.bmiHeader.biCompression = 0
        buffer = ctypes.create_string_buffer(width * height * 4)
        rows = gdi32.GetDIBits(
            memory_dc,
            bitmap,
            0,
            height,
            buffer,
            ctypes.byref(bitmap_info),
            0,
        )
        if rows != height:
            raise RuntimeError("GetDIBits failed.")
        _write_png(path, width, height, buffer.raw)
    finally:
        gdi32.SelectObject(memory_dc, old_object)
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(memory_dc)
        user32.ReleaseDC(hwnd, source_dc)


def _window_handle(app: PlannerApp) -> int:
    app.update_idletasks()
    app.update()
    return int(app.tk.call("wm", "frame", app._w), 0)


def _capture_app(path: Path, configure) -> None:
    app = PlannerApp()
    try:
        app.geometry("1120x760+120+120")
        configure(app)
        app.update_idletasks()
        app.update()
        _capture_window(_window_handle(app), path)
    finally:
        app.destroy()


def main() -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _capture_app(SCREENSHOT_DIR / "wizard.png", lambda app: None)

    def configure_evaluation(app: PlannerApp) -> None:
        app.config_model = StudyConfig(
            study_name="Uno learning game achieved-result comparison",
            workflow_path="evaluate_against_plan",
            outcome_type="binary",
            observed_control_n=80,
            observed_intervention_n=80,
            observed_control_events=36,
            observed_intervention_events=48,
            planned_control_n=173,
            planned_intervention_n=173,
            planned_effect_size=0.15,
            planned_alpha=0.05,
            planned_power=0.80,
        )
        app._build_ui()
        app.calculate()
        app.notebook.select(app.results_tab)
        app.results_notebook.select(2)

    _capture_app(SCREENSHOT_DIR / "plan_benchmarks.png", configure_evaluation)


if __name__ == "__main__":
    main()
