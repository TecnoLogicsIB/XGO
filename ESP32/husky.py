from time import sleep_ms, ticks_ms, ticks_diff

# =========================
# Constants de protocol HuskyLens
# =========================
DEFAULT_I2C_ADDR = 0x32
PADDR = 0x11

CMD_REQ_ALL     = 0x20
CMD_REQ_BLOCKS  = 0x21
CMD_KNOCK       = 0x2C
CMD_SET_ALGO    = 0x2D
CMD_LEARN       = 0x36
CMD_FORGET      = 0x37

RSP_INFO        = 0x29
RSP_BLOCK       = 0x2A
RSP_OK          = 0x2E

# Algorismes
FACE           = 0x0000
TRACK          = 0x0001
OBJECT         = 0x0002
LINE           = 0x0003
COLOR          = 0x0004
TAG            = 0x0005
CLASSIFICATION = 0x0006


class HuskyLens:
    def __init__(self, i2c, addr=DEFAULT_I2C_ADDR):
        """
        i2c  : objecte machine.I2C creat fora de la llibreria
        addr : adreça I2C de la HuskyLens
        """
        self.i2c = i2c
        self.addr = addr
        self.current_algorithm = None

    # =========================
    # Utilitats internes
    # =========================
    def _sum8(self, buf):
        s = 0
        for b in buf:
            s += b
        return s & 0xFF

    def _u16le(self, d, idx):
        return d[idx] | (d[idx + 1] << 8)

    def _send(self, cmd, data=b""):
        ln = len(data)
        frame = bytearray([0x55, 0xAA, PADDR, ln, cmd])
        frame.extend(data)
        frame.append(self._sum8(frame))
        self.i2c.writeto(self.addr, frame)

    def _flush_bus(self, times=3, nbytes=32, delay_ms=5):
        for _ in range(times):
            try:
                self.i2c.readfrom(self.addr, nbytes)
            except Exception:
                pass
            sleep_ms(delay_ms)

    def _read_frame_once(self):
        """
        Llegeix un frame:
          header: 55 AA addr len cmd
          rest: payload(len) + checksum

        Retorna:
          (cmd, payload) o (None, None)
        """
        try:
            header = self.i2c.readfrom(self.addr, 5)
            if len(header) != 5:
                return None, None

            if header[0] != 0x55 or header[1] != 0xAA:
                return None, None

            ln = header[3]
            rest = self.i2c.readfrom(self.addr, ln + 1)
            if len(rest) != ln + 1:
                return None, None

            frame = bytes(header) + bytes(rest)

            if self._sum8(frame[:-1]) != frame[-1]:
                return None, None

            cmd = frame[4]
            payload = frame[5:5 + ln]
            return cmd, payload

        except Exception:
            return None, None

    def _get_frame(self, timeout=600, poll_delay_ms=15):
        t0 = ticks_ms()
        while ticks_diff(ticks_ms(), t0) < timeout:
            cmd, payload = self._read_frame_once()
            if cmd is not None:
                return cmd, payload
            sleep_ms(poll_delay_ms)
        return None, None

    def _parse_info_payload(self, d):
        if not d:
            return {
                "count": 0,
                "learned_count": None,
                "frame_number": None,
                "raw": d
            }

        return {
            "count": self._u16le(d, 0) if len(d) >= 2 else d[0],
            "learned_count": self._u16le(d, 2) if len(d) >= 4 else None,
            "frame_number": self._u16le(d, 4) if len(d) >= 6 else None,
            "raw": d
        }

    def _parse_block_payload(self, d):
        """
        Block:
          x_center, y_center, width, height, id
        """
        if not d or len(d) < 10:
            return None

        return {
            "x": self._u16le(d, 0),
            "y": self._u16le(d, 2),
            "w": self._u16le(d, 4),
            "h": self._u16le(d, 6),
            "id": self._u16le(d, 8),
        }

    def _request_blocks(self, timeout=1000, flush=False):
        """
        Demana blocks i retorna:
          {
            "info": {...},
            "blocks": [...]
          }
        o None si falla.
        """
        try:
            if flush:
                self._flush_bus()

            self._send(CMD_REQ_BLOCKS)

            info_payload = None
            t0 = ticks_ms()
            while ticks_diff(ticks_ms(), t0) < timeout:
                cmd, d = self._get_frame(400)
                if cmd == RSP_INFO and d:
                    info_payload = d
                    break
                sleep_ms(10)

            if not info_payload:
                return None

            info = self._parse_info_payload(info_payload)
            n = info["count"]

            result = {
                "info": info,
                "blocks": []
            }

            if n <= 0:
                return result

            for _ in range(n):
                cmd, d = self._get_frame(500)
                if cmd == RSP_BLOCK:
                    b = self._parse_block_payload(d)
                    if b:
                        result["blocks"].append(b)

            # petit marge extra
            t1 = ticks_ms()
            while ticks_diff(ticks_ms(), t1) < 250:
                cmd, d = self._get_frame(150)
                if cmd == RSP_BLOCK:
                    b = self._parse_block_payload(d)
                    if b:
                        result["blocks"].append(b)
                else:
                    break

            return result

        except Exception:
            return None

    # =========================
    # API pública
    # =========================
    def scan_i2c_address(self):
        try:
            return self.addr in self.i2c.scan()
        except Exception:
            return False

    def knock(self):
        try:
            self._flush_bus()
            self._send(CMD_KNOCK)
            cmd, _ = self._get_frame(800)
            return cmd == RSP_OK
        except Exception:
            return False

    def set_algorithm(self, algo, force=False):
        """
        Canvia l'algorisme.
        Si force=False, no reenvia la comanda si ja és el mode actual.
        """
        try:
            if (not force) and (self.current_algorithm == algo):
                return True

            self._flush_bus()
            data = bytes([algo & 0xFF, (algo >> 8) & 0xFF])
            self._send(CMD_SET_ALGO, data)

            t0 = ticks_ms()
            while ticks_diff(ticks_ms(), t0) < 1200:
                cmd, _ = self._get_frame(400)
                if cmd == RSP_OK:
                    self.current_algorithm = algo
                    return True
                sleep_ms(20)

            return False
        except Exception:
            return False

    def set_mode_face(self, force=False):
        return self.set_algorithm(FACE, force=force)

    def set_mode_object(self, force=False):
        return self.set_algorithm(OBJECT, force=force)

    def learn(self, id_num=1):
        try:
            self._flush_bus()
            data = bytes([id_num & 0xFF, (id_num >> 8) & 0xFF])
            self._send(CMD_LEARN, data)

            t0 = ticks_ms()
            while ticks_diff(ticks_ms(), t0) < 1500:
                cmd, _ = self._get_frame(500)
                if cmd == RSP_OK:
                    return True
                sleep_ms(30)
            return False
        except Exception:
            return False

    def forget(self):
        try:
            self._flush_bus()
            self._send(CMD_FORGET)

            t0 = ticks_ms()
            while ticks_diff(ticks_ms(), t0) < 1500:
                cmd, _ = self._get_frame(500)
                if cmd == RSP_OK:
                    return True
                sleep_ms(30)
            return False
        except Exception:
            return False

    def get_block(self, timeout=1000):
        """
        Retorna el primer block trobat o None.
        Ideal per al teu cas de cares/objectes.
        """
        data = self._request_blocks(timeout=timeout)
        if not data or not data["blocks"]:
            return None
        return data["blocks"][0]

    def get_first_block(self, timeout=1000):
        """
        Àlies de get_block()
        """
        return self.get_block(timeout=timeout)

    def get_blocks(self, timeout=1000):
        """
        Retorna tots els blocks trobats.
        """
        data = self._request_blocks(timeout=timeout)
        if not data:
            return []
        return data["blocks"]

    def get_info(self, timeout=1000):
        """
        Retorna info general de l'última consulta de blocks.
        """
        data = self._request_blocks(timeout=timeout)
        if not data:
            return None
        return data["info"]

    def detect(self, timeout=1000):
        """
        Retorna un dict útil per treballar més còmodament:
          {
            "found": True/False,
            "block": {...} o None,
            "count": N
          }
        """
        data = self._request_blocks(timeout=timeout)
        if not data:
            return {
                "found": False,
                "block": None,
                "count": 0
            }

        blocks = data["blocks"]
        return {
            "found": len(blocks) > 0,
            "block": blocks[0] if blocks else None,
            "count": len(blocks)
        }