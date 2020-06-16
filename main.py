# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from pytube import YouTube
import datetime
import os
import urllib.request

# load ui file
ui_MainWindow, qmain_window = uic.loadUiType(os.path.join("app.ui"))


class ytdl_ui(qmain_window, ui_MainWindow):
    def __init__(self, parent=None):
        super(ytdl_ui, self).__init__(parent)
        self.setupUi(self)
        
        self.infoVideoWidget.hide()
        self.infoPlaylistWidget.hide()
        self.downloadWidget.hide()
        
        self.searchButton.clicked.connect(self.search)
        self.linkLineEdit.textChanged.connect(self.editLink)
        self.typeCombo.currentIndexChanged.connect(self.addFormat)
        self.downloadButton.clicked.connect(self.download)
        self.quickdownloadButton.clicked.connect(self.downloadHighest)
        self.audioButton.clicked.connect(lambda:self.btnstate("audio"))
        self.videoButton.clicked.connect(lambda:self.btnstate("video"))
        
    def update_infos(self):
        # Get link
        link = self.linkLineEdit.text()
        self.yt = YouTube(link)
        # Set title text
        self.videotitleLabel.setText(self.yt.title)
        self.videotitleLabel.adjustSize()
        # Set author text
        self.videoauthorLabel.setText(self.yt.author)
        self.videoauthorLabel.adjustSize()
        # Set length text
        self.videolengthLabel.setText(str(datetime.timedelta(seconds=self.yt.length)))
        self.videolengthLabel.adjustSize()
        # Set views text
        self.videoviewsLabel.setText(str(self.yt.views))
        self.videoviewsLabel.adjustSize()
        # Set ratings text
        self.videoratingsLabel.setText("{:.2f}/5.00".format(self.yt.rating))
        # Set description text
        self.videodescriptionLabel.setText(str(self.yt.description))
        self.videodescriptionLabel.adjustSize()
        # Set thumbnail
        data = urllib.request.urlopen(self.yt.thumbnail_url).read()
        self.thumbnail = QtGui.QImage()
        self.thumbnail.loadFromData(data)
        pixmap = QtGui.QPixmap(self.thumbnail).scaled(self.thumbnailLabel.width(), self.thumbnailLabel.height(), QtCore.Qt.KeepAspectRatio)
        self.thumbnailLabel.setPixmap(pixmap)
        
    def search(self):
        movie = QtGui.QMovie("loader.gif")
        self.statusLabel.setMovie(movie)
        movie.start()
        self.update_infos()
        # Check link_type TODO
        link_type = "video"
        if link_type == "video":
            self.infoVideoWidget.show()
        self.downloadWidget.show()

        # Set possibilities
        types = []
        self.typeCombo.clear()
        
        for s in self.yt.streams:
            if s.type not in types:
                types.append(s.type)
        
        self.typeCombo.addItems([t.capitalize() for t in sorted(types)])
        
        self.addFormat()
        
        movie.stop()
        self.statusLabel.setText("Done!")
        self.statusLabel.adjustSize()
        
        
    def selectStream(self):
        ct = str(self.typeCombo.currentText()) # Current type
        cf = self.formatCombo.currentText() # Current format
        if ct == "Audio":
            cmt, cbr = cf.split(', ') # Current mime type and bitrate
            self.stream = self.yt.streams.filter(type=ct.lower(), subtype=cmt, abr=cbr).first()
        elif ct == "Video":
            cres, cfps, cmt = cf.split(', ') # Current res and fps
            cfps = int(cfps.split('fps')[0])
            self.stream = self.yt.streams.filter(type=ct.lower(), resolution=cres, fps=cfps, subtype=cmt).first()
        

    def download(self):
        self.statusLabel.setText("Downloading...")
        self.selectStream()
        print(self.stream)
        self.sizeLabel.setText(self.sizeFormat(self.stream.filesize_approx))
        path = os.getcwd()
        fname = "{} - {}".format(self.videoauthorLabel.text(), self.videotitleLabel.text())
        self.stream.download(output_path=os.path.join(path, "Downloads"), filename=fname)
        self.statusLabel.setText("Done!")
        
        
    def downloadHighest(self):
        self.statusLabel.setText("Downloading...")
        self.update_infos()
        if self.audioButton.isChecked():
            self.stream = self.yt.streams.get_audio_only()
        elif self.videoButton.isChecked():
            self.stream = self.yt.streams.get_highest_resolution()
        if self.stream == None:
            self.statusLabel.setText("No stream for selected type")
            
        self.sizeLabel.setText(self.sizeFormat(self.stream.filesize_approx))
        path = os.getcwd()
        fname = "{} - {}".format(self.videoauthorLabel.text(), self.videotitleLabel.text())
        self.stream.download(output_path=os.path.join(path, "Downloads"), filename=fname)
        self.statusLabel.setText("Done!")
        
        
    def editLink(self, text):
        self.linkLineEdit.setText(text)
        
    def btnstate(self, stype:str):
        if stype == "audio":
            self.audioButton.setChecked(1)
            self.videoButton.setChecked(0)
        elif stype == "video":
            self.audioButton.setChecked(0)
            self.videoButton.setChecked(1)
        
    def addFormat(self):    # Set formats for current type
        formats = []
        self.formatCombo.clear()
        ct = str(self.typeCombo.currentText()) # Current type
        for s in self.yt.streams.filter(type=ct.lower(), adaptive=1):
            if ct == "Audio":
                frmt = (s.mime_type.split("/")[-1], s.abr)
            elif ct == "Video":
                frmt = (s.resolution, f"{s.fps}fps", s.mime_type.split("/")[-1])
            else:
                frmt = "No format available"
            if frmt not in formats:
                formats.append(', '.join(frmt))

        self.formatCombo.addItems([f for f in sorted(formats)])
        
    def sizeFormat(self, num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return "Approx. {0:.2f}{1}b".format(num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
        
if __name__ == "__main__":
    import sys
    MainEvntThread = QtWidgets.QApplication([])
    ui = ytdl_ui(None)
    ui.showMinimized()
    MainEvntThread.exec()
