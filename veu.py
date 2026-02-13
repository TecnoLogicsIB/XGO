from microbit import i2c, sleep

DF2301Q_ADDR = 0x64

REG_CMDID      = 0x02
REG_PLAY_CMDID = 0x03
REG_SET_MUTE   = 0x04
REG_SET_VOLUME = 0x05
REG_WAKE_TIME  = 0x06


class VeuDF2301Q:
    def __init__(self, addr=DF2301Q_ADDR):
        self.addr = addr
        self._last = 0

    def _write_reg(self, reg, val):
        i2c.write(self.addr, bytes([reg, val & 0xFF]))

    def _read_reg(self, reg):
        i2c.write(self.addr, bytes([reg]), repeat=True)
        return i2c.read(self.addr, 1)[0]

    def configurar(self, volum=5, wake_time=20, mute=False):
        self.set_volume(volum)
        self.set_wake_time(wake_time)
        self.set_mute(mute)

    def get_cmdid(self):
        # Llegeix l’últim ID reconegut; 0 vol dir “cap comanda nova”
        sleep(10)
        return self._read_reg(REG_CMDID)

    def get_cmdid_nou(self):
        """
        Evita repetir el mateix ID si el mòdul el manté uns cicles.
        Retorna 0 si no hi ha cap "nova".
        """
        cmd = self.get_cmdid()
        if cmd != 0 and cmd != self._last:
            self._last = cmd
            return cmd
        if cmd == 0:
            self._last = 0
        return 0

    def play_by_cmdid(self, cmdid):
        self._write_reg(REG_PLAY_CMDID, int(cmdid))
        sleep(200)

    def set_volume(self, vol):
        vol = int(vol)
        if vol < 0: vol = 0
        if vol > 7: vol = 7
        self._write_reg(REG_SET_VOLUME, vol)

    def set_mute(self, mute):
        self._write_reg(REG_SET_MUTE, 1 if mute else 0)

    def set_wake_time(self, seconds):
        self._write_reg(REG_WAKE_TIME, int(seconds) & 0xFF)
