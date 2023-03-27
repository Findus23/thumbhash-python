import time

from PIL import Image, ImageOps

from thumbhash_python import ThumbhashEncoder


def bench(repeats=100):
    with open("tests/files/firefox.png", "rb") as f:
        img = Image.open(f)
        img = ImageOps.exif_transpose(img)

    start = time.perf_counter_ns()
    for _ in range(repeats):
        a = ThumbhashEncoder(img)
    end = time.perf_counter_ns()
    print((end - start) / 1_000_000 / repeats, "ms")


if __name__ == '__main__':
    bench()
