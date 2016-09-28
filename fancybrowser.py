#!/usr/bin/env python

#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited
## Copyright (C) 2010 Hans-Peter Jansen <hpj@urpla.net>.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
###########################################################################
from PyQt5 import QtWidgets

from PyQt5.QtCore import QFile, QIODevice, Qt, QTextStream, QUrl
from PyQt5.QtWidgets import (QAction, QApplication, QLineEdit, QMainWindow,
        QSizePolicy, QStyle, QTextEdit)
from PyQt5.QtNetwork import QNetworkProxyFactory, QNetworkRequest
from PyQt5.QtWebKitWidgets import QWebPage, QWebView



import jquery_rc


class IncompleteSiteDetailError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        # self.expression = expression
        self.message = message

class SiteDetail(object):
    def __init__(self, **kwargs):
        try:
            self.init_url = kwargs['init_url']
            self.login_name = kwargs['login_name']
            self.login_name_dom_path = kwargs['login_name_dom_path']
            self.login_password = kwargs['login_password']
            self.login_password_dom_path = kwargs['login_password_dom_path']
            self.login_button_dom_path = kwargs['login_button_dom_path']
        except KeyError as e:
            raise IncompleteSiteDetailError('{} not found in site detail kwargs'.format(e))


class WebView(object):
    def __init__(self, main_window, index, site_details):
        self.view_signal_connected_to_slot = False
        self.index = index
        self.site_details = site_details
        self.view = QWebView(main_window)
        self.view.load(QUrl(site_details.init_url))
        if main_window.default_tab == index:
            self.view.loadFinished.connect(main_window.adjustLocation)
            self.view.titleChanged.connect(main_window.adjustTitle)
            self.view.loadProgress.connect(main_window.setProgress)
            self.view.loadFinished.connect(main_window.finishLoading)
            self.view.linkClicked.connect(main_window.loadClickedLink)
            self.view_signal_connected_to_slot = True

    def get_web_view(self):
        return self.view


class MainWindow(QMainWindow):
    # def viewSource(self):
    #     accessManager = self.view.page().networkAccessManager()
    #     request = QNetworkRequest(self.view.url())
    #     reply = accessManager.get(request)
    #     reply.finished.connect(self.slotSourceDownloaded)
    #
    # def slotSourceDownloaded(self):
    #     reply = self.sender()
    #     self.textEdit = QTextEdit()
    #     self.textEdit.setAttribute(Qt.WA_DeleteOnClose)
    #     self.textEdit.show()
    #     self.textEdit.setPlainText(QTextStream(reply).readAll())
    #     self.textEdit.resize(600, 400)
    #     reply.deleteLater()
    def adjustLocation(self):
        self.locationEdit.setText(self.view.url().toString())

    def changeLocation(self):
        url = QUrl.fromUserInput(self.locationEdit.text())
        self.view.load(url)
        self.view.setFocus()

    def change_self_web_view(self, index):
        self.web_view = self.web_views[index]
        self.view = self.web_views[index].get_web_view()

        if self.web_views[index].view_signal_connected_to_slot:
            self.view.loadFinished.disconnect(self.adjustLocation)
            self.view.titleChanged.disconnect(self.adjustTitle)
            self.view.loadProgress.disconnect(self.setProgress)
            self.view.loadFinished.disconnect(self.finishLoading)
        self.view.loadFinished.connect(self.adjustLocation)
        self.view.titleChanged.connect(self.adjustTitle)
        self.view.loadProgress.connect(self.setProgress)
        self.view.loadFinished.connect(self.finishLoading)
        self.adjustLocation()
        self.adjustTitle()


        # TODO add cookie support(cookie will be prebuilt)
        # FIXME cannot click link on twitter

        # FIXME percentage sill shown when page stop
        # The above issue can be fixed by making a progess variable in WebView class and show that when clicked

        # FIXME Reload not working I guess

    def loadClickedLink(self, q_url):
        self.view.load(q_url)
        self.view.setFocus()

    def __init__(self, *sites_details):
        super(MainWindow, self).__init__()

        self.progress = 0
        self.default_tab = 0

        fd = QFile(":/jquery.min.js")

        if fd.open(QIODevice.ReadOnly | QFile.Text):
            self.jQuery = QTextStream(fd).readAll()
            fd.close()
        else:
            self.jQuery = ''

        QNetworkProxyFactory.setUseSystemConfiguration(True)

        # # Add tabbed dock
        # wrufesh_dock = QtWidgets.QDockWidget('Wrufesh')
        # wroshan_dock = QtWidgets.QDockWidget('Wroshan')
        # self.addDockWidget(Qt.TopDockWidgetArea, wrufesh_dock)
        # self.addDockWidget(Qt.TopDockWidgetArea, wroshan_dock)

        self.web_views = []
        self.tabwidget = QtWidgets.QTabWidget(self)
        self.tabwidget.setTabShape(1)

        self.tabwidget.tabBarClicked.connect(self.change_self_web_view)
        self.setTabPosition(Qt.TopDockWidgetArea, self.tabwidget.East)
        for i, site_deatils in enumerate(sites_deatils):
            web_view = WebView(self, i, site_deatils)
            self.web_views.append(web_view)
            self.tabwidget.addTab(web_view.get_web_view(), 'New Tab')
        self.web_view = self.web_views[0]
        self.view = self.web_views[0].get_web_view()
        #
        # # End  Add tabbed dock

        # self.view = QWebView(self)
        # self.view.load(url)
        # self.view.loadFinished.connect(self.adjustLocation)
        # self.view.titleChanged.connect(self.adjustTitle)
        # self.view.loadProgress.connect(self.setProgress)
        # self.view.loadFinished.connect(self.finishLoading)
        #
        self.locationEdit = QLineEdit(self)
        self.locationEdit.setSizePolicy(QSizePolicy.Expanding,
                self.locationEdit.sizePolicy().verticalPolicy())
        self.locationEdit.returnPressed.connect(self.changeLocation)

        self.find_product = QLineEdit(self)
        self.find_product.setSizePolicy(QSizePolicy.Expanding,
                                        self.find_product.sizePolicy().verticalPolicy())
        self.find_product.returnPressed.connect(self.findProduct)

        self.product_finder_label_widget = QtWidgets.QLabel('\t\t\t\t{}'.format('Search Product: '), self)

        toolBar = self.addToolBar("Navigation")
        toolBar.addAction(self.view.pageAction(QWebPage.Back))
        toolBar.addAction(self.view.pageAction(QWebPage.Forward))
        toolBar.addAction(self.view.pageAction(QWebPage.Reload))
        toolBar.addAction(self.view.pageAction(QWebPage.Stop))
        toolBar.addWidget(self.locationEdit)
        toolBar.addWidget(self.product_finder_label_widget)
        toolBar.addWidget(self.find_product)

        # viewMenu = self.menuBar().addMenu("&View")
        # viewSourceAction = QAction("Page Source", self)
        # viewSourceAction.triggered.connect(self.viewSource)
        # viewMenu.addAction(viewSourceAction)
        #
        # effectMenu = self.menuBar().addMenu("&Effect")
        # effectMenu.addAction("Highlight all links", self.highlightAllLinks)
        #
        # self.rotateAction = QAction(
        #         self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
        #         "Turn images upside down", self, checkable=True,
        #         toggled=self.rotateImages)
        # effectMenu.addAction(self.rotateAction)
        #
        # toolsMenu = self.menuBar().addMenu("&Tools")
        # toolsMenu.addAction("Remove GIF images", self.removeGifImages)
        # toolsMenu.addAction("Remove all inline frames",
        #         self.removeInlineFrames)
        # toolsMenu.addAction("Remove all object elements",
        #         self.removeObjectElements)
        # toolsMenu.addAction("Remove all embedded elements",
        #         self.removeEmbeddedElements)
        #
        # Tab
        # tabwidget = QtWidgets.QTabWidget(self)
        # self.setTabPosition(Qt.TopDockWidgetArea, tabwidget.East)
        # tabwidget.addTab(self.view, 'myself')
        # End Tab


        self.setCentralWidget(self.tabwidget)


    def findProduct(self):
        print('Finding Product')

    def adjustTitle(self):
        if 0 < self.progress < 100:
            self.setWindowTitle("%s (%s%%)" % (self.view.title(), self.progress))
        else:
            self.setWindowTitle(self.view.title())
        for i, web_view in enumerate(self.web_views):
            self.tabwidget.setTabText(i, web_view.get_web_view().title())

    def setProgress(self, p):
        self.progress = p
        self.adjustTitle()

    def finishLoading(self):
        self.progress = 100
        self.adjustTitle()
        self.view.page().mainFrame().evaluateJavaScript(self.jQuery)

        # self.rotateImages(self.rotateAction.isChecked())

    # def highlightAllLinks(self):
    #     code = """$('a').each(
    #                 function () {
    #                     $(this).css('background-color', 'yellow')
    #                 }
    #               )"""
    #     self.view.page().mainFrame().evaluateJavaScript(code)
    #
    # def rotateImages(self, invert):
    #     if invert:
    #         code = """
    #             $('img').each(
    #                 function () {
    #                     $(this).css('-webkit-transition', '-webkit-transform 2s');
    #                     $(this).css('-webkit-transform', 'rotate(180deg)')
    #                 }
    #             )"""
    #     else:
    #         code = """
    #             $('img').each(
    #                 function () {
    #                     $(this).css('-webkit-transition', '-webkit-transform 2s');
    #                     $(this).css('-webkit-transform', 'rotate(0deg)')
    #                 }
    #             )"""
    #
    #     self.view.page().mainFrame().evaluateJavaScript(code)
    #
    # def removeGifImages(self):
    #     code = "$('[src*=gif]').remove()"
    #     self.view.page().mainFrame().evaluateJavaScript(code)
    #
    # def removeInlineFrames(self):
    #     code = "$('iframe').remove()"
    #     self.view.page().mainFrame().evaluateJavaScript(code)
    #
    # def removeObjectElements(self):
    #     code = "$('object').remove()"
    #     self.view.page().mainFrame().evaluateJavaScript(code)
    #
    # def removeEmbeddedElements(self):
    #     code = "$('embed').remove()"
    #     self.view.page().mainFrame().evaluateJavaScript(code)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    # if len(sys.argv) > 1:
    #     url = QUrl(sys.argv[1])
    # else:
    sites_deatils = [
        SiteDetail(**{
            'init_url': 'https://www.dandh.com/',
            'login_name':'wrufesh',
            'login_name_dom_path':'wrufesh',
            'login_password':'wrufesh',
            'login_password_dom_path':'password',
            'login_button_dom_path':'button'
        }),
        SiteDetail(**{
            'init_url': 'http://buy.wynit.com/ce/',
            'login_name': 'wrufesh',
            'login_name_dom_path': 'wrufesh',
            'login_password': 'wrufesh',
            'login_password_dom_path': 'password',
            'login_button_dom_path': 'button'
        }),
        SiteDetail(**{
            'init_url': 'https://ec.synnex.com/',
            'login_name': 'wrufesh',
            'login_name_dom_path': 'wrufesh',
            'login_password': 'wrufesh',
            'login_password_dom_path': 'password',
            'login_button_dom_path': 'button'
        })
    ]
    # urls = [
    #     QUrl('https://www.dandh.com/'),
    #     QUrl('http://buy.wynit.com/ce/'),
    #     QUrl('https://ec.synnex.com/')
    # ]

    browser = MainWindow(*sites_deatils)
    browser.show()

    sys.exit(app.exec_())
