# husky_esp32.py

from machine import Pin, I2C
from time import sleep_ms, ticks_ms, ticks_diff

# =========================
# Configuració I2C ESP32
# =========================
# Canvia aquests pins si al teu muntatge uses uns altres.
# Exemple habitual ESP32: scl=22, sda=21
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# =========================
# Constants de protocol
# =========================
I2C_ADDR = 0x32
PADDR = 0x11

CMD_REQ       = 0x20   # request all
CMD_REQ_KNOCK = 0x2C
CMD_REQ_ALGO  = 0x2D
CMD_REQ_LEARN = 0x36
CMD_REQ_FORGET= 0x37

RSP_RETURN_OK   = 0x2E
RSP_RETURN_INFO = 0x29
RSP_RETURN_BLOCK= 0x2A
RSP_RETURN_ARROW= 0x2B

# Algorismes
FACE = 0x0000
TRACK = 0x0001
OBJECT = 0x0002
LINE = 0x0003
COLOR = 0x0004
TAG = 0x0005
CLASSIFICATION = 0x0006

# =========================
# Utilitats
# =========================
def _sum8(buf):
    s = 0
    for b in buf:
        s += b
    return s & 0xFF


def _send(cmd, data=b""):
    ln = len(data)
    frame = bytearray([0x55, 0xAA, PADDR, ln, cmd])
    frame.extend(data)
    frame.append(_sum8(frame))
    i2c.writeto(I2C_ADDR, frame)


def _flush_bus():
    # Intent de neteja "best effort"
    for _ in range(3):
        try:
            i2c.readfrom(I2C_ADDR, 32)
        except Exception:
            pass
        sleep_ms(5)


def _read_frame_once():
    """
    Llegeix 1 frame:
      header: 55 AA addr len cmd
      rest: payload(len) + checksum
    Retorna (cmd, payload) o (None, None)
    """
    try:
        header = i2c.readfrom(I2C_ADDR, 5)
        if len(header) != 5:
            return None, None

        if header[0] != 0x55 or header[1] != 0xAA:
            return None, None

        ln = header[3]
        rest = i2c.readfrom(I2C_ADDR, ln + 1)
        if len(rest) != ln + 1:
            return None, None

        frame = bytes(header) + bytes(rest)

        # checksum
        if _sum8(frame[:-1]) != frame[-1]:
            return None, None

        cmd = frame[4]
        payload = frame[5:5 + ln]
        return cmd, payload

    except Exception:
        return None, None


def _get_frame(timeout=600):
    t0 = ticks_ms()
    while ticks_diff(ticks_ms(), t0) < timeout:
        cmd, payload = _read_frame_once()
        if cmd is not None:
            return cmd, payload
        sleep_ms(15)
    return None, None


# =========================
# API pública
# =========================
def knock():
    try:
        _flush_bus()
        _send(CMD_REQ_KNOCK)
        cmd, _ = _get_frame(800)
        return cmd == RSP_RETURN_OK
    except Exception:
        return False


def set_algorithm(algo):
    try:
        _flush_bus()
        data = bytes([algo & 0xFF, (algo >> 8) & 0xFF])
        _send(CMD_REQ_ALGO, data)

        t0 = ticks_ms()
        while ticks_diff(ticks_ms(), t0) < 1200:
            cmd, _ = _get_frame(400)
            if cmd == RSP_RETURN_OK:
                return True
            sleep_ms(20)
        return False
    except Exception:
        return False


def _parse_block_payload(d):
    # payload mínim típic: x,y,w,h,id (10 bytes, little-endian)
    if not d or len(d) < 10:
        return None

    x = d[0] | (d[1] << 8)
    y = d[2] | (d[3] << 8)
    w = d[4] | (d[5] << 8)
    h = d[6] | (d[7] << 8)
    i = d[8] | (d[9] << 8)

    return {
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "id": i
    }


def _parse_arrow_payload(d):
    # x_origin, y_origin, x_target, y_target, id
    if not d or len(d) < 10:
        return None

    xo = d[0] | (d[1] << 8)
    yo = d[2] | (d[3] << 8)
    xt = d[4] | (d[5] << 8)
    yt = d[6] | (d[7] << 8)
    i  = d[8] | (d[9] << 8)

    return {
        "x_origin": xo,
        "y_origin": yo,
        "x_target": xt,
        "y_target": yt,
        "id": i
    }


def get_block(timeout=1000):
    """
    Demana resultats i retorna el primer block trobat, o None.
    """
    try:
        _send(CMD_REQ)

        # Espera INFO
        info_payload = None
        t0 = ticks_ms()
        while ticks_diff(ticks_ms(), t0) < timeout:
            cmd, d = _get_frame(400)
            if cmd == RSP_RETURN_INFO and d:
                info_payload = d
                break
            sleep_ms(10)

        if not info_payload:
            return None

        # nombre de resultats
        if len(info_payload) >= 2:
            n = info_payload[0] | (info_payload[1] << 8)
        else:
            n = info_payload[0]

        if n <= 0:
            return None

        # llegeix fins trobar un block
        for _ in range(n):
            cmd, d = _get_frame(500)
            if cmd == RSP_RETURN_BLOCK:
                b = _parse_block_payload(d)
                if b:
                    return b

        # petit marge extra
        t1 = ticks_ms()
        while ticks_diff(ticks_ms(), t1) < 300:
            cmd, d = _get_frame(300)
            if cmd == RSP_RETURN_BLOCK:
                b = _parse_block_payload(d)
                if b:
                    return b
            sleep_ms(10)

        return None

    except Exception:
        return None


def get_arrow(timeout=1000):
    """
    Demana resultats i retorna la primera arrow trobada, o None.
    """
    try:
        _send(CMD_REQ)

        info_payload = None
        t0 = ticks_ms()
        while ticks_diff(ticks_ms(), t0) < timeout:
            cmd, d = _get_frame(400)
            if cmd == RSP_RETURN_INFO and d:
                info_payload = d
                break
            sleep_ms(10)

        if not info_payload:
            return None

        if len(info_payload) >= 2:
            n = info_payload[0] | (info_payload[1] << 8)
        else:
            n = info_payload[0]

        if n <= 0:
            return None

        for _ in range(n):
            cmd, d = _get_frame(500)
            if cmd == RSP_RETURN_ARROW:
                a = _parse_arrow_payload(d)
                if a:
                    return a

        t1 = ticks_ms()
        while ticks_diff(ticks_ms(), t1) < 300:
            cmd, d = _get_frame(300)
            if cmd == RSP_RETURN_ARROW:
                a = _parse_arrow_payload(d)
                if a:
                    return a
            sleep_ms(10)

        return None

    except Exception:
        return None


def learn(id_num=1):
    try:
        _flush_bus()
        data = bytes([id_num & 0xFF, (id_num >> 8) & 0xFF])
        _send(CMD_REQ_LEARN, data)

        t0 = ticks_ms()
        while ticks_diff(ticks_ms(), t0) < 1500:
            cmd, _ = _get_frame(500)
            if cmd == RSP_RETURN_OK:
                return True
            sleep_ms(30)
        return False
    except Exception:
        return False


def forget():
    try:
        _flush_bus()
        _send(CMD_REQ_FORGET)

        t0 = ticks_ms()
        while ticks_diff(ticks_ms(), t0) < 1500:
            cmd, _ = _get_frame(500)
            if cmd == RSP_RETURN_OK:
                return True
            sleep_ms(30)
        return False
    except Exception:
        return False
