import random
import cv2
import os
import time

from typing import Iterable, Callable


def get_time_str() -> str:
    t = time.localtime()
    hour, min, sec = t.tm_hour, t.tm_min, t.tm_sec
    time_str = '{:02d}.{:02d}.{:02d}'.format(hour, min, sec)
    return time_str


def get_img_map() -> dict:
    return {
        i: cv2.imread(os.path.join('.', 'img', f'{i}.png'))
        for i in ['.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    }


def gen_img(img_map: dict, value: str):
    v = 307 // 4
    h = 104

    img_list = [img_map[i] for i in value]
    img = cv2.hconcat(img_list)
    img = cv2.copyMakeBorder(img, v, v, h, h, cv2.BORDER_CONSTANT)
    return img


def gen_time_img(img_map):
    time_str = get_time_str()
    return gen_img(img_map, time_str)


def gen_divergence_img(img_map):
    possibility = 100  # 1%
    if random.randint(0, possibility) == possibility:
        num_str = '1.048596'
    else:
        num_list = [str(random.randint(0, 9)) for _ in range(7)]
        num_str = ''.join(num_list)
        num_str = num_str[0] + '.' + num_str[1:]
    return gen_img(img_map, num_str)


def fixed_wait_time() -> int:
    i = 1
    while True:
        if i % 30 == 0:
            yield 1700
        else:
            yield 60

        i += 1


def random_wait_time() -> int:
    i = 1
    while True:
        force = False

        if i % 20 == 0:
            yield 1700
            force = True
        else:
            yield 60

        v = 1 if force else random.choice([0, 0, 0, 1, 1])  # weight choice makes it more random
        i += v


def show(window_name: str, wait_time: [int, Iterable], image_getter: Callable) -> None:
    img_map = get_img_map()
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    while True:
        if cv2.getWindowProperty(window_name, 0) == -1:
            break

        img = image_getter(img_map)
        cv2.imshow(window_name, img)

        if isinstance(wait_time, int):
            wait = wait_time
        else:
            wait = next(wait_time)

        key = cv2.waitKey(wait)

        if key == 27:  # esc 退出
            cv2.destroyAllWindows()
            break
        elif key == ord('s'):  # s 保存
            cv2.imwrite('image.png', img)


def divergence_meter() -> None:
    window_name = 'divergence meter'
    wait_time = random_wait_time()
    show(window_name, wait_time, gen_divergence_img)


def divergence_clock() -> None:
    window_name = 'divergence clock'
    wait_time = 1000
    show(window_name, wait_time, gen_time_img)


if __name__ == '__main__':
    # divergence_clock()
    divergence_meter()
