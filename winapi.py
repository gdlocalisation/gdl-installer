import platform
import ctypes
from ctypes import wintypes


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', wintypes.PULONG),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', wintypes.LONG),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', wintypes.WCHAR * 260)  # Max Path
    ]


try:
    kernel32 = ctypes.windll.kernel32
    GetLastError = kernel32.GetLastError
    GetLastError.argtypes = ()
    GetLastError.restype = wintypes.DWORD
    CloseHandle = kernel32.CloseHandle
    CloseHandle.argtypes = (wintypes.HANDLE, )
    CloseHandle.restype = wintypes.BOOL
    Process32FirstW = kernel32.Process32FirstW
    Process32FirstW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W))
    Process32FirstW.restype = wintypes.BOOL
    Process32NextW = kernel32.Process32NextW
    Process32NextW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W))
    Process32NextW.restype = wintypes.BOOL
    CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
    CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    CreateToolhelp32Snapshot.restype = wintypes.HANDLE
except (FileNotFoundError, AttributeError):
    GetLastError = None
    CloseHandle = None
    Process32FirstW = None
    Process32NextW = None
    CreateToolhelp32Snapshot = None

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
