import ctypes
from ctypes import wintypes


user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

MessageBoxW = user32.MessageBoxW
MessageBoxW.argtypes = (wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT)  # noqa
MessageBoxW.restype = ctypes.c_int

ShellExecuteW = shell32.ShellExecuteW
ShellExecuteW.argtypes = (
    wintypes.HWND,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    ctypes.c_int
)  # noqa
ShellExecuteW.restype = wintypes.HINSTANCE
