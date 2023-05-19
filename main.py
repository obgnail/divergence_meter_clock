import random
import cv2
import os
import time

from typing import Iterable, Callable


class DivergenceMeter:
    def __init__(self):
        self._img_map = self._get_img_map()

        self.meter_window_name = 'divergence meter'
        self.clock_window_name = 'divergence clock'

        self.possibility = 100  # 1%
        self.lucky_number = '1.048596'

        self.borderV = 307 // 4
        self.borderH = 104

    @staticmethod
    def _get_img_map() -> dict:
        return {i: cv2.imread(os.path.join('.', 'img', f'{i}.png'))
                for i in ('.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9')}

    @staticmethod
    def _fixed_wait_time() -> Iterable[int]:
        i = 1
        while True:
            if i == 30:
                yield 1800
                i = 0
            else:
                yield 60

            i += 1

    @staticmethod
    def _random_wait_time() -> Iterable[int]:
        i = 1
        while True:
            if i >= 20:
                yield 1800
                i = 1
            else:
                # yield random.randint(30, 90)
                yield 60
                i += random.choice([0, 0, 0, 1, 1, 2])  # weight choice makes it more random

    @staticmethod
    def show_image(window_name: str, wait_time: [int, Iterable[int]], image_generator: Callable) -> None:
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        while True:
            if cv2.getWindowProperty(window_name, 0) == -1:
                break

            img = image_generator()
            cv2.imshow(window_name, img)

            wait = wait_time if isinstance(wait_time, int) else next(wait_time)
            key = cv2.waitKey(wait)

            if key == 27:  # esc 退出
                cv2.destroyAllWindows()
                break
            elif key == ord('s'):  # s 保存
                cv2.imwrite(f'{window_name}.png', img)

    def generate_image(self, value: str):
        img_list = [self._img_map[i] for i in value]
        img = cv2.hconcat(img_list)
        img = cv2.copyMakeBorder(img, self.borderV, self.borderV,
                                 self.borderH, self.borderH, cv2.BORDER_CONSTANT)
        return img

    def generate_time_image(self):
        t = time.localtime()
        time_str = '{:02d}.{:02d}.{:02d}'.format(t.tm_hour, t.tm_min, t.tm_sec)
        return self.generate_image(time_str)

    def generate_divergence_image(self):
        if random.randint(0, self.possibility) == self.possibility:
            num_str = self.lucky_number
        else:
            num_list = [str(random.randint(0, 9)) for _ in range(7)]
            num_str = ''.join(num_list)
            num_str = num_str[0] + '.' + num_str[1:]
        return self.generate_image(num_str)

    def meter(self) -> None:
        wait_time = self._random_wait_time()
        image_generator = self.generate_divergence_image
        self.show_image(self.meter_window_name, wait_time, image_generator)

    def clock(self) -> None:
        wait_time = 1000
        image_generator = self.generate_time_image
        self.show_image(self.clock_window_name, wait_time, image_generator)


if __name__ == '__main__':
    d = DivergenceMeter()
    # d.clock()
    d.meter()
