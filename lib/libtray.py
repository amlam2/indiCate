# coding=utf-8

import win32api
import win32con
import win32gui

from ctypes.wintypes import WinDLL, BOOL, DWORD
_kernel32 = WinDLL("kernel32")

SetProcessShutdownParameters = _kernel32.SetProcessShutdownParameters
SetProcessShutdownParameters.restype = BOOL
SetProcessShutdownParameters.argtypes = [DWORD, DWORD]

class Taskbar:
    def __init__(self):
        self.visible = 0

        message_map = {
            win32con.WM_DESTROY         : self.OnDestroy,
            win32con.WM_CLOSE           : self.OnDestroy,
            win32con.WM_QUIT            : self.OnDestroy,
            #win32con.WM_QUERYENDSESSION : self.OnDestroy,
            win32con.WM_ENDSESSION      : self.OnDestroy,
            win32con.WM_COMMAND         : self.OnCommand,
            win32con.WM_USER+20         : self.OnTaskbarNotify,
                      }
        # Регистрация класса окна
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map
        classAtom = win32gui.RegisterClass(wc)
        # Создание окна
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow( classAtom, "Taskbar", style, \
                    0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                    0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)

    def SetIcon(self, hicon, tooltip=None):
        self.hicon = hicon
        self.tooltip = tooltip

    def Show(self):
        """Display the taskbar icon"""
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE
        if self.tooltip is not None:
            flags |= win32gui.NIF_TIP
            nid = (self.hwnd, 0, flags, win32con.WM_USER+20, self.hicon, self.tooltip)
        else:
            nid = (self.hwnd, 0, flags, win32con.WM_USER+20, self.hicon)
        if self.visible:
            self.Hide()
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        self.visible = 1

    def Hide(self):
        """Hide the taskbar icon"""
        if self.visible:
            nid = (self.hwnd, 0)
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        self.visible = 0

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        self.Hide()
        win32gui.PostQuitMessage(0) # Завершить приложение

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        # WM_LBUTTONDBLCLK  - 'Двойной щелчок левой кнопкой'
        # WM_LBUTTONDOWN    - 'Нажатие левой кнопки мыши'
        # WM_LBUTTONUP      - 'Отжатие левой кнопки мыши'
        # WM_MBUTTONDBLCLK  - 'Двойной щелчок средней кнопкой мыши'
        # WM_MBUTTONDOWN    - 'Нажатие средней кнопки мыши'
        # WM_MBUTTONUP      - 'Отжатие средней кнопки мыши'
        # WM_MOUSEMOVE      - 'Перемещение мыши'
        # WM_MOUSEWHEEL     - 'Вращение колесика мыши'
        # WM_RBUTTONDBLCLK  - 'Двойной щелчок правой кнопкой'
        # WM_RBUTTONDOWN    - 'Нажатие правой кнопки мыши'
        # WM_RBUTTONUP      - 'Отжатие правой кнопки мыши'
        # WM_BALLOONCLOSE (WM_USER+4), 1028 - 'Закрыть крестиком на подсказке'
        # WM_BALLOONCLICK (WM_USER+5), 1029 — 'Закрыть кликом по подсказке'

        if lparam == win32con.WM_LBUTTONUP:
            self.OnClick()
        elif lparam == win32con.WM_LBUTTONDBLCLK:
            self.OnDoubleClick()
        elif lparam == win32con.WM_RBUTTONUP:
            self.OnRightClick()
        elif lparam == win32con.WM_USER+5: # WM_BALLOONCLICK, 1029
            self.OnBalloonClick()
        elif lparam == win32con.WM_USER+4: # WM_BALLOONCLOSE, 1028
            self.OnBalloonClose()
        return True

    def OnClick(self):
        """Override in subclassess"""
        pass

    def OnDoubleClick(self):
        """Override in subclassess"""
        pass

    def OnRightClick(self):
        """Override in subclasses"""
        pass

    def OnBalloonClick(self):
        """Override in subclasses"""
        pass

    def OnBalloonClose(self):
        """Override in subclasses"""
        pass

    def OnCommand(self, hwnd, msg, wparam, lparam):
        """Override in subclassess"""
        pass
