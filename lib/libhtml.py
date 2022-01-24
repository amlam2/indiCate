# coding=utf-8

### > возвращает заголовок странички, линию с версией и копирайтом
def html_Title(title, version=''):
    if version == '':
        ver = ''
    else:
        ver = u'Version %s' % (version,)
    html = u'''
        <font face='Tahoma, Ariel'>
            <h2 align='center'>%s</h2>
        </font>
        <div align='right'>
            <table bgcolor='silver' width='100%%' border='2'></table>
            <font size='2' color='grey' align='right'>
                %s &copy; Берёзовский РУПС
            </font>
        </div>

        ''' % (title, ver)
    return html
###


### >
def html_Body(linkcolor, title, body):
    html = u'''
        <html>
            <body link=%s>
                %s
                <font face='Ariel' size='4'>
                    %s
                </font>
            <body>
        </html>
        '''
    return html % (linkcolor, title, body,)
###


### >
def html_Advert(fontcolor, imagepath, text):
    html = u'''
        <font color='%s'>
            <h4>
                <table align='center' valign='middle'>
                    <tr>
                        <td>
                            <img src='%s'>
                        </td>
                        <td>
                            %s
                        </td>
                    </tr>
                </table>
            </h4>
        </font>
        '''
    return html % (fontcolor, imagepath, text,)
###


### >
def html_Upg(dateget, description, datefrom, dateto):
    html = u'''
        <dl>
            <dt><b>Поступление:</b></dt>
            <dd><table align='justify'><tr><td>%s</td></tr></table></dd>
        </dl>
        <dl>
            <dt><b>Описание:</b></dt>
            <dd><table align='justify'><tr><td>%s</td></tr></table></dd>
        </dl>
        <dl>
            <dt><b>Выполнить:</b></dt>
            <dd><table align='justify'><tr><td>%s г. (вечером) либо %s г. (утром)
            при <b>ЗАКРЫТОЙ</b> смене в режиме администратора
            на каждой машине в отдельности</td></tr></table></dd>
        </dl>
        <dl>
            <dt><b>Памятка:</b></dt>
            <dd>
                <table align='justify'>
                    <tr><td>
                        <font face='Ariel' size='2' color='white'>
                            <table align='center' valign='middle' bgcolor='red' width='100%%' border='2'>
                                <tr>
                                    <td><b>ФУНКЦИИ АДМИНИСТРАТОРА</b></td>
                                    <td>=></td>
                                    <td><b>ПАРАМЕТРЫ ПКТ</b></td>
                                    <td>=></td>
                                    <td><b>ОБНОВЛЕНИЕ ВЕРСИИ</b></td>
                                    <td>=></td>
                                    <td><b>нажать F7</b></td>
                                </tr>
                            </table>
                        </font>
                        Появится надпись: Поступили обновления - 1 шт.
                        Нажать <b>Enter</b> и немного подождать.
                        После чего перезагрузить ПКТ и проконтроллировать обновление:
                        <font face='Ariel' size='2' color='white'>
                            <table align='center' valign='middle' bgcolor='red' width='100%%' border='2'>
                                <tr>
                                    <td><b>ФУНКЦИИ АДМИНИСТРАТОРА</b></td>
                                    <td>=></td>
                                    <td><b>ПАРАМЕТРЫ ПКТ</b></td>
                                    <td>=></td>
                                    <td><b>ИНФОРМАЦИЯ О ПАКЕТЕ</b></td>
                                </tr>
                            </table>
                        </font>
                        <center>После обновления версии обязательно сообщите
                        об этом прогаммистам РУПС
                        <br>в чат либо по телефрну <b>4 - 45 - 17</b>.
                        &nbsp;&nbsp;&nbsp;&nbsp;<b>С П А С И Б О !</b></center>
                    </td></tr>
                </table>
            </dd>
        </dl>
        '''
    return html % (dateget, description, datefrom, dateto,)
###


### пока не используется
def html_DefList(title, text):
    html = u'''
        <dl>
            <dt><b>%s</b></dt>
            <dd><table align='justify'><tr><td>%s</td></tr></table></dd>
        </dl>
        '''
    return html % (title, text,)
###


### >
def html_Confirm(checkbox='', space='<hr>'):
    html_Btn = u'''
        <html>
            <body>
                %s
                <center>
                    <table align='center' valign='middle'>
                        %s
                        <tr>
                            <td>
                                <wxp module='wx' class='Button' width='100'>
                                    <param name='label' value='OK'>
                                    <param name='id'    value='ID_OK'>
                                </wxp>
                            </td>
                        </tr>
                    </table>
                </center>
            </body>
        </html>
        '''
    html_CheckBox = u'''
        <tr>
            <td>
                <wxp module='wx' class='CheckBox'>
                    <param name='label' value='%s'>
                    <param name='id'    value='10'>
                </wxp>
            </td>
        </tr>
        '''
    if checkbox:
        return html_Btn % (space, html_CheckBox % checkbox,)
    else:
        return html_Btn % (space, u'',)
###


### >
def html_SDO(columns):
    html = u'''
        <p>
        <font face='Ariel' size='4'>
            <table bgcolor='silver' width='100%%' cellspacing='2' cellpadding='20' border='2'>
                <tr>
                    %s
                </tr>
            </table>
        </font>
        '''
    return html % columns
###


### >
def html_NotImplemented():
    html = u'''
        <html>
            <body>
                <h2 align='center'>
                    Не реализовано
                </h2>
            <body>
        </html>
        '''
    return html
###


### !!!
def html_BQuote(text, factor=1):
    html  = u'%s'
    quote = u'<blockquote>%s</blockquote>'
    for i in xrange(factor):
        html = html % quote
    return html % text
###


### !!!
def html_HChoice(*args):
    table = u'''
        <table align='left' valign='middle'>
            %s
        </table>
        '''
    return table % ' '.join(args)
###


### !!!
def html_HItem(func, image, text):
    html = u'''
        <a href='%s'>
            <tr>
                <td>
                    <img src='%s'>
                </td>
                <td>
                    <font color='blue'><i>%s</i></font>
                </td>
            </tr>
        </a>
        '''
    return html % (func, image, text,)
###


### !!!
def html_Section(caption, lines):
    html = u'''
        <h3>
            <font face='Ariel' color='#778899'> <--!LightSlateGray-->
                %s
            </font>
        </h3>
        <ul>
            %s
        </ul>
        '''
    return html % (caption, lines,)
###
