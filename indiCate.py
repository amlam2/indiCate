#!/usr/bin/env python
# coding=utf-8

# 1 - режим отладки
# 0 - рабочий режим
debug = 0
__version__ = '0.0.5'
__date_version__ = '27.11.2013'
__author__ = u"Лобович Олег Михайлович"
__maintainer__ = u"Лобович Олег Михайлович"
__email__ = 'Aleh@bereza.brest.belpost.by'

import os
import wx.lib.agw.labelbook as LB
import wx.html
import wx.lib.wxpTag
import ConfigParser

from lib.libwork import SFInfo, findFile
from lib.liblore import codeSDODict, opsDict
from lib.libhtml import *

### > иконки, надписи на закладках, отступ по краях
tabIcons_ = (
            'folder.png',
            'messages.png',
            'notes.png',
            'help.png',
            )

tabTexts_ = (
            u"Входящее",
            u"Сообщения",
            u"Пометки",
            u"Справка",
            )

border_ = 2
###

# Цвета для html-текста:
# http://www.stm.dp.ua/web-design/color-html.php

### > начало класса LabelBook < -----------------------------------------------
class LabelBook(LB.LabelBook):
    def __init__(self, picDir, parent):
        """class LabelBook"""
        self.picDir = picDir
        LB.LabelBook.__init__(self, parent, wx.ID_ANY)

        styles = (
                 LB.INB_FIT_LABELTEXT       |
                 #LB.INB_RIGHT               |
                 LB.INB_LEFT                |
                 LB.INB_DRAW_SHADOW         |
                 LB.INB_GRADIENT_BACKGROUND |
                 #LB.INB_WEB_HILITE          |
                 LB.INB_BORDER              |
                 LB.INB_USE_PIN_BUTTON
                 )

        self.SetAGWWindowStyleFlag(styles)

        self.SetColour(LB.INB_TAB_AREA_BACKGROUND_COLOUR, wx.Colour(132, 164, 213))
        self.SetColour(LB.INB_TABS_BORDER_COLOUR,         wx.Colour(0, 0, 204))
        self.SetColour(LB.INB_ACTIVE_TAB_COLOUR,          wx.Colour(255, 255, 255))
        self.SetColour(LB.INB_TEXT_COLOUR,                wx.BLACK)
        self.SetColour(LB.INB_ACTIVE_TEXT_COLOUR,         wx.BLACK)
        self.SetColour(LB.INB_HILITE_TAB_COLOUR,          wx.Colour(191, 216, 216))

        self.SetFontBold(10)

        self.AssignImageList(self.CreateImageList())

        self.Freeze()
        self.AddPage(Tab_01(self), tabTexts_[0], 1, 0)
        #self.AddPage(Tab_02(self), tabTexts_[1], 0, 1)
        #self.AddPage(Tab_03(self), tabTexts_[2], 0, 2)
        self.AddPage(Tab_04(self), tabTexts_[3], 0, 3)
        self.Thaw()


    def CreateImageList(self):
        imagelist = wx.ImageList(32, 32)
        for image in tabIcons_:
            newImage = os.path.join(self.picDir, '%s' % image)
            bmp = wx.Bitmap(newImage, wx.BITMAP_TYPE_PNG)
            imagelist.Add(bmp)
        return imagelist
### > конец класса LabelBook < ------------------------------------------------


### > начало класса ПЕРВОЙ закладки < -----------------------------------------
class Tab_01(wx.Panel):
    """First tab"""
    def __init__(self, parent):
        """First tab"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.htmlWindow = wx.html.HtmlWindow(self)

        ### > событие клика по гиперссылке в окне htmlWindow
        wx.html.EVT_HTML_LINK_CLICKED(self.htmlWindow, wx.ID_ANY, self.OnLink)
        ###

        self.Bind(wx.EVT_BUTTON,   self.OnOK,     id=wx.ID_OK)
        self.Bind(wx.EVT_CHECKBOX, self.OnToggle, id=10      )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.htmlWindow, 1, wx.EXPAND | wx.LEFT, border_)

        self.SetSizer(sizer)
        self.Layout()


    # -- загружает нужную страничку
    def LoadPage(self):
        self.checked = False
        if self.inDir:
            try:
                type(self.upgFile)
                self.MakeUpgradePage()
            except:
                self.MakeInfoPage()
        else:
            if self.inDir == None and self.opsIndex == None:
                errorText = u'Не определён индекс отделения почтовой связи!'
            elif self.inDir == None and not self.opsIndex == None:
                errorText = u'Не найден каталог входящей информации!'
            self.MakeErrorPage(errorText)


    # -- генерирует и отображает html-текст ошибки
    def MakeErrorPage(self, errorText):
        tabCaption = u"О  ш  и  б  к  а"
        self.SetTitle(tabCaption)

        varBlock1 = html_Advert(
                                u'red',
                                os.path.join(self.htmlDir, 'html_error_64.png'),
                                errorText
                               )

        varBlock2 = html_Body(
                              u'',
                              html_Title(tabCaption, __version__),
                              html_BQuote(varBlock1, 2),
                             )

        self.htmlWindow.SetPage(varBlock2)
        self.htmlWindow.SetFocus()


    # -- генерирует и отображает html-текст о состоянии каталога входящей НСИ
    def MakeInfoPage(self):
        tabCaption = u"Состояние каталога входящей нормативно-справочной информации"
        self.SetTitle(tabCaption)

        sectionDic={'01_ver': u'Обновлени%s версии:',
                    '02_sep': u'Баз%s:',
                    '03_els': u'Баз%s ЕЛС:',
                    '04_msc': u'Разное:'
                   }
        linkColor = u'blue'

        # Пустой словарь для промежуточных данных
        resultDic={'01_ver': [],
                   '02_sep': [],
                   '03_els': [],
                   '04_msc': []
                  }

        os.chdir(self.inDir)
        for inFile in iter(os.listdir(self.inDir)):
            if os.path.isfile(inFile):
                typeDB = SFInfo.sfInfo(inFile)
                firstElement = typeDB[0]

                if   firstElement in ['fl_ver']:
                    upgInfoStr = SFInfo.sfInfoShortString(typeDB)
                    parts = [i.strip() for i in upgInfoStr.split(u':')]
                    parts[0] = str(inFile)
                    parts[1] = parts[1].capitalize()
                    resultDic['01_ver'].append(u':'.join(parts))

                    if SFInfo.sfHowOldFile(inFile):
                        linkColor = u'red'
                elif firstElement in ['db_sep']:
                    sdo = typeDB[1].split(u'=')[1]
                    resultStr = u'<b>%s</b> - %s' % (sdo,codeSDODict.get(sdo),)
                    resultDic['02_sep'].append(resultStr)
                elif firstElement in ['db_els']:
                    sdoList = typeDB
                    sdoList.pop(0)
                    for sdo in iter(sdoList):
                        sdo = sdo.split(u'=')[1]
                        resultStr = u'<b>%s</b> - %s' % (sdo,codeSDODict.get(sdo),)
                        resultDic['03_els'].append(resultStr)
                elif firstElement in ['db_lot']:
                    lotList = typeDB
                    lotList.pop(0)
                    for lot in iter(lotList):
                        dbInLot = []
                        dbInLot.append('db_lot')
                        dbInLot.append(lot)
                        resultDic['04_msc'].append(SFInfo.sfInfoShortString(dbInLot))
                elif firstElement in ['db_ktg',\
                                      'db_kta',\
                                      'db_lim',\
                                      'db_blt',\
                                      'db_tar',\
                                      'db_pns',\
                                      'fl_inf',\
                                      'db_pdp',\
                                      'ac_upd']:
                    main = SFInfo.sfInfoShortString(typeDB)
                    # получить описание из файла 'info.txt'
                    if firstElement in ['db_tar',\
                                        'db_ktg',\
                                        'db_kta',\
                                        'db_lim',\
                                        'db_blt']:
                        more = SFInfo.sfGetDescription(inFile)
                        if more:
                            main = u'%s: <i>%s</i>' % (main, more.strip(),)#[:72-len(main)],)
                    resultDic['04_msc'].append(main)

        section = u'''
            <h3>
                <font face='Ariel' color='#778899'> <--!LightSlateGray-->
                    %s
                </font>
            </h3>
            <ul>
                %s
            </ul>
            '''

        line    = u'''<li>%s</li>'''

        href = u'''<i><a href='%s'>%s</a></i>'''

        if resultDic['01_ver'] == []\
                    and resultDic['02_sep'] == []\
                    and resultDic['03_els'] == []\
                    and resultDic['04_msc'] == []:
            sections = html_Advert(
                                   u'',
                                   os.path.join(self.htmlDir, 'html_empty_64.png'),
                                   u'Ничего нет!'
                                  )
        else:
            sections = u''
            for result in iter(sorted(resultDic.keys())):
                lines = u''
                if resultDic[result]:
                    for element in iter(sorted(resultDic[result])):
                        if   result == '01_ver':
                            link = href % (tuple(element.split(u':')))
                            lines += line % (link,)
                        else:
                            lines += line % (element,)
                    if   result in ['01_ver']:
                        if len(resultDic[result]) == 1:
                            ending = u'е'
                        else:
                            ending = u'я'
                            linkColor = u'red'
                        sections += section % (sectionDic[result] % (ending,), lines)
                    elif result in ['02_sep', '03_els']:
                        if len(resultDic[result]) == 1:
                            ending = u'а'
                        else:
                            ending = u'ы'
                        sections += section % (sectionDic[result] % (ending,), lines)
                    elif result in ['04_msc']:
                        sections += section % (sectionDic[result], lines)

        self.htmlWindow.SetPage(
                                html_Body(
                                          linkColor,
                                          html_Title(u'Каталог входящей НСИ содержит:', __version__),
                                          html_BQuote(sections, 2)
                                         )
                               )
        self.htmlWindow.SetFocus()


    # --- событие при щелчке по ссылке на html-форме
    def OnLink(self, event):
        self.upgFile = event.GetLinkInfo().GetHref()
        self.MakeUpgradePage()


    def SetTitle(self, caption):
        if self.opsIndex:
            index = self.opsIndex
        else:
            index = u'не определено'
        title = u"ОПС %s - [ %s ]" % (index, caption)
        self.GetTopLevelParent().SetTitle(title)


    # -- генерирует и отображает html-текст о файле обновления
    def MakeUpgradePage(self):
        tabCaption = SFInfo.sfInfoShortString(SFInfo.sfInfo(self.upgFile))
        self.SetTitle(tabCaption)

        varBlock = html_Upg(
                            SFInfo.sfMTimeFile(self.upgFile),
                            SFInfo.sfGetDescription(self.upgFile, u'Нет описания'),
                            SFInfo.sfReceivDate(self.upgFile),
                            SFInfo.sfReceivDate(self.upgFile, 1),
                           )

        self.htmlWindow.SetPage(
                                html_Body(
                                          u'',
                                          html_Title(tabCaption, __version__),
                                          html_BQuote(varBlock)
                                         )
                               )

        if SFInfo.sfHowOldFile(self.upgFile):
            checkBoxText = u'Обновление произведено. Больше не показывать'
            self.htmlWindow.AppendToPage(html_Confirm(checkBoxText))
        else:
            self.htmlWindow.AppendToPage(html_Confirm())
        #self.htmlWindow.ClearBackground()
        self.htmlWindow.SetFocus()


    # -- событие при щелчке на элементе CheckBox
    # -- заносит в переменную его состояние (отмечено или нет)
    def OnToggle(self, event):
        if event.GetInt():
            self.checked = True
        else:
            self.checked = False


    # -- событие при нажатии кнопки "ОК" на html-форме
    def OnOK(self, event):
        if self.checked:
            # удалить файл, если стоит "галочка"
            if os.path.exists(self.upgFile):
                os.remove(self.upgFile)
        self.MakeInfoPage()
        del self.upgFile
### > конец класса ПЕРВОЙ закладки < ------------------------------------------


### > начало класса ВТОРОЙ закладки < -----------------------------------------
class Tab_02(wx.Panel):
    def __init__(self, parent):
        """Third tab"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tabCaption = u"Информационные сообщения из РУПС"

        self.htmlWindow = wx.html.HtmlWindow(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.htmlWindow, 1, wx.EXPAND | wx.LEFT, border_)

        self.SetSizer(sizer)
        self.Layout()


    def LoadPage(self):
        self.MakePage()
        self.SetTitle(self.tabCaption)


    def SetTitle(self, caption):
        if self.opsIndex:
            index = self.opsIndex
        else:
            index = u'не определено'
        title = u"ОПС %s - [ %s ]" % (index, caption)
        self.GetTopLevelParent().SetTitle(title)


    def MakePage(self):
        with open(os.path.join(self.startDir, 'info.txt'), 'rb') as f:
            infoTxt = u''
            for line in f:
                line = unicode(line, 'cp1251')
                infoTxt += line

        varBlock = html_Body(
                             u'red',
                             html_Title(u'Последнее информационное сообщение', __version__),
                             u'''<pre>%s</pre>''' % infoTxt,
                            )
        self.htmlWindow.SetPage(varBlock)
### > конец класса ВТОРОЙ закладки < ------------------------------------------


### > начало класса ТРЕТЕЙ закладки < -----------------------------------------
class Tab_03(wx.Panel):
    def __init__(self, parent):
        """Third tab"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tabCaption = u"Мои пометки"

        self.htmlWindow = wx.html.HtmlWindow(self)

        self.htmlWindow.SetPage(html_NotImplemented())

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.htmlWindow, 1, wx.EXPAND | wx.LEFT, border_)

        self.SetSizer(sizer)
        self.Layout()


    def LoadPage(self):
        self.MakePage()


    def SetTitle(self, caption):
        if self.opsIndex:
            index = self.opsIndex
        else:
            index = u'не определено'
        title = u"ОПС %s - [ %s ]" % (index, caption)
        self.GetTopLevelParent().SetTitle(title)


    def MakePage(self):
        pass
### > конец класса ТРЕТЕЙ закладки < ------------------------------------------


### > начало класса ЧЕТВЁРТОЙ закладки < --------------------------------------
class Tab_04(wx.Panel):
    def __init__(self, parent):
        """Third tab"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.htmlWindow = wx.html.HtmlWindow(self)

        ### > событие клика по гиперссылке в окне htmlWindow
        wx.html.EVT_HTML_LINK_CLICKED(self.htmlWindow, wx.ID_ANY, self.OnLink)
        ###

        ### > событие при нажатии кнопки ОК в окне htmlWindow
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        ###

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.htmlWindow, 1, wx.EXPAND | wx.LEFT, border_)

        self.SetSizer(sizer)
        self.Layout()


    def LoadPage(self):
        try:
            exec('self.%s()' % self.currentFunc)
        except:
            self.MakeMainPage()


    # -- динамическое изменение заголовка окна
    def SetTitle(self, caption):
        if self.opsIndex:
            index = self.opsIndex
        else:
            index = u'не определено'
        title = u"ОПС %s - [ %s ]" % (index, caption)
        self.GetTopLevelParent().SetTitle(title)


    # --- событие при щелчке по ссылке на html-форме
    def OnLink(self, event):
        self.currentFunc = event.GetLinkInfo().GetHref()
        try:
            exec('self.%s()' % self.currentFunc)
        except:
            ### > показать сообщение об ошибке
            infMsg = u"Нет функции %s" % self.currentFunc
            infMsg += 10 * ' '

            wx.MessageBox(infMsg,
                          u"Ошибка!",
                          wx.OK | wx.ICON_ERROR,
                          self)
            ###


    # -- событие при нажатии кнопки "ОК" на html-форме
    def OnOK(self, event):
        del self.currentFunc
        self.MakeMainPage()


    # -- главная страница вкладки "Справка"
    def MakeMainPage(self):
        tabCaption = u"Справочная информация"
        self.SetTitle(tabCaption)

        hItem_1 = html_HItem('MakeFAQPage', # название функции-обработчика
                             os.path.join(self.htmlDir, 'html_help_48px.png'),
                             u'Как пользоваться программой?')
        hItem_2 = html_HItem('MakeSDOPage', # название функции-обработчика
                             os.path.join(self.htmlDir, 'html_sdo_48px.png'),
                             u'Некоторые коды СДО и названия платежей')
        hItem_3 = html_HItem('MakeAboutPage', # название функции-обработчика
                             os.path.join(self.htmlDir, 'html_info_48px.png'),
                             u'Об ОПС %s' % self.opsIndex)

        html_Help = html_HChoice(
                                 hItem_1,
                                 hItem_2,
                                 hItem_3
                                )

        bannerFile = findFile(self.htmlDir, 'html_banner*.*')
        if bannerFile:
            banner = u'''
                <div align='right'>
                    <img src='%s'>
                </div>
                ''' % os.path.join(self.htmlDir, bannerFile)
        else:
            banner = u''

        varBlock = html_Body(
                             u'',
                             html_Title(tabCaption, __version__),
                             html_BQuote(html_Help, 2),
                            )

        self.htmlWindow.SetPage(varBlock)
        self.htmlWindow.AppendToPage(banner)
        self.htmlWindow.SetFocus()


    # -- страница при переходе по первой ссылке на вкладке "Справка"
    def MakeFAQPage(self):
        tabCaption = u"Как пользоваться программой"
        self.SetTitle(tabCaption)

        varBlock1 = html_Advert(
                                u'',#html_uconstruction_64px#html_help_4
                                os.path.join(self.htmlDir, 'html_uconstruction_64px.png'),
                                u"%sВ разработке" % (u'&nbsp;' * 5,)
                               )

        varBlock2 = html_Body(
                             u'',
                             html_Title(tabCaption, __version__),
                             html_BQuote(varBlock1, 1)
                            )

        self.htmlWindow.SetPage(varBlock2)
        self.htmlWindow.AppendToPage(html_Confirm())
        self.htmlWindow.SetFocus()


    # -- страница при переходе по второй ссылке на вкладке "Справка"
    def MakeSDOPage(self):
        tabCaption = u"Справочная информация по некоторым кодам СДО"
        self.SetTitle(tabCaption)

        lenght = len(codeSDODict)
        middle = lenght/2 + lenght%2

        hList = []
        for sdo in iter(sorted(codeSDODict)):
            hList.append(u'<b>%s</b> - %s' % (sdo, codeSDODict.get(sdo),))

        column1 = u'''
                    <td valign='top' width='50%%'>
                        %s
                    </td>
                    ''' % (u'<br>'.join(hList[:middle]),)
        column2 = u'''
                    <td valign='top' width='50%%'>
                        %s
                    </td>
                    ''' % (u'<br>'.join(hList[middle:]),)

        varBlock = html_Body(
                             u'',
                             html_Title(u'Некоторые коды СДО и названия платежей', __version__),
                             html_SDO(column1 + column2),
                            )

        self.htmlWindow.SetPage(varBlock)
        self.htmlWindow.AppendToPage(html_Confirm(space='<p>'))
        self.htmlWindow.SetFocus()


    # -- страница при переходе по третей ссылке на вкладке "Справка"
    def MakeAboutPage(self):
        tabCaption = u"Об почтовом отделении"
        self.SetTitle(tabCaption)

        varBlock1 = html_Advert(
                                u'',
                                os.path.join(self.htmlDir, 'html_uconstruction_64px.png'),
                                u"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;В разработке"
                               )

        varBlock2 = html_Body(
                             u'',
                             html_Title(tabCaption, __version__),
                             html_BQuote(varBlock1, 2)
                            )

        self.htmlWindow.SetPage(varBlock2)
        self.htmlWindow.AppendToPage(html_Confirm())
        self.htmlWindow.SetFocus()
### > конец класса ЧЕТВЁРТОЙ закладки < ---------------------------------------


### > начало класса главного окна приложения < --------------------------------
class MainWindowFrame(wx.Frame):
    def __init__(self,  *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE ^\
                       (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

        wx.Frame.__init__(self, *args, **kwds)

        self.Hide()

        self.__set_variables()

        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour(wx.Colour(255,255,255))

        self.labelBook = LabelBook(self.picDir, self.panel)

        self.Bind(wx.EVT_CLOSE,
                  self.OnCloseWindow)
        self.labelBook.Bind(LB.EVT_IMAGENOTEBOOK_PAGE_CHANGED,
                            self.OnTabChanged)

        self.__do_layout()
        self.__set_properties()

        self.LoadTab()


    # --- размещение виджетов на сайзерах
    def __do_layout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        vSizer = wx.BoxSizer(wx.VERTICAL)

        vSizer.Add(self.labelBook, 1, wx.EXPAND | wx.ALL, border_)

        self.panel.SetSizer(vSizer)

        mainSizer.Add(self.panel, 1, wx.EXPAND, 0)

        self.SetSizer(mainSizer)

        mainSizer.Fit(self)

        self.Layout()


    # --- установка свойств
    def __set_properties(self):
        self.SetSize((950, 700))
        self.CenterOnScreen()
        self.Show(True)

        # создание элементов главного окна приложения
        #self.MakeToolBar()
        #self.MakeStatusBar()


    # --- установка переменных
    def __set_variables(self):
        ### > директория запуска
        # '__WXMSW__', '__WXMAC__', '__WXGTK__'
        # if 'wxGTK' in wx.PlatformInfo:
        if wx.Platform == '__WXMSW__':
            self.startDir = os.path.dirname(__file__)
        else:
            self.startDir = os.getcwd()
        ###

        ### > текущая директория
        os.chdir(self.startDir)
        ###

        ### > имя файла настроек
        self.cfgFileName = os.path.splitext(os.path.basename(__file__))[0] + '.cfg'
        ###

        ### > директория пиктограмм
        self.picDir = os.path.join(self.startDir, 'pic')
        ###

        ### > директория html-страничек и картинок
        self.htmlDir = os.path.join(self.picDir, 'html')
        ###

        ### > иконка приложения
        self.icon = os.path.join(self.startDir, 'icon.png')
        ###

        ### > установка иконки приложения
        self.SetIcon(wx.IconFromBitmap(wx.Bitmap(self.icon)))
        ###

        ### > получить индекс из ini-файла
        self.opsIndex = self.GetOpsIndex(self.cfgFileName)
        ###

        ### > директория входящей НСИ
        if self.opsIndex:
            if debug:
                self.inDir = os.path.join(self.startDir, 'in') ## для настройки
                if not os.path.exists(self.inDir):
                    os.mkdir(self.inDir)
            else:
                self.inDir = 'D:\\SKSdata\\PRPI\\OS%s\\OUT' % (self.opsIndex,)
                if not os.path.exists(self.inDir):
                    self.inDir = None
        else:
            self.inDir = None
        ###


    # --- событие при закрытии окна приложения
    def OnCloseWindow(self, event):
        self.Hide()
        self.Destroy()


    # --- событие при смене закладки
    def OnTabChanged(self, event):
        self.LoadTab()

    '''
    #for key in self.__dict__:
    #    print key
    
    opsIndex
    cfgFileName
    picDir
    this
    htmlDir
    labelBook
    startDir
    inDir
    panel
    icon
    '''
    def LoadTab(self):
        #for attr in self.__dict__:
        #    setattr(self.labelBook.GetCurrentPage(), attr, self.attr)
        
        self.labelBook.GetCurrentPage().opsIndex = self.opsIndex
        self.labelBook.GetCurrentPage().inDir    = self.inDir
        self.labelBook.GetCurrentPage().htmlDir  = self.htmlDir
        self.labelBook.GetCurrentPage().startDir = self.startDir
        self.labelBook.GetCurrentPage().LoadPage()


    # --- получить индекс ОПС из cfg-файла
    def GetOpsIndex(self, cfgFileName):
        try:
            cfgFile = ConfigParser.SafeConfigParser()
            cfgFile.read(cfgFileName)

            opsIndex = cfgFile.get('ops','index')
            if opsIndex in iter(opsDict):
                return opsIndex
            else:
                return None
        #except ConfigParser.MissingSectionHeaderError or ConfigParser.NoOptionError:
        except:
            return None
### > конец класса главного окна приложения < ---------------------------------


### > начало класса приложения < ----------------------------------------------
class App(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame = MainWindowFrame(None, -1, "")
        self.SetTopWindow(frame)
        frame.Show()
        return True
### > конец класса приложения < -----------------------------------------------

def main():
    app = App(0)
    app.MainLoop()

if __name__ == "__main__":
    main()
