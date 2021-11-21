from ftplib import FTP

class DownloadData(object):
    def __init__(self, destination, name):
        self.audioSourceFolder = "recordings/"
        self.videoSourceFolder = "videoRecords/"
        self.androidSourceFolder = "ExperimentONE/video/"
        self.destinationFolder = destination + '/'
        self.pepperAdres = "192.168.1.100"
        self.pepperPort = 2121
        self.tapletAdres = "192.168.1.101"
        self.tabletPort = 2221
        self.name = name
        self.pepperFTP = FTP()
        self.tabletFTP = FTP()
        self.initializeFTPConections()

    def initializeFTPConections(self):
        self.pepperFTP.connect(self.pepperAdres, self.pepperPort)
        self.pepperFTP.login()
        self.tabletFTP.connect(self.tapletAdres, self.tabletPort)
        self.tabletFTP.login()

    def close(self):
        self.pepperFTP.quit()
        self.tabletFTP.quit()

    def download(self):
        print "downloading audio file"
        self.pepperFTP.cwd(self.audioSourceFolder)
        self.pepperFTP.retrbinary('RETR ' + self.name + '.wav',
                                  open(self.destinationFolder + self.name + '.wav', 'wb').write)
        self.pepperFTP.delete(self.name + '.wav')

        print "done"
        print "downloading video file"
        self.pepperFTP.cwd("/")

        self.pepperFTP.cwd(self.videoSourceFolder)
        self.pepperFTP.retrbinary('RETR ' + self.name + '.avi',
                                  open(self.destinationFolder + self.name + '.avi', 'wb').write)
        self.pepperFTP.delete(self.name + '.avi')

        print "done"
        print "downloading av file"
        self.tabletFTP.cwd(self.androidSourceFolder)
        self.tabletFTP.retrbinary('RETR ' + 'videooutput_' + self.name + '.mp4',
                                  open(self.destinationFolder + 'videooutput_' + self.name + '.mp4', 'wb').write)
        self.tabletFTP.delete('videooutput_' + self.name + '.mp4')
        print "done"


if __name__ == '__main__':
    downloadData = DownloadData(".","exp1")
    downloadData.download()
    downloadData.close()