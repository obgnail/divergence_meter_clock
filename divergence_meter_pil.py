import random
import os
import time
import sys
from typing import Iterable, Callable
from PIL import Image, ImageOps, ImageQt
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QDesktopWidget

TYPE_CLOCK = 'clock'
TYPE_METER = 'meter'


class ImageOptionMixin:
    @staticmethod
    def concat_h(img_list):
        total_width = sum(img.width for img in img_list)
        max_height = max(img.height for img in img_list)

        dst = Image.new('RGB', (total_width, max_height))
        offset = 0
        for img in img_list:
            dst.paste(img, (offset, 0))
            offset += img.width

        return dst

    @staticmethod
    def add_border(img, w, h):
        return ImageOps.expand(img, border=(w, h))


class ImageGenerator(ImageOptionMixin):
    def __init__(self):
        self._img_map = self._get_img_map()

    @staticmethod
    def _get_img_map() -> dict:
        dir_path = os.path.abspath(os.path.dirname(__file__))
        return {i: Image.open(os.path.join(dir_path, 'img', f'{i}.png'))
                for i in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.')}

    @staticmethod
    def _random_wait_time() -> Callable:
        i = 1

        def core():
            nonlocal i
            if i >= 20:
                i = 1
                return 1800
            else:
                i += random.choice([0, 0, 0, 1, 1, 2])  # weight choice makes it more random
                return 60

        return core

    @staticmethod
    def _generate_border():
        return 307 // 4, 104

    @staticmethod
    def _generate_clock() -> [str, None]:
        t = time.localtime()
        time_str = '{:02d}.{:02d}.{:02d}'.format(t.tm_hour, t.tm_min, t.tm_sec)
        return time_str

    @staticmethod
    def _generate_meter() -> [str, None]:
        num_list = [str(random.randint(0, 9)) for _ in range(7)]
        num_str = ''.join(num_list)
        num_str = num_str[0] + '.' + num_str[1:]
        return num_str

    def generate_image(self, num_str: str, border_v: int, border_h: int):
        img_list = [self._img_map[i] for i in num_str]
        img = self.concat_h(img_list)
        img = self.add_border(img, border_v, border_h)
        return img

    def generate(self, gen_img_str: Callable, gen_border: Callable, gen_wait_time: Callable) -> Iterable:
        while True:
            img_str = gen_img_str()
            if not img_str:
                break

            border_v, border_h = gen_border()

            img = self.generate_image(img_str, border_v, border_h)
            yield img

            wait = gen_wait_time()
            if not wait:
                break
            time.sleep(wait / 1000)

    def meter(self, border=None, wait_time=None) -> Iterable:
        border = self._generate_border if not border else border
        wait_time = self._random_wait_time() if not wait_time else wait_time
        return self.generate(self._generate_meter, border, wait_time)

    def clock(self, border=None) -> Iterable:
        border = self._generate_border if not border else border
        return self.generate(self._generate_clock, border, lambda: 1000)


class ImageThread(QThread):
    change_pic = pyqtSignal(Image.Image)

    def __init__(self, type_):
        super().__init__()
        self.type_ = type_

    def run(self):
        d = ImageGenerator()
        generator = d.clock if self.type_ == TYPE_CLOCK else d.meter
        for pic in generator():
            self.change_pic.emit(pic)


class Divergence(QWidget):
    def __init__(self, type_=TYPE_CLOCK):
        super(QWidget, self).__init__()
        self.initUI(type_)

        self.origin_pic_size = None
        self.pixmap = None

    def initUI(self, type_):
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setStyleSheet('background-color:black')

        self.label = QLabel(self)
        self.label.resize(984, 515)

        self.worker = ImageThread(type_)
        self.worker.change_pic.connect(self.show_image)
        self.worker.start()

    def show_image(self, pic):
        qim = ImageQt.ImageQt(pic)
        img = qim.copy()
        self.origin_pic_size = img.size()
        self.pixmap = QPixmap.fromImage(img)
        self.label.setPixmap(self.pixmap)

    def paintEvent(self, event):
        if (self.origin_pic_size is not None) and (self.pixmap is not None):
            size = self.geometry().size()
            win_w = size.width()
            win_h = size.height()

            origin_w = self.origin_pic_size.width()
            origin_h = self.origin_pic_size.height()

            scale = min(win_w / origin_w, win_h / origin_h)
            new_w = int(origin_w * scale)
            new_h = int(origin_h * scale)

            self.pixmap = self.pixmap.scaled(new_w, new_h, Qt.IgnoreAspectRatio)
            self.label.resize(new_w, new_h)
            self.label.setPixmap(self.pixmap)

        QWidget.paintEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

        if event.button() == Qt.RightButton:
            self.close()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.is_dragging:
            self.move(QMouseEvent.globalPos() - self.drag_position)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.is_dragging = False
        self.setCursor(QCursor(Qt.ArrowCursor))


def test_image_generator():
    d = ImageGenerator()
    for p in d.meter():
        t = time.localtime()
        time_str = '{:02d}.{:02d}.{:02d}.jpg'.format(t.tm_hour, t.tm_min, t.tm_sec)
        p.save(time_str, "JPEG")
        print(time_str)


def test_qt():
    app = QApplication(sys.argv)
    main = Divergence(type_=TYPE_CLOCK)
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_qt()
