# ESP32_main
from machine import Pin, TouchPad, I2C
from time import sleep_ms
import microbit_link as mb
import veu

mb.init(16)
led = Pin(15, Pin.OUT)    # led integrat
tBreak = TouchPad(Pin(3))
tActiva = TouchPad(Pin(2))

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)  # inicialitza I2C pels pins 9 (SCL), 8 (SDA)

# inicialitza i configura el sensor:
sensor = veu.VeuDF2301Q(i2c)
sensor.configurar(volum=7, wake_time=20, mute=False)

# per comprovar si es reconeix el sensor (si cal):
print("scan:", i2c.scan())  # hauria de retornar [100]

sleep_ms(1000)  # pausa d'1 s per estabilitzar (imprescindible per als touch)

# ==============================================

def reconeix_veu():
    cmd = sensor.get_cmdid()  # obté l'id del que escolta (0 si no reconeix)

    if cmd == 5:  # CAROL
        led.on()
        mb.a()    # pols de durada A
        
        print("CAROL")  # per comprovació

    elif cmd == 6:  # DESPERTA
        led.off()
        mb.k()    # pols de durada K per activar el robot també amb la veu
        print("DESPERTA")

    elif cmd == 7:  # VINE
        led.off()
        mb.c()    # pols de durada C
        print("VINE")
    
    elif cmd == 9:  # BUSCA
        led.off()
        mb.d()    # pols de durada C
        print("BUSCA")
    
    elif cmd == 11:  # MOLT BE
        led.off()
        mb.e()    # pols de durada C
        print("MOLT BE")
    
    elif cmd == 12:  # STOP
        led.off()
        mb.b()    # pols de durada C
        print("STOP")

# ==============================================

while True:
    if tBreak.read() > 15000:
        print("break")
        break

    if tActiva.read() > 15000:
        mb.k()
        print("activat")

    reconeix_veu()
  
    sleep_ms(50)
