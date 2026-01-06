# main.py
from microbit import *
import radio
import music

radio.config(group=23, channel=50, power=7, queue=20, length=32)
radio.on()

def esperar_go():
    display.clear()
    while True:
        pkt = radio.receive_full()
        if pkt:
            data = pkt[0]
            if data and (b"XGO:GO" in data):
                for y in range(5):
                    display.set_pixel(0, y, 9)
                sleep(300)
                return
        sleep(30)

while True:
    esperar_go()    # espera activació
    try:            # importa mòduls (només quan GO activat)
        import xgo
        import test   
        xgo.inicialitzar(0xA0)    # inicialitza robot
        test.executar()           # executa test
    except Exception as e:        # si hi ha algun error ...
        music.pitch(1000, 200)    # bip curt d'error (freqüència, durada)
        display.clear()
    sleep(200)    # torna al mode espera (i requereix un altre GO)