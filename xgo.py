# xgo.py (XGO UART + HuskyLens I2C) compactat per micro:bit V2
from microbit import uart, pin14, pin13, sleep, i2c, running_time

# =======================
# XGO (UART)
# =======================
BAUDRATE = 115200
_uart_ok = False

def uart_inicialitzar():
    global _uart_ok
    if not _uart_ok:
        uart.init(baudrate=BAUDRATE, tx=pin14, rx=pin13)
        _uart_ok = True

def _chk(length, cmd, addr, data):
    return (~((length + cmd + addr + data) & 0xFF)) & 0xFF

def escriure_byte(adreca, dada):
    uart_inicialitzar()
    ln = 0x09
    cmd = 0x00
    d = dada & 0xFF
    a = adreca & 0xFF
    c = _chk(ln, cmd, a, d)
    uart.write(bytes([0x55, 0x00, ln, cmd, a, d, c, 0x00, 0xAA]))
    sleep(2)

def aturar_tot():
    escriure_byte(0x03, 0x00)
    escriure_byte(0x39, 0x00); escriure_byte(0x3A, 0x00); escriure_byte(0x3B, 0x00)
    escriure_byte(0x80, 0x00); escriure_byte(0x81, 0x00); escriure_byte(0x82, 0x00)
    escriure_byte(0x3C, 0x00)

def restaurar_postura():
    escriure_byte(0x3E, 0xFF)

def velocitat_servos(valor):
    escriure_byte(0x5C, valor & 0xFF)

def potes_mode_debug():
    escriure_byte(0x20, 0x21); escriure_byte(0x20, 0x22)
    escriure_byte(0x20, 0x23); escriure_byte(0x20, 0x24)

def inicialitzar(velocitat=0xA0):
    aturar_tot()
    potes_mode_debug()
    velocitat_servos(velocitat)

def posicio_inicial_estable():
    aturar_tot()
    escriure_byte(0x30, 0x80); escriure_byte(0x31, 0x80); escriure_byte(0x32, 0x80)
    escriure_byte(0x33, 0x80); escriure_byte(0x34, 0x80); escriure_byte(0x35, 0x80)
    escriure_byte(0x36, 0x80); escriure_byte(0x37, 0x80); escriure_byte(0x38, 0x80)
    escriure_byte(0x3C, 0x00)

# --- Locomoció ---
def gait_walk():
    escriure_byte(0x09, 0x01)

def caminar(vel):
    gait_walk()
    escriure_byte(0x30, vel & 0xFF)
    escriure_byte(0x31, 0x80)
    escriure_byte(0x32, 0x80)

def girar(valor):
    gait_walk()
    escriure_byte(0x30, 0x80)
    escriure_byte(0x31, 0x80)
    escriure_byte(0x32, valor & 0xFF)

def lateral(valor):
    gait_walk()
    escriure_byte(0x30, 0x80)
    escriure_byte(0x31, valor & 0xFF)
    escriure_byte(0x32, 0x80)

def stop():
    caminar(0x80)

# --- Cos ---
def cos_translacio(eix, valor):
    v = valor & 0xFF
    if eix == 'x': escriure_byte(0x33, v)
    elif eix == 'y': escriure_byte(0x34, v)
    elif eix == 'z': escriure_byte(0x35, v)

def cos_rotacio(eix, valor):
    v = valor & 0xFF
    if eix == 'x': escriure_byte(0x36, v)
    elif eix == 'y': escriure_byte(0x37, v)
    elif eix == 'z': escriure_byte(0x38, v)

def cos_neutre():
    escriure_byte(0x33,0x80); escriure_byte(0x34,0x80); escriure_byte(0x35,0x80)
    escriure_byte(0x36,0x80); escriure_byte(0x37,0x80); escriure_byte(0x38,0x80)

def desplacar_cos(eix, valor):
    cos_translacio(eix, valor)

def girar_cos(eix, valor):
    cos_rotacio(eix, valor)

# --- Potes (servo IDs) ---
_MAPA_ID_A_ADRECA = {
    11:0x50, 12:0x51, 13:0x52,
    21:0x53, 22:0x54, 23:0x55,
    31:0x56, 32:0x57, 33:0x58,
    41:0x59, 42:0x5A, 43:0x5B
}

def pota_posar_servo_id(servo_id, valor):
    ad = _MAPA_ID_A_ADRECA.get(servo_id)
    if ad is not None:
        escriure_byte(ad, valor & 0xFF)

# --- Braç + Pinça ---
_ADRECA_BRAC_AVANT = 0x5D
_ADRECA_BRAC_GRAN  = 0x5E
_ADRECA_PINCA      = 0x71
_ADRECA_PINCA_X    = 0x73
_ADRECA_PINCA_Z    = 0x74

def avant_brac(valor):
    escriure_byte(_ADRECA_BRAC_AVANT, valor & 0xFF)

def brac(valor):
    escriure_byte(_ADRECA_BRAC_GRAN, valor & 0xFF)

def pinca_obrir():
    escriure_byte(_ADRECA_PINCA, 0x00)

def pinca_tancar():
    escriure_byte(_ADRECA_PINCA, 0xFF)

def pinca_x(valor):
    escriure_byte(_ADRECA_PINCA_X, valor & 0xFF)

def pinca_z(valor):
    escriure_byte(_ADRECA_PINCA_Z, valor & 0xFF)

# --- Accions ---
_DUR = (0,
    3500,3500,5500,6500,2000,
    4500,5500,5500,5500,8000,
    7000,5000,7000,10000,6000,
    6000,4000,8000,10000
)

def stop_accio():
    escriure_byte(0x3E, 0x00)
    sleep(50)
    aturar_tot()
    escriure_byte(0x30,0x80); escriure_byte(0x31,0x80); escriure_byte(0x32,0x80)
    escriure_byte(0x3C,0x00)

def executar_accio(action_id, esperar=True):
    dur = _DUR[action_id] if 0 < action_id < len(_DUR) else 0
    escriure_byte(0x3E, action_id & 0xFF)
    if esperar and dur:
        sleep(dur)
        stop_accio()
    return dur

def _mk_acc(n):
    def f(esperar=True):
        return executar_accio(n, esperar)
    return f

for _i in range(1, 20):
    globals()["accio_%d" % _i] = _mk_acc(_i)

# =======================
# HuskyLens (I2C)
# =======================
I2C_ADDR = 0x32
PADDR = 0x11
CMD_KNOCK=0x2C; CMD_SET_ALGO=0x2D; CMD_REQ=0x21; CMD_LEARN=0x36; CMD_FORGET=0x37
RSP_OK=0x2E; RSP_INFO=0x29; RSP_BLOCK=0x2A

FACE=0x0000; TRACK=0x0001; OBJECT=0x0002; LINE=0x0003; COLOR=0x0004; TAG=0x0005; CLASSIFICATION=0x0006

def _sum8(b):
    return sum(b) & 0xFF

def _flush():
    for _ in range(2):
        try:
            i2c.read(I2C_ADDR, 32)
        except:
            pass

def _send(cmd, data=b""):
    ln = len(data)
    fr = bytearray([0x55,0xAA,PADDR,ln,cmd])
    for x in data: fr.append(x)
    fr.append(_sum8(fr))
    i2c.write(I2C_ADDR, fr)

def _get(timeout=300):
    t0 = running_time()
    while running_time() - t0 < timeout:
        raw = bytes(i2c.read(I2C_ADDR, 32))
        n = len(raw)
        for i in range(n-6):
            if raw[i]==0x55 and raw[i+1]==0xAA:
                ln = raw[i+3]
                tot = 6 + ln
                if i+tot <= n:
                    fr = raw[i:i+tot]
                    if _sum8(fr[:-1]) == fr[-1]:
                        return fr[4], fr[5:5+ln]
        sleep(20)
    return None, None

def knock():
    try:
        _flush()
        _send(CMD_KNOCK)
        c,_ = _get(500)
        return c == RSP_OK
    except:
        return False

def set_algorithm(algo):
    try:
        _flush()
        _send(CMD_SET_ALGO, bytes([algo & 0xFF, (algo>>8) & 0xFF]))
        for _ in range(6):
            c,_ = _get(300)
            if c == RSP_OK:
                return True
            sleep(40)
        return False
    except:
        return False

def get_block():
    try:
        _flush()
        _send(CMD_REQ)
        sleep(80)
        for _ in range(10):
            c,d = _get(300)
            if c == RSP_BLOCK and d and len(d) == 10:
                x = d[0] | (d[1]<<8)
                y = d[2] | (d[3]<<8)
                w = d[4] | (d[5]<<8)
                h = d[6] | (d[7]<<8)
                i = d[8] | (d[9]<<8)
                return {"x":x,"y":y,"w":w,"h":h,"id":i}
            sleep(40)
        return None
    except:
        return None

def learn(id_num=1):
    try:
        _flush()
        _send(CMD_LEARN, bytes([id_num & 0xFF, (id_num>>8) & 0xFF]))
        for _ in range(6):
            c,_ = _get(400)
            if c == RSP_OK:
                return True
            sleep(60)
        return False
    except:
        return False

def forget():
    try:
        _flush()
        _send(CMD_FORGET)
        for _ in range(6):
            c,_ = _get(400)
            if c == RSP_OK:
                return True
            sleep(60)
        return False
    except:
        return False