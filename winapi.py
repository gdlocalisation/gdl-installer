import platform
import ctypes
from ctypes import wintypes

try:
    user32 = ctypes.windll.user32
    MessageBoxW = user32.MessageBoxW
    MessageBoxW.argtypes = (wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT)
    MessageBoxW.restype = ctypes.c_int
except (FileNotFoundError, AttributeError):
    ShellExecuteW = None

try:
    shell32 = ctypes.windll.shell32
    ShellExecuteW = shell32.ShellExecuteW
    ShellExecuteW.argtypes = (
        wintypes.HWND,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        ctypes.c_int
    )
    ShellExecuteW.restype = wintypes.HINSTANCE
except (FileNotFoundError, AttributeError):
    ShellExecuteW = None

try:
    if int(platform.version().split('.')[-1]) < 17763:  # noqa fuck Micro$oft fuck Micro$oft fuck Micro$oft fuck
        raise FileNotFoundError('FUCK MICROSOFT DUDE WINDOWS IS PEACE OF SHIT')
    ux_theme = ctypes.windll.uxtheme
    ShouldUseDarkMode = ux_theme.__getitem__(132)
    ShouldUseDarkMode.argtypes = ()
    ShouldUseDarkMode.restype = ctypes.c_byte
except (FileNotFoundError, AttributeError):
    ShouldUseDarkMode = None

try:
    dwm_api = ctypes.windll.dwmapi
    DwmSetWindowAttribute = dwm_api.DwmSetWindowAttribute
    DwmSetWindowAttribute.argtypes = (
        wintypes.HWND,
        wintypes.DWORD,
        wintypes.LPCVOID,
        wintypes.DWORD
    )
    DwmSetWindowAttribute.restype = wintypes.LONG
except (FileNotFoundError, AttributeError):
    DwmSetWindowAttribute = None
