import os


def getFileSize(filePath: str):
    fsize = os.path.getsize(filePath)
    if fsize < 1024:
        return (round(fsize, 2), 'Byte')
    else:
        KBX = fsize/1024
        if KBX < 1024:
            return (round(KBX, 2), 'K')
        else:
            MBX = KBX / 1024
            if MBX < 1024:
                return (round(MBX, 2), 'M')
            else:
                return (round(MBX / 1024), 'G')


def getFileSizeDesc(filePath: str):
    filesize = getFileSize(filePath)
    return str(filesize[0]) + filesize[1]


def getFileName(filePath: str, withExt=False):
    fileName = os.path.basename(filePath)
    if not withExt:
        print(fileName.split('.'))
        list = fileName.split('.')
        return list[0]
    return fileName


if __name__ == '__main__':
    getFileName('C:/Users/yiwei/cz_126.mp4')
