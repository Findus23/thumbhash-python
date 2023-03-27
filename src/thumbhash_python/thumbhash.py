import numpy as np
from PIL import Image


def encode(img: Image):
    img = img.convert("RGBA")
    data = np.asarray(img)
    data = np.swapaxes(data, 0, 1)
    width, height, dims = data.shape
    assert dims == 4  # RGBA
    return rgba_to_thumb_hash(width, height, data)


def encode_channel(channel: np.ndarray, nx: int, ny: int, w: int, h: int):
    """
    channel is a (w, h) array
    """
    dc = 0
    ac = []
    scale = 0
    fx = np.zeros(w)
    for cy in range(ny):
        cx = 0
        while cx * ny < nx * (ny - cy):
            f = 0
            for x in range(w):
                fx[x] = np.cos(np.pi / w * cx * (x + 0.5))
            for y in range(h):
                fy = np.cos(np.pi / h * cy * (y + 0.5))
                for x in range(w):
                    f += channel[x, y] * fx[x] * fy
            f /= w * h
            if cx > 0 or cy > 0:
                ac.append(f)
                scale = max(scale, abs(f))
            else:
                dc = f
            cx += 1
    if scale:
        ac_arr = np.asarray(ac)
        ac = (0.5 + 0.5 / scale * ac_arr).tolist()
    return dc, ac, scale


def rgba_to_thumb_hash(w: int, h: int, data: np.ndarray):
    """
    convert

    unlike the other language ports, here data is a (w, h, 4) array
    """
    assert w <= 100 and h <= 100, "Encoding an image larger than 100x100 is slow with no benefit"
    assert w == data.shape[0]
    assert h == data.shape[1]
    numpix = h * w

    alpha = data[..., 3] / 255
    alpha_sum = alpha.sum()
    data_with_alpha = data.copy().astype(np.float64)
    data_with_alpha[..., 0] *= alpha
    data_with_alpha[..., 1] *= alpha
    data_with_alpha[..., 2] *= alpha
    avg = np.sum(data_with_alpha, axis=(0, 1)) / 255

    if alpha_sum:
        avg[0] /= alpha_sum
        avg[1] /= alpha_sum
        avg[2] /= alpha_sum

    has_alpha = alpha_sum < numpix
    l_limit = 5 if has_alpha else 7
    lx = max(1, round(l_limit * w / max(w, h)))
    ly = max(1, round(l_limit * h / max(w, h)))

    r = data[..., 0] / 255 * alpha + avg[0] * (1 - alpha)
    g = data[..., 1] / 255 * alpha + avg[1] * (1 - alpha)
    b = data[..., 2] / 255 * alpha + avg[2] * (1 - alpha)

    # Convert the image from RGBA to LPQA (composite atop the average color)
    l = (r + g + b) / 3
    p = (r + g) / 2 - b
    q = r - g

    l_dc, l_ac, l_scale = encode_channel(l, max(3, lx), max(3, ly), w, h)
    p_dc, p_ac, p_scale = encode_channel(p, 3, 3, w, h)
    q_dc, q_ac, q_scale = encode_channel(q, 3, 3, w, h)
    isLandscape = w > h
    header24 = round(63 * l_dc) | (round(31.5 + 31.5 * p_dc) << 6) | (round(31.5 + 31.5 * q_dc) << 12) | (
            round(31 * l_scale) << 18) | (has_alpha << 23)
    header16 = (ly if isLandscape else lx) | (round(63 * p_scale) << 3) | (round(63 * q_scale) << 9) | (
            isLandscape << 15)
    hash = [header24 & 255, (header24 >> 8) & 255, header24 >> 16, header16 & 255, header16 >> 8]
    ac_start = 6 if has_alpha else 5
    ac_index = 0
    if has_alpha:
        a_dc, a_ac, a_scale = encode_channel(alpha, 5, 5, w, h)
        hash.append(round(15 * a_dc) | (round(15 * a_scale) << 4))
        acs = [l_ac, p_ac, q_ac, a_ac]
    else:
        acs = [l_ac, p_ac, q_ac]
    is_odd = False
    for ac in acs:
        for f in ac:
            u = round(15 * f)
            if is_odd:
                hash[-1] |= u << 4
            else:
                hash.append(u)
            is_odd = not is_odd
    return hash


def hexstring(arr):
    out = []
    for i in arr:
        text = hex(i)[2:].upper()
        if len(text) < 2:
            text = "0" + text
        out.append(text)
    return " ".join(out)
