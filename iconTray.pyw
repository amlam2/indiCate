#!/usr/bin/env python
# coding=utf-8

import win32gui, NSImon

if __name__ == '__main__':
    NSImon.NSIMonTaskbar()
    win32gui.PumpMessages()
