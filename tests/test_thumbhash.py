from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pytest
from PIL import Image, ImageOps

from thumbhash_python import ThumbhashEncoder

this_dir = Path(__file__).parent
file_dir = this_dir / "files"


@dataclass
class Expected:
    hex: str
    array: List[int]
    base64: Optional[str] = None


reference = [
    # hex/base64 are from website/JavaScript, array from rust
    ("firefox.png", Expected(
        # Website has 6D instead of 6C
        hex="60 9A 86 3D 0C 3B B0 59 6C 96 A8 45 69 F4 84 F9 0E A8 27 58 76 88 70 76 47",
        array=[96, 154, 134, 61, 12, 59, 176, 89, 108, 150, 168, 69, 105, 244, 132, 249, 14, 168, 39, 88, 118, 136,
               112, 118, 71]
    )),
    ("sunrise.jpg", Expected(
        hex="D5 07 12 1D 04 67 87 8F 77 57 87 48 87 87 97 87 58 78 90 95 08",
        base64="1QcSHQRnh493V4dIh4eXh1h4kJUI",
        array=[213, 7, 18, 29, 132, 95, 116, 137, 120, 136, 135, 118, 136, 135, 120, 120, 8, 135, 149, 96, 87]
    )),
    ("flower.jpg", Expected(
        hex="93 4A 06 2D 06 92 56 C3 74 05 58 67 DA 8A B6 67 94 90 51 07 19",
        array=[147, 74, 6, 45, 6, 146, 86, 195, 116, 5, 88, 103, 218, 138, 182, 103, 148, 144, 81, 7, 25]
    )),
    ("coast.jpg", Expected(
        hex="21 08 12 2D 86 7A 88 77 8F 87 88 75 78 57 87 87 87 70 83 08 37",
        array=[33, 8, 18, 45, 134, 122, 136, 119, 143, 135, 136, 117, 120, 87, 135, 135, 135, 112, 131, 8, 55]
    )),
    ("fall.jpg", Expected(
        hex="1C 19 12 1D 84 88 78 78 8F 88 78 7C 78 97 78 79 33 74 10 44 06",
        array=[28, 25, 18, 29, 132, 136, 120, 120, 143, 136, 120, 124, 120, 151, 120, 121, 51, 116, 16, 68, 6]
    )),
    ("field.jpg", Expected(
        hex="DC E7 11 25 80 78 77 78 7F 88 87 87 78 48 77 78 88 70 FA 3D C0",
        array=[220, 231, 17, 37, 128, 120, 119, 120, 127, 136, 135, 135, 120, 72, 119, 120, 136, 112, 250, 61, 192]
    )),
    ("mountain.jpg", Expected(
        hex="D9 F7 19 14 80 77 88 87 7F 87 78 89 87 86 88 60 9D 95 F2",
        # original has 137 instead of second 136
        array=[217, 247, 25, 20, 128, 119, 136, 135, 127, 135, 120, 137, 135, 134, 136, 96, 157, 149, 242]
    )),
    ("opera.png", Expected(
        # original is "D8 8A 83 05 04 27 C6 78 F4 26 82 D8 74 CD CF F1 A8 69 B8 37 87 88 77 70 67"
        # looks visually identical
        hex="99 8A 83 05 04 27 C6 78 F4 26 82 D8 74 DE DF F0 98 69 B8 37 87 88 77 70 67",
        array=[153, 138, 131, 5, 4, 39, 198, 120, 244, 38, 130, 216, 116, 222, 223, 240, 152, 105, 184, 55, 135, 136,
               119, 112, 103]
    )),
    ("street.jpg", Expected(
        hex="56 08 0A 0D 80 16 EA 56 6F 75 87 7A 77 68 99 87 FA 78 18 4F E4",
        # original has 95 instead of 79
        array=[86, 8, 10, 13, 128, 22, 234, 86, 111, 117, 135, 122, 119, 104, 153, 135, 250, 120, 24, 79, 228]
    )),
    ("sunset.jpg", Expected(
        hex="DC F7 0D 35 84 85 79 78 7F 77 77 A5 77 48 87 66 86 60 57 08 76",
        base64="3PcNNYSFeXh/d3eld0iHZoZgVwh2",
        array=[220, 247, 13, 53, 132, 133, 121, 120, 127, 119, 119, 165, 119, 72, 135, 102, 134, 96, 87, 8, 118]
    )),
]


@pytest.mark.parametrize("filename,expected", reference)
def test_flower(filename, expected):
    with open(file_dir / filename, "rb") as f:
        img = Image.open(f)
        img_rotated = ImageOps.exif_transpose(img)

    result_rotated = ThumbhashEncoder(img_rotated)
    result_unrotated = ThumbhashEncoder(img)
    assert result_rotated.to_hexstring() == expected.hex
    # Rust version doesn't rotate images according to EXIF
    assert result_unrotated.hash == expected.array
