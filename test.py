# ==== imports ====
from microbit import *
import xgo
import radio
# no cal inicialitzar la ràdio, ja s'ha inicialitzat des de main.py

# ==== funció principal cridada des de main.py ====
def executar():    
    display.clear()
    display.show(Image.ARROW_N)    # suport visual
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
    display.show('C')
    aprendre_2_cares()

def accio_2():
    display.show('D')
    caminar_amb_1_i_parar_amb_2()

def accio_3():
    display.show('E')

def accio_4():
    display.show('F')
    
# Funcions HuskyLens ==================

def aprendre_2_cares():
    xgo.set_algorithm(xgo.FACE)

    display.show('1')
    while xgo.get_block() is None:
        sleep(100)
    xgo.learn(1)

    display.show('2')
    while xgo.get_block() is None:
        sleep(100)
    xgo.learn(2)

    display.clear()

def caminar_amb_1_i_parar_amb_2():
    xgo.set_algorithm(xgo.FACE)

    while True:
        blk = xgo.get_block()
        if blk:
            if blk["id"] == 1:
                xgo.caminar(0xA5)
            elif blk["id"] == 2:
                xgo.stop()
                return
        sleep(120)
