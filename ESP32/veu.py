# veu_esp32.py

from machine import I2C
from time import sleep_ms

DF2301Q_ADDR = 0x64

REG_CMDID = 0x02
REG_PLAY_CMDID = 0x03
REG_SET_MUTE = 0x04
REG_SET_VOLUME = 0x05
REG_WAKE_TIME = 0x06


class VeuDF2301Q:
    def __init__(self, i2c, addr=DF2301Q_ADDR):
        self.addr = addr
        self.i2c = i2c
        self._last = 0

    def _write_reg(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val & 0xFF]))

    def _read_reg(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 1)
        return data[0]

    def configurar(self, volum=5, wake_time=20, mute=False):
        self.set_volume(volum)
        self.set_wake_time(wake_time)
        self.set_mute(mute)

    def get_cmdid(self):
        sleep_ms(50)
        return self._read_reg(REG_CMDID)

    def get_cmdid_nou(self):
        cmd = self.get_cmdid()

        if cmd != 0 and cmd != self._last:
            self._last = cmd
            return cmd

        if cmd == 0:
            self._last = 0

        return 0

    def play_by_cmdid(self, cmdid):
        self._write_reg(REG_PLAY_CMDID, int(cmdid))
        sleep_ms(200)

    def set_volume(self, vol):
        vol = max(0, min(7, int(vol)))
        self._write_reg(REG_SET_VOLUME, vol)

    def set_mute(self, mute):
        self._write_reg(REG_SET_MUTE, 1 if mute else 0)

    def set_wake_time(self, seconds):
        self._write_reg(REG_WAKE_TIME, int(seconds) & 0xFF)
