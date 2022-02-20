import sys
import math

import requests

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from io import BytesIO
from PIL import Image, ImageQt

from main_ui import Ui_MainWindow

from Samples import geocoder, business

'''from Samples import geocoder'''


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

        self.map_types = {'гибрид': 'sat,skl',
                          'карта': 'map',
                          'спутник': 'sat'}

        self.map_type = self.map_types[self.comboBox_map_type.currentText()]

        self.show_map(self.ll, self.spn, self.map_type)

        self.comboBox_map_type.currentTextChanged.connect(self.change_map_type)

        self.btn_search_place.clicked.connect(self.search_place_with_name)

        self.btn_reset_place.clicked.connect(self.reset)

        self.index_point = False

        self.check_index.stateChanged.connect(self.change_address_index)

    def keyPressEvent(self, event):
        """Перемещение по карте"""
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

    def change_address_index(self):
        if self.index_point:
            self.obj_address.setPlainText(self.current_address)
            self.index_point = False
        else:
            try:
                self.index_point = True
                toponym = geocoder.geocode(f'{self.point_coords[0]},{self.point_coords[1]}')
                self.current_index = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
                text = f'{self.current_address}, {self.current_index}'
                self.obj_address.setPlainText(text)
            except Exception:
                pass

    def change_map_type(self):
        """Меняет тип карты"""
        self.ll = f'{self.ll_size[0]},{self.ll_size[1]}'

        self.spn = (str(self.spn_size) + ',' + str(self.spn_size))

        self.map_type = self.map_types[self.comboBox_map_type.currentText()]

        self.show_map(self.ll, self.spn, self.map_type)

        self.comboBox_map_type.clearFocus()

    def search_place_with_name(self):
        """Находит место по названию в поле для ввода"""

        if self.input_place_name.text():
            self.ll, self.spn = geocoder.get_ll_span(self.input_place_name.text())  # адрес
            self.spn_size = min(list(map(float, self.spn.split(','))))
            self.ll_size = list(map(float, self.ll.split(',')))

            self.point_coords = self.ll_size.copy()

            toponym = geocoder.geocode(self.ll)  # получение данных об объекте
            self.current_address = toponym['metaDataProperty']['GeocoderMetaData']['text']
            if self.index_point:
                try:
                    self.current_index = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
                    text = f'{self.current_address}, {self.current_index}'
                    self.obj_address.setPlainText(text)
                except Exception:
                    self.obj_address.setPlainText(self.current_address)
            else:
                self.obj_address.setPlainText(self.current_address)

            self.show_map(self.ll, self.spn, self.map_type)

            self.btn_search_place.clearFocus()

    def reset(self):
        """Сброс всех поисковых результатов"""
        self.point_coords = None
        self.current_address = None

        self.obj_address.clear()
        self.input_place_name.setText('')

        self.show_map(self.ll, self.spn, self.map_type)

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

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            if self.map_pic.pos().x() <= event.pos().x() <= self.map_pic.pos().x() + self.map_pic.width() and \
                    self.map_pic.pos().y() <= event.pos().y() <= self.map_pic.pos().y() + self.map_pic.height():
                # print(math.radians(self.ll_size[1]), math.radians(self.ll_size[0]))
                # x = (event.pos().x() - self.map_pic.pos().x() - self.map_pic.width() // 2) * \
                #     self.spn_size * 3.45 / 650 + self.ll_size[0]
                # y = (event.pos().y() - self.map_pic.pos().y() - self.map_pic.height() // 2) * \
                #     self.spn_size * 1.47 / 450 * (-1) + self.ll_size[1]
                x = (event.pos().x() - self.map_pic.pos().x() - self.map_pic.width() // 2) * \
                    self.spn_size * 2.69 / math.sin(math.radians(self.ll_size[1])) / self.map_pic.width() + \
                    self.ll_size[0]
                y = (event.pos().y() - self.map_pic.pos().y() - self.map_pic.height() // 2) * \
                    self.spn_size * 0.925 / math.cos(math.radians(self.ll_size[1])) / self.map_pic.height() * (-1) + \
                    self.ll_size[1]
                # разбор этих двух формул:

                params = {
                    'pt': f'{x},{y},comma'
                }

                self.point_coords = [x, y]

                self.show_map(f'{self.ll_size[0]},{self.ll_size[1]}', f'{self.spn_size},{self.spn_size}',
                              map_type=self.map_type, params=params)

                toponym = geocoder.geocode(f'{x},{y}')
                self.current_address = toponym['metaDataProperty']['GeocoderMetaData']['text']
                if self.index_point:
                    try:
                        self.current_index = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
                        text = f'{self.current_address}, {self.current_index}'
                        self.obj_address.setPlainText(text)
                    except Exception:
                        self.obj_address.setPlainText(self.current_address)
                else:
                    self.obj_address.setPlainText(self.current_address)

        elif event.button() == Qt.RightButton:
            if self.map_pic.pos().x() <= event.pos().x() <= self.map_pic.pos().x() + self.map_pic.width() and \
                    self.map_pic.pos().y() <= event.pos().y() <= self.map_pic.pos().y() + self.map_pic.height():
                x = (event.pos().x() - self.map_pic.pos().x() - self.map_pic.width() // 2) * \
                    self.spn_size * 2.69 / math.sin(math.radians(self.ll_size[1])) / self.map_pic.width() + \
                    self.ll_size[0]
                y = (event.pos().y() - self.map_pic.pos().y() - self.map_pic.height() // 2) * \
                    self.spn_size * 0.925 / math.cos(math.radians(self.ll_size[1])) / self.map_pic.height() * (-1) + \
                    self.ll_size[1]
                # разбор этих двух формул:

                params = {
                    'pt': f'{x},{y},comma'
                }

                self.show_map(f'{self.ll_size[0]},{self.ll_size[1]}', f'{self.spn_size},{self.spn_size}',
                              map_type=self.map_type, params=params)

                organization = geocoder.geocode(f'{x},{y}')['metaDataProperty']['GeocoderMetaData']
                org_name = organization['text']

                org = business.find_business(f'{x},{y}', '0.00045,0.00045', org_name)  # 0.00045 - ~50м в градусах

                if org:
                    self.current_address = org['properties']['CompanyMetaData']['address']
                    if self.index_point:
                        try:
                            self.current_index = organization['Address']['postal_code']
                            text = f"{org['properties']['CompanyMetaData']['name']} - {self.current_address}, {self.current_index}"
                            self.obj_address.setPlainText(text)
                        except Exception:
                            self.obj_address.setPlainText(
                                f"{org['properties']['CompanyMetaData']['name']} - {self.current_address}")
                    else:
                        self.obj_address.setPlainText(f"{org['properties']['CompanyMetaData']['name']} - {self.current_address}")

                else:
                    print('ничего не найдено')

                self.point_coords = [x, y]


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
