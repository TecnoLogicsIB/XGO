# husky.py - HuskyLens I2C (micro:bit MicroPython)
from microbit import i2c, sleep, running_time

# --- I2C / protocol constants ---
I2C_ADDR = 0x32
PADDR    = 0x11

CMD_KNOCK    = 0x2C
CMD_SET_ALGO = 0x2D
CMD_REQ      = 0x21
CMD_LEARN    = 0x36
CMD_FORGET   = 0x37

RSP_OK    = 0x2E
RSP_INFO  = 0x29
RSP_BLOCK = 0x2A

# --- Algorithms (same mapping you had in xgo) ---
FACE = 0x0000
TRACK = 0x0001
OBJECT = 0x0002
LINE = 0x0003
COLOR = 0x0004
TAG = 0x0005
CLASSIFICATION = 0x0006


def _sum8(buf):
    s = 0
    for b in buf:
        s += b
    return s & 0xFF


def _flush_bus():
    # Clear any pending bytes in the I2C device FIFO (best effort)
    for _ in range(3):
        try:
            i2c.read(I2C_ADDR, 32)
        except:
            pass
        sleep(5)


def _send(cmd, data=b""):
    ln = len(data)
    fr = bytearray([0x55, 0xAA, PADDR, ln, cmd])
    for x in data:
        fr.append(x)
    fr.append(_sum8(fr))
    i2c.write(I2C_ADDR, fr)


def _read_frame_once():
    """
    Reads exactly one frame using the '5 bytes header + (len+1) bytes' pattern:
      header: 55 AA addr len cmd
      rest: payload(len bytes) + checksum(1 byte)
    Returns (cmd, payload) or (None, None) on failure.
    """
    try:
        header = i2c.read(I2C_ADDR, 5)
        if len(header) != 5:
            return None, None
        if header[0] != 0x55 or header[1] != 0xAA:
            return None, None

        ln = header[3]
        rest = i2c.read(I2C_ADDR, ln + 1)  # payload + checksum
        if len(rest) != ln + 1:
            return None, None

        fr = bytes(header) + bytes(rest)

        # checksum is last byte of full frame
        if _sum8(fr[:-1]) != fr[-1]:
            return None, None

        cmd = fr[4]
        payload = fr[5:5 + ln]
        return cmd, payload
    except:
        return None, None


def _get_frame(timeout=600):
    """
    Keep trying to read a valid frame until timeout.
    """
    t0 = running_time()
    while running_time() - t0 < timeout:
        cmd, payload = _read_frame_once()
        if cmd is not None:
            return cmd, payload
        sleep(15)
    return None, None


def knock():
    try:
        _flush_bus()
        _send(CMD_KNOCK)
        cmd, _ = _get_frame(800)
        return cmd == RSP_OK
    except:
        return False


def set_algorithm(algo):
    try:
        _flush_bus()
        _send(CMD_SET_ALGO, bytes([algo & 0xFF, (algo >> 8) & 0xFF]))

        t0 = running_time()
        while running_time() - t0 < 1200:
            cmd, _ = _get_frame(400)
            if cmd == RSP_OK:
                return True
            sleep(20)
        return False
    except:
        return False


def _parse_block_payload(d):
    # Standard block payload uses at least 10 bytes (x,y,w,h,id) little-endian
    if not d or len(d) < 10:
        return None
    x = d[0] | (d[1] << 8)
    y = d[2] | (d[3] << 8)
    w = d[4] | (d[5] << 8)
    h = d[6] | (d[7] << 8)
    i = d[8] | (d[9] << 8)
    return {"x": x, "y": y, "w": w, "h": h, "id": i}


def get_block(timeout=1000):
    """
    Requests results and returns the first BLOCK (dict) found, else None.
    Flow:
      send REQ
      read INFO
      read N frames after INFO and return first BLOCK
    """
    try:
        _send(CMD_REQ)

        # 1) Wait for INFO
        info_payload = None
        t0 = running_time()
        while running_time() - t0 < timeout:
            cmd, d = _get_frame(400)
            if cmd == RSP_INFO and d:
                info_payload = d
                break
            sleep(10)

        if not info_payload:
            return None

        # INFO payload layout varies a bit across firmwares.
        # We only need "how many results" (blocks/arrows) and then read that many frames.
        # In many firmwares it's little-endian in first 2 bytes.
        if len(info_payload) >= 2:
            n = info_payload[0] | (info_payload[1] << 8)
        else:
            n = info_payload[0]

        if n <= 0:
            return None

        # 2) Read next n frames and return first BLOCK
        # (Some firmwares may include arrows too; we ignore non-BLOCK.)
        for _ in range(n):
            cmd, d = _get_frame(500)
            if cmd == RSP_BLOCK:
                b = _parse_block_payload(d)
                if b:
                    return b

        # If we didn't get a BLOCK in n reads, give a short grace period
        t1 = running_time()
        while running_time() - t1 < 300:
            cmd, d = _get_frame(300)
            if cmd == RSP_BLOCK:
                b = _parse_block_payload(d)
                if b:
                    return b
            sleep(10)

        return None
    except:
        return None


def learn(id_num=1):
    try:
        _flush_bus()
        _send(CMD_LEARN, bytes([id_num & 0xFF, (id_num >> 8) & 0xFF]))

        t0 = running_time()
        while running_time() - t0 < 1500:
            cmd, _ = _get_frame(500)
            if cmd == RSP_OK:
                return True
            sleep(30)
        return False
    except:
        return False


def forget():
    try:
        _flush_bus()
        _send(CMD_FORGET)

        t0 = running_time()
        while running_time() - t0 < 1500:
            cmd, _ = _get_frame(500)
            if cmd == RSP_OK:
                return True
            sleep(30)
        return False
    except:
        return False
