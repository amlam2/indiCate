#!/usr/bin/env python
# coding=utf-8

import indiCate
import os, glob, shutil, ConfigParser
import win32con, win32gui, win32gui_struct
import threading, PyWT
from datetime import datetime
from fsmonitor import FSMonitorThread
from lib.liblore import opsDict
from lib.libtray import Taskbar

### К О Н С Т А Н Т Ы
## заголовок MessageBoxes
MSG_CAPTION = u"Мониторинг каталога входящей НСИ"

# название файла иконки
ICON = 'icon.ico'

## поддержка
_VERSION      = indiCate.__version__ or '0.0.6'
_DATE_VERSION = '28.02.2014'
_AUTHOR       = indiCate.__author__
_MAINTAINER   = indiCate.__maintainer__
_EMAIL        = indiCate.__email__

## id пунктов контекстного меню
CONTEXT_MENU_ID_EXIT = 1000
CONTEXT_MENU_ID_SHOW = 1010

## задержки и интервалы (в секундах)
T_DELAY_BEFORE_DISPLAYING_FIRST_REMINDER = 300.0
T_DELAY_BEFORE_DISPLAYING_NOTIFICATION   = 20.0
T_INTERVAL_BETWEEN_REMINDERS             = 1800.0

T_TIME_DISPLAY_REMINDERS     = 60
T_TIME_DISPLAY_NOTIFICATIONS = 30

## директории
DIR_IN    = 'D:\\SKSdata\\PRPI\\OS%s\\OUT'
DIR_LIMIT = 'D:\\SKSdata\\PRPI\\KTF5%s\\OUT'

## файлы
FILE_NAME_LIMIT = 'nt0000.000'

## максимальный размер log-файла
# возможные варианты
# 1048576L - 1 Мбайт
# 786432L  - 750 кбайт
# 524288L  - 500 кбайт
# 262144L  - 250 кбайт
LOG_FILE_MAX_SIZE = 524288L

## словари
DICT_ERR =  {
    1: u"Не найден файл конфигурации",
    2: u"Не найден индекс ОПС в файле конфигурации",
    3: u"Не верный индекс ОПС в файле конфигурации",
    4: u"Не найден каталог входящей НСИ",
    5: u"Не найден каталог входящих НДВ",
    6: u"Не удалось запустить мониторинг каталога НСИ"
            }
DICT_NSI =  {
    'vn'           : u"обновление версии",
    'np'           : u"базы платежей",
    'nt'           : u"тарифы",
    'ns'           : u"база пенсий",
    'nl'           : u"лотереи",
    'limit'        : u"нормы выдачи в доставку",
    'katalog.zip'  : u"подписной каталог",
    'pdpskops.rar' : u"подписка Paradox",
    'fupdate.rar'  : u"обновление файлов",
    'info.txt'     : u"информационный файл"
            }

class NSIMonTaskbar(Taskbar):
    def __init__(self):
        Taskbar.__init__(self)
        self.inDir      = None
        self.limitDir   = None
        self.notifyFlag = True
        self.menuItems = (
                          (u"Выход",    CONTEXT_MENU_ID_EXIT),
                          (u"Показать", CONTEXT_MENU_ID_SHOW)
                         )
        errMsgs = self.__set_properties()
        if os.path.exists(self.logFilePath): self.__write_log('')
        self.__write_log(u"*** Старт программы *** ver. %s ***" % _VERSION)
        if errMsgs:
            win32gui.MessageBox(
                    self.hwnd,
                    '\n'.join([DICT_ERR.get(i) for i in errMsgs]) + 10 * " ",
                    MSG_CAPTION,
                    win32con.MB_OK | win32con.MB_ICONERROR
                                )
            for errMsg in errMsgs: self.__write_log(DICT_ERR.get(errMsg))
            win32gui.DestroyWindow(self.hwnd)
        else:
            self.Show()
        if self.inDir:
            self.__run_monitor()
            self.nsiStackNew = []
            self.nsiStackOld = os.listdir(self.inDir)
            self.wtimer = PyWT.WaitableTimer(
                                    T_INTERVAL_BETWEEN_REMINDERS,
                                    T_INTERVAL_BETWEEN_REMINDERS,
                                    self.DisplayReminder,
                                    StartCondition=PyWT.TIMER_NO_ACTIVATE
                                            )
            self.wtimer.start()
            for nsiFile in self.nsiStackOld[:]: # убрать обновление версии из напоминания
                if nsiFile.lower()[:2] in ['vn']:
                    self.nsiStackOld.remove(nsiFile)
            self.MoveLimit(self.nsiStackOld)
            if self.nsiStackOld:
                threading.Timer(T_DELAY_BEFORE_DISPLAYING_FIRST_REMINDER,\
                                self.ReminderStartUp).start()

    def __set_properties(self):
        self.startDir = os.path.dirname(__file__)
        os.chdir(self.startDir)
        self.cfgFilePath = os.path.join(self.startDir, 'indiCate.cfg')
        self.logDir = os.path.join(self.startDir, 'log')
        if not os.path.exists(self.logDir): os.mkdir(self.logDir)

        ### > иконка приложения
        iconFlags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(
                                    win32gui.GetModuleHandle(None),
                                    os.path.join(self.startDir, ICON),
                                    win32con.IMAGE_ICON,
                                    0,
                                    0,
                                    iconFlags
                                  )
        self.SetIcon(hicon, u"Поступившая НСИ")
        ###

        errorMessages = []
        self.opsIndex = None
        if os.path.exists(self.cfgFilePath):
            cfg = ConfigParser.SafeConfigParser()
            cfg.read(self.cfgFilePath)
            cfg_dict = {}
            for section in cfg.sections():
                cfg_dict[section] = {}
                for option in cfg.options(section):
                    cfg_dict[section][option] = cfg.get(section, option)
            try:
                self.debug = cfg_dict.get('mode').get('debug')
                self.debug = int(self.debug)
            except:
                self.debug = 0
            try:
                self.opsIndex = cfg_dict.get('ops').get('index')
                if not(self.opsIndex in iter(opsDict)):
                    self.opsIndex = None
                    errorMessages.append(3)
            except:
                errorMessages.append(2)
            if self.opsIndex:
                if self.debug: ## для настройки
                    self.inDir  = os.path.join(self.startDir, 'in' )
                    self.limitDir = os.path.join(self.startDir, 'limit')
                    for dir in [self.inDir, self.limitDir]:
                        if not os.path.exists(dir): os.mkdir(dir)
                else:
                    self.inDir    = DIR_IN    % (self.opsIndex,)
                    self.limitDir = DIR_LIMIT % (self.opsIndex[-3:],)
                    if not os.path.exists(self.inDir):
                        self.inDir = None
                        errorMessages.append(4)
                    if not os.path.exists(self.limitDir):
                        self.limitDir = None
                        errorMessages.append(5)
        else:
            errorMessages.append(1)
        self.logFileName = '%s_%s.log' %\
                (os.path.splitext(os.path.basename(__file__))[0],\
                self.opsIndex or 'errors')
        self.logFilePath = os.path.join(self.logDir, self.logFileName)
        return errorMessages

    def __run_monitor(self):
        self.monitor = FSMonitorThread(callback=self.OnFSEvent)
        try:
            self.monitor.add_dir_watch(self.inDir)
        except:
            self.__write_log(DICT_ERR.get(6))

    def __write_log(self, line):
        if os.path.exists(self.logFilePath):
            if os.path.getsize(self.logFilePath) <= LOG_FILE_MAX_SIZE:
                openFlag = 'a'
            else:
                name, ext = os.path.splitext(self.logFilePath)
                listLogFiles = glob.glob1(self.logDir, '%s.*' % os.path.basename(name))
                maxNum = []
                if listLogFiles:
                    for file in listLogFiles:
                        item = file.split('.')[1]
                        if item.isdigit():
                            maxNum.append(item)
                if maxNum:
                    ext = '.' + (str(int(max(maxNum)) + 1)).zfill(3)
                else:
                    ext = '.' + '0'.zfill(3)
                os.rename(self.logFilePath, name + ext)
                openFlag = 'w'
        else:
            openFlag = 'w'
        with open(self.logFilePath, openFlag) as lf:
            if line:
                wline = datetime.now().strftime('%d.%m.%y | %H:%M:%S.%f | ')
                wline += line.encode('cp1251')
                wline += '\n'
                lf.write(wline)
            else:
                lf.write('\n')

    def ReminderStartUp(self):
        self.DisplayReminder()
        self.wtimer.Activate()
    
    def ReminderStartLater(self):
        if self.nsiStackNew:
            self.DisplayNotice()
            self.MoveLimit(self.nsiStackNew)
            self.notifyFlag = True
            self.nsiStackOld.extend(self.nsiStackNew)
            self.nsiStackNew = []
            if self.nsiStackOld:
                if self.wtimer.GetState() == PyWT.TIMER_STATE_INIT:
                    self.wtimer.Activate()
                elif self.wtimer.GetState() in [PyWT.TIMER_STATE_RUNNINGINITIAL,\
                                                PyWT.TIMER_STATE_RUNNING]:
                    self.wtimer.Deactivate()
                    while True:
                        if self.wtimer.GetState() == PyWT.TIMER_STATE_INIT:
                            self.wtimer.Activate()
                            break

    def GetInfoMsg(self, nsiStack):
        if nsiStack:
            infoList = []
            for nsiFile in nsiStack:
                name = nsiFile.lower()
                bname, ext = os.path.splitext(name)
                if bname[:2] in ['vn', 'np', 'nt', 'ns', 'nl']:
                    infoList.append(bname[:2])
                elif bname in ['limit']:
                    infoList.append(bname)
                elif name in ['katalog.zip', 'pdpskops.rar']:
                    infoList.append(name)
                elif name in ['fupdate.rar']:
                    pass
                elif name in ['info.txt']:
                    pass
            infoMsg = []
            for nsi in sorted(set(infoList), reverse=True):
                infoMsg.append(8 * " " + "- " + DICT_NSI.get(nsi))
            return infoMsg
        else:
            return None

    def DisplayNotice(self):
        upd = False
        for nsiFile in self.nsiStackNew[:]:
            if nsiFile.lower()[:2] in ['vn']:
                self.nsiStackNew.remove(nsiFile)
                upd = True
        if upd:
            title = u"ПОСТУПЛЕНИЕ ОБНОВЛЕНИЯ ВЕРСИИ:"
            icon = win32gui.NIIF_WARNING
            msg = u"Внимание!\n"
            msg += u"Обновление весии выполнить сегодня вечером\n"
            msg += u"либо завтра утром при закрытой смене на каждой\n"
            msg += u"машине в отдельности."
            if self.nsiStackNew:
                msg += 3 * u'\n'
                msg += u"ПОСТУПЛЕНИЕ НСИ:\n"
                msg += 1 * u'\n'
                msg += '\n'.join(self.GetInfoMsg(self.nsiStackNew))
        else:
            title = u"ПОСТУПЛЕНИЕ НСИ:"
            icon = win32gui.NIIF_INFO
            msg = '\n'.join(self.GetInfoMsg(self.nsiStackNew))
        if msg:
            self.BalloonBox(
                             title + " " * 3,
                             msg,
                             icon,
                             T_TIME_DISPLAY_NOTIFICATIONS
                           )

    def MoveLimit(self, nsiStack):
        try:
            limitFile = FILE_NAME_LIMIT
        except:
            limitFile = datetime.now().strftime('nt%d%m%H.0%M ')
        for nsiFile in nsiStack[:]:
            if os.path.splitext(nsiFile)[0].lower() in ['limit']:
                shutil.move(os.path.join(self.inDir,    nsiFile),
                            os.path.join(self.limitDir, limitFile))

    def DisplayReminder(self):
        msg = self.GetInfoMsg(self.nsiStackOld)
        if msg:
            title = u"НЕ ЗАГРУЖЕНА НСИ:"
            self.BalloonBox(
                             title + " " * 3,
                             '\n'.join(msg),
                             win32gui.NIIF_WARNING,
                             T_TIME_DISPLAY_REMINDERS
                           )

    def DisplayTest(self):
        title = u"ТЕСТОВОЕ СООБЩЕНИЕ:"
        self.BalloonBox(
                         title + " " * 3,
                         u"Это проверка!",
                         win32gui.NIIF_WARNING,
                         T_TIME_DISPLAY_REMINDERS
                       )

    def BalloonBox(self, title, msg, hicon, delay):
        # Переменная hicon, вид иконки
        # win32gui.NIIF_INFO     # иконка "Восклицательный знак"
        # win32gui.NIIF_WARNING  # иконка "Внимание"
        # win32gui.NIIF_NONE     # без иконки
        # win32gui.NIIF_ERROR    # иконка "Ошибка"
        # win32gui.NIIF_NOSOUND  # без звука

        #NIF_ICON | NIF_TIP | NIF_MESSAGE | NIF_SHOWTIP
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_INFO
        nid = (
                self.hwnd,
                0,
                flags,
                win32con.WM_USER+20,
                self.hicon,
                "",
                msg,
                delay * 1000,
                title,
                hicon
              )
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)

    def OnFSEvent(self, evt):
        if evt.action_name in ['create']:
            self.__write_log(u"[NSI_DIR] Поступил файл %s" % evt.name)
            self.nsiStackNew.append(evt.name)
            if self.notifyFlag:
                self.notifyFlag = False
                threading.Timer(T_DELAY_BEFORE_DISPLAYING_NOTIFICATION,\
                                self.ReminderStartLater).start()
        elif evt.action_name in ['delete']:
            self.__write_log(u"[NSI_DIR] Удалён файл %s" % evt.name)
            if self.nsiStackNew.count(evt.name):
                self.nsiStackNew.remove(evt.name)
            else:
                self.nsiStackOld.remove(evt.name)
            if not self.nsiStackOld:
                self.wtimer.Deactivate()
        elif evt.action_name in ['move to']:
            self.__write_log(u"[NSI_DIR] Изменён файл %s" % evt.name)

    def OnClick(self):
        if self.debug:
            #print PyWT.STATE_TO_TEXT.get(self.wtimer.GetState())
            #self.DisplayTest()
            #print 'self.nsiStackNew = %s' % self.nsiStackNew
            #print 'self.nsiStackOld = %s' % self.nsiStackOld
            pass

    def OnRightClick(self):
        try:
            menu = win32gui.CreatePopupMenu()
            for menuText, menuId in self.menuItems:
                menuItem = win32gui_struct.PackMENUITEMINFO(text=menuText, wID=menuId)
                win32gui.InsertMenuItem(menu, 0, 1, menuItem[0])

            # Пункт меню жирным шрифтом
            #win32gui.SetMenuDefaultItem(menu, CONTEXT_MENU_ID_SHOW, 0)

            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.TrackPopupMenu(
                                     menu,
                                     win32con.TPM_LEFTALIGN,
                                     pos[0],
                                     pos[1],
                                     0,
                                     self.hwnd,
                                     None
                                    )
            win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        except:
            pass

    def OnCommand(self, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        if id == CONTEXT_MENU_ID_EXIT:
            infMsg = u"Вы действительно хотите закрыть программу?"
            infMsg += 10 * " "
            answer = win32gui.MessageBox(
                                         hwnd,
                                         infMsg,
                                         MSG_CAPTION,
                                         win32con.MB_YESNO
                                            |win32con.MB_ICONQUESTION
                                            |win32con.MB_DEFBUTTON2
                                         )
            if answer == win32con.IDYES:
                win32gui.DestroyWindow(hwnd)
        elif id == CONTEXT_MENU_ID_SHOW:
            self.StartExternalApp()

    def OnDoubleClick(self):
        self.StartExternalApp()

    def OnBalloonClick(self):
        if self.nsiStackOld:
            self.StartExternalApp()

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        if self.inDir: self.wtimer.Terminate(DisableStateCheck=True)
        self.__write_log(u"*** Выход из программы ***")
        Taskbar.OnDestroy(self, hwnd, msg, wparam, lparam)

    def StartExternalApp(self):
        thread = threading.Thread(target=indiCate.main)
        thread.setName('indiCate')
        thread.daemon = True
        thread.start()

if __name__=='__main__':
    NSIMonTaskbar()
    win32gui.PumpMessages() # Запустить приложение
