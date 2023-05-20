import random
import cv2
import os
import time

from typing import Iterable, Sequence


class DivergenceMeter:
    def __init__(self):
        self._img_map = self._get_img_map()
        self.borderV = 307 // 4
        self.borderH = 104

    @staticmethod
    def _get_img_map() -> dict:
        return {i: cv2.imread(os.path.join('.', 'img', f'{i}.png'))
                for i in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.')}

    @staticmethod
    def _fixed_wait_time() -> Iterable[int]:
        i = 1
        while True:
            if i == 30:
                yield 1800
                i = 1
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
    def generate_clock() -> Iterable[str]:
        while True:
            t = time.localtime()
            time_str = '{:02d}.{:02d}.{:02d}'.format(t.tm_hour, t.tm_min, t.tm_sec)
            yield time_str

    @staticmethod
    def generate_meter() -> Iterable[str]:
        while True:
            num_list = [str(random.randint(0, 9)) for _ in range(7)]
            num_str = ''.join(num_list)
            num_str = num_str[0] + '.' + num_str[1:]
            yield num_str

    def generate_image(self, num_str: str):
        img_list = [self._img_map[i] for i in num_str]
        img = cv2.hconcat(img_list)
        img = cv2.copyMakeBorder(img, self.borderV, self.borderV, self.borderH, self.borderH, cv2.BORDER_CONSTANT)
        return img

    def show(
            self,
            images: [Iterable[str], Sequence[str]],
            wait_time: [Iterable[int], Sequence[int], int] = 0,
            window_name: str = 'imshow',
    ) -> None:
        images = iter(images) if isinstance(images, Sequence) else images
        wait_time = iter(wait_time) if isinstance(wait_time, Sequence) else wait_time

        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        while True:
            if cv2.getWindowProperty(window_name, 0) == -1:
                break

            img_str = next(images, None)
            wait = next(wait_time, None) if isinstance(wait_time, Iterable) else wait_time
            if img_str is None or wait is None:
                break

            img = self.generate_image(img_str)
            cv2.imshow(window_name, img)
            key = cv2.waitKey(wait)
            if key == 27 or key == ord('q'):  # esc/q -> exit
                cv2.destroyAllWindows()
                break
            elif key == ord(' '):  # space -> suspend/start
                cv2.waitKey(0)
            elif key == ord('s'):  # s -> save
                cv2.imwrite(f'{window_name}.png', img)

    def meter(self) -> None:
        self.show(self.generate_meter(), self._random_wait_time(), 'divergence meter')

    def clock(self) -> None:
        self.show(self.generate_clock(), 1000, 'divergence clock')


if __name__ == '__main__':
    d = DivergenceMeter()
    d.clock()
    d.meter()
    d.show(['1.048596', '3.1415926', '10086'])
