# ==== imports ====
from microbit import *
import xgo
import radio
import music
# no cal inicialitzar la ràdio, ja s'ha inicialitzat des de main.py

# ==== funció principal cridada des de main.py ====
def executar():    
    xgo.posicio_inicial_estable()  # deixa el robot en estat neutre i estable inicial

    while True:   # accions condicionades a la recepció de missatges de ràdio 
        pkt = radio.receive_full()
        if pkt:
            data = pkt[0]
            if data and (b"XGO:C" in data):
                accio_1()
            elif data and (b"XGO:D" in data):
                accio_2()
            elif data and (b"XGO:E" in data):
                accio_3()
            elif data and (b"XGO:F" in data):
                accio_4()
            elif data and (b"XGO:STOP" in data):
                return
        sleep(30)

# ==== accions a executar, definides com a funcions ====

def accio_1():
    music.pitch (1000, 200)    # beep curt (freqüència 1000 Hz (to), durada 200 ms)
    
def accio_2():
    music.pitch (1000, 200)

def accio_3():
    music.pitch (1000, 200)
    
def accio_4():
    music.pitch (1000, 200)
