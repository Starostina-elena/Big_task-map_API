import sys

import requests

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap

from io import BytesIO
from PIL import Image, ImageQt

from main_ui import Ui_MainWindow


class Map(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.show_map('46.034158,51.533103', '0.065,0.065')

    def show_map(self, ll, spn, map_type='map', params=None):
        # ll и spn в формате "<число>,<число>" (да-да, для spn тоже два числа),
        # map_type - строка, params - словарь, все ключи и значения - строки

        map_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={map_type}&size=650,450"

        response = requests.get(map_request, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

        # установка полученного изображения
        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))
        self.map_pic.setPixmap(QPixmap.fromImage(self.img))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
