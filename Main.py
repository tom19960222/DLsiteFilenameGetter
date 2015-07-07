# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QTableWidgetItem
from MainWindow import Ui_DLSiteGetWindow
from bs4 import BeautifulSoup
import requests
import json

app = QApplication(sys.argv)

baseWindow = QMainWindow()
UI = Ui_DLSiteGetWindow()

def getDLSiteDataByNumber(number):
    req = requests.get("http://www.dlsite.com/maniax/work/=/product_id/" + number + ".html")
    print("Getting " + req.url)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, "html.parser")
    data = dict()

    data['work_name'] = soup.find(id='work_name').text
    data['maker_name'] = soup.find_all(class_='maker_name')[0].a.span.text

    try:
        data['maker_website'] = soup.find(id='work_maker').tr.next_sibling.next_sibling.td.a.get('href')  # There is a damn '\n'
    except AttributeError:
        data['maker_website'] = ''

    data['publish_date'] = soup.find(id='work_outline').tr.td.a.text.replace('年', '/').replace('月', '/').replace('日', '')
    data['publish_date_for_filename'] = soup.find(id='work_outline').tr.td.a.text.replace('年', '').replace('月', '').replace('日', '')[2:]

    data['series'] = ''
    for item in soup.find(id='work_outline').tr.next_siblings:
        if hasattr(item, 'th') and item.th.string[0:5] == 'シリーズ名':
            data['series'] = item.td.text

    data['age_restrictions'] = soup.find_all(class_='work_genre')[0].text
    data['work_type'] = list()
    for item in soup.find_all(class_='work_genre')[1]:
        data['work_type'].append(item.string)
    data['file_type'] = list()
    for item in soup.find_all(class_='work_genre')[2]:
        data['file_type'].append(item.text)
    data['supported_OS'] = list()
    for item in soup.find_all('dl'):
        if item.get('class') is not None and item['class'][0].__contains__('os_'):
            data['supported_OS'].append(item.dt.text+' '+item.dd.text)

    data['others'] = list()
    try:
        for item in soup.find_all(class_='work_genre')[3]:
            data['others'].append(item.text)
    except IndexError:
        pass  # No other tags.

    data['tags'] = list()
    for item in soup.find_all(class_='main_genre')[0]:
        if item.string != '\xa0':  # 'nbsp;'
            data['tags'].append(item.string)

    APIreq = requests.post("http://www.dlsite.com/maniax/product/info/ajax?product_id=" + number)
    APIreq.encoding = 'utf-8'
    APIjson = json.loads(APIreq.text)
    data['dl_count'] = APIjson[number]['dl_count']
    data['rate_average'] = APIjson[number]['rate_average']
    data['rate_count'] = APIjson[number]['rate_count']
    data['review_count'] = APIjson[number]['review_count']
    data['price'] = APIjson[number]['price']
    return data

def putDataOnTable(data):
    UI.tableParameters.setItem(0, 1, QTableWidgetItem(UI.txtInputNumber.text()))
    UI.tableParameters.setItem(1, 1, QTableWidgetItem(data['work_name']))
    UI.tableParameters.setItem(2, 1, QTableWidgetItem(str(data['dl_count'])))
    UI.tableParameters.setItem(3, 1, QTableWidgetItem(data['maker_name']))
    UI.tableParameters.setItem(4, 1, QTableWidgetItem(data['maker_website']))
    UI.tableParameters.setItem(5, 1, QTableWidgetItem(data['publish_date_for_filename']))
    UI.tableParameters.setItem(6, 1, QTableWidgetItem(data['series']))
    UI.tableParameters.setItem(7, 1, QTableWidgetItem(data['age_restrictions']))
    work_type_str = str()
    for item in data['work_type']:
        work_type_str += item + ', '
    UI.tableParameters.setItem(8, 1, QTableWidgetItem(work_type_str[0:work_type_str.__len__()-2]))
    file_type_str = str()
    for item in data['file_type']:
        file_type_str += item + ', '
    UI.tableParameters.setItem(9, 1, QTableWidgetItem(file_type_str[0:file_type_str.__len__()-2]))
    supported_os_str = str()
    for item in data['supported_OS']:
        supported_os_str += item + ', '
    UI.tableParameters.setItem(10, 1, QTableWidgetItem(supported_os_str[0:supported_os_str.__len__()-2]))

    UI.tableParameters.resizeColumnsToContents()

def replaceTagWithContent(strWithTag, tag_dataDict):
    for key in tag_dataDict.keys():
        strWithTag = strWithTag.replace('{{'+key+'}}', tag_dataDict[key])
    return strWithTag

def btnGetData_Click():
    if UI.txtInputNumber.text()[0:2] != 'RJ':
        UI.txtInputNumber.setText("Only ID start with RJ supported!")
    data = getDLSiteDataByNumber(UI.txtInputNumber.text())
    putDataOnTable(data)
    print(data)

def btnDoReplace_Click():
    data = dict()
    for i in range(0, UI.tableParameters.rowCount()):
        if UI.tableParameters.item(i, 0) is not None:
            data[UI.tableParameters.item(i, 0).text()] = UI.tableParameters.item(i, 1).text()
    UI.txtOutput.setText(UI.comboPrefix.currentText() + replaceTagWithContent(UI.txtReplaceFormat.text(), data) + UI.comboPostfix.currentText())

def initUI():
    baseWindow.setWindowTitle("DLsite infomation -> filename")
    UI.btnGetData.clicked.connect(btnGetData_Click)
    UI.txtInputNumber.returnPressed.connect(btnGetData_Click)
    UI.btnDoReplace.clicked.connect(btnDoReplace_Click)

    UI.tableParameters.setItem(0, 0, QTableWidgetItem('work_id'))
    UI.tableParameters.setItem(1, 0, QTableWidgetItem('work_name'))
    UI.tableParameters.setItem(2, 0, QTableWidgetItem('dl_count'))
    UI.tableParameters.setItem(3, 0, QTableWidgetItem('maker_name'))
    UI.tableParameters.setItem(4, 0, QTableWidgetItem('maker_website'))
    UI.tableParameters.setItem(5, 0, QTableWidgetItem('publish_date_for_filename'))
    UI.tableParameters.setItem(6, 0, QTableWidgetItem('series'))
    UI.tableParameters.setItem(7, 0, QTableWidgetItem('age_restrictions'))
    UI.tableParameters.setItem(8, 0, QTableWidgetItem('work_type'))
    UI.tableParameters.setItem(9, 0, QTableWidgetItem('file_type'))
    UI.tableParameters.setItem(10, 0, QTableWidgetItem('supported_os'))
    UI.tableParameters.resizeColumnsToContents()

    prefixList = list()
    prefixList.append('')
    prefixList.append("(同人ゲーム) ")
    prefixList.append("(同人アニメ) ")
    prefixList.append("(18禁ゲーム) ")
    prefixList.append("(18禁アニメ) ")
    UI.comboPrefix.addItems(prefixList)

    postfixList = list()
    postfixList.append('')
    postfixList.append('.zip')
    postfixList.append('.rar')
    postfixList.append('.7z')
    UI.comboPostfix.addItems(postfixList)

    UI.txtReplaceFormat.setText("[{{publish_date_for_filename}}][{{work_id}}][{{maker_name}}] {{work_name}}")

def main():
    window = UI.setupUi(baseWindow)
    initUI()
    # window.resize(250, 150)
    # window.move(300, 300)
    # window.setWindowTitle('Simple')
    # window.show()
    baseWindow.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    # print(getDLSiteDataByNumber('RJ158352'))
    main()