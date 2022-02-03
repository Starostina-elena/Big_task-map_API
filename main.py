import sys

import requests

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from io import BytesIO
from PIL import Image, ImageQt

from main_ui import Ui_MainWindow


class Map(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.spn_size = 0.065

        self.ll_size = [46.034158, 51.533103]

        self.ll = f'{self.ll_size[0]},{self.ll_size[1]}'

        self.spn = (str(self.spn_size) + ',' + str(self.spn_size))

        self.map_types = {'гибрид': 'sat,skl',
                          'карта': 'map',
                          'спутник': 'sat'}

        self.map_type = self.map_types[self.comboBox_map_type.currentText()]

        self.comboBox_map_type.currentTextChanged.connect(self.change_map_type)

        self.show_map(self.ll, self.spn, self.map_type)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.spn_size /= 2
            if self.spn_size < 0.0005078125:
                self.spn_size = 0.0005078125
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            map_type = self.map_types[self.comboBox_map_type.currentText()]
            self.show_map(ll, spn, map_type)

        elif event.key() == Qt.Key_PageDown:
            self.spn_size *= 2
            if self.spn_size > 66.56:
                self.spn_size = 66.56
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            map_type = self.map_types[self.comboBox_map_type.currentText()]
            self.show_map(ll, spn, map_type)

        elif event.key() == Qt.Key_Up:
            self.ll_size[1] += self.spn_size * 0.6
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            map_type = self.map_types[self.comboBox_map_type.currentText()]
            self.show_map(ll, spn, map_type)

        elif event.key() == Qt.Key_Down:
            self.ll_size[1] -= self.spn_size * 0.6
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            map_type = self.map_types[self.comboBox_map_type.currentText()]
            self.show_map(ll, spn, map_type)

        elif event.key() == Qt.Key_Right:
            self.ll_size[0] += self.spn_size * 0.6
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            map_type = self.map_types[self.comboBox_map_type.currentText()]
            self.show_map(ll, spn, map_type)

        elif event.key() == Qt.Key_Left:
            self.ll_size[0] -= self.spn_size * 0.6
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            map_type = self.map_types[self.comboBox_map_type.currentText()]
            self.show_map(ll, spn, map_type)

    def change_map_type(self):
        self.ll = f'{self.ll_size[0]},{self.ll_size[1]}'

        self.spn = (str(self.spn_size) + ',' + str(self.spn_size))

        self.map_type = self.map_types[self.comboBox_map_type.currentText()]

        self.show_map(self.ll, self.spn, self.map_type)

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
