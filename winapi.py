import ctypes
from ctypes import wintypes


user32 = ctypes.windll.user32

MessageBoxW = user32.MessageBoxW
MessageBoxW.argtypes = (wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT)  # noqa
MessageBoxW.restype = ctypes.c_int
