import sys

import requests

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from io import BytesIO
from PIL import Image, ImageQt

from main_ui import Ui_MainWindow

from Samples import geocoder


class Map(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.spn_size = 0.065
        self.ll_size = [46.034158, 51.533103]
        self.ll = f'{self.ll_size[0]},{self.ll_size[1]}'
        self.spn = (str(self.spn_size) + ',' + str(self.spn_size))

        self.point_coords = None  # хранит координаты метки
        self.current_address = None

        self.show_map(self.ll, self.spn)

        self.btn_search_place.clicked.connect(self.search_place_with_name)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.spn_size /= 2
            if self.spn_size < 0.00005078125:
                self.spn_size = 0.00005078125
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            self.show_map(ll, spn)

        elif event.key() == Qt.Key_PageDown:
            self.spn_size *= 2
            if self.spn_size > 66.56:
                self.spn_size = 66.56
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            self.show_map(ll, spn)

        elif event.key() == Qt.Key_Up:
            self.ll_size[1] += self.spn_size * 0.6
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            self.show_map(ll, spn)

        elif event.key() == Qt.Key_Down:
            self.ll_size[1] -= self.spn_size * 0.6
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            self.show_map(ll, spn)

        elif event.key() == Qt.Key_Right:
            self.ll_size[0] += self.spn_size * 0.6
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            self.show_map(ll, spn)

        elif event.key() == Qt.Key_Left:
            self.ll_size[0] -= self.spn_size * 0.6
            ll = f'{self.ll_size[0]},{self.ll_size[1]}'
            spn = (str(self.spn_size) + ',' + str(self.spn_size))
            self.show_map(ll, spn)

    def search_place_with_name(self):
        """Находит место по названию в поле для ввода"""

        if self.input_place_name.text():
            self.ll, self.spn = geocoder.get_ll_span(self.input_place_name.text())
            self.spn_size = min(list(map(float, self.spn.split(','))))
            self.ll_size = list(map(float, self.ll.split(',')))

            self.point_coords = self.ll_size.copy()

            toponym = geocoder.geocode(self.ll)  # получение данных об объекте
            self.current_address = toponym['metaDataProperty']['GeocoderMetaData']['text']
            self.obj_address.setText(self.current_address)

            self.show_map(self.ll, self.spn)

            self.btn_search_place.clearFocus()

    def show_map(self, ll, spn, map_type='map', params=None):
        # ll и spn в формате "<число>,<число>" (да-да, для spn тоже два числа),
        # map_type - строка, params - словарь, все ключи и значения - строки

        map_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={map_type}&size=650,450"

        if not params and self.point_coords:
            params = {
                'pt': f'{self.point_coords[0]},{self.point_coords[1]},comma'
            }
        if params and self.point_coords and 'pt' not in params:
            params['pt'] = f'{self.point_coords[0]},{self.point_coords[1]},comma'

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
