# Definició de l'enviament de polsos des de ESP32-S2 en funció de l'acció que volem a XGO

from machine import Pin
from time import sleep_ms

_pin_out = None    # permet definir el pin de comunicació. per defecte: 16)

# durada del pols (ms) segon l'ordre a transmetre (personalitzar els noms):
_ORDRES = {
    "ACCIO_1": 60,
    "ACCIO_2": 100,
    "ACCIO_3": 140,
    "ACCIO_4": 180,
    "ACCIO_5": 220,
    "ACCIO_6": 260,
    "ACCIO_7": 300,
    "ACCIO_8": 340,
    "ACCIO_9": 380,
    "ACCIO_10": 420,
}

def init(pin_num=16):    # permet definir al main el pin de comunicació. per defecte: 16
    global _pin_out
    _pin_out = Pin(pin_num, Pin.OUT)
    _pin_out.value(0)

def envia_ordre(nom):    # funció genèrica d'enviament del pols
    if _pin_out is None:
        init()

    ms = _ORDRES[nom]

    _pin_out.value(0)   # pin baix durant 50 ms
    sleep_ms(50)  
    _pin_out.value(1)   # pin alt
    sleep_ms(ms)        # manté el pin alt durant els ms corresponents a l'ordre a enviar
    _pin_out.value(0)   # pin baix durant 50 ms (GPT recomana 100 ms)
    sleep_ms(50)  

# ==== funcions específiques d'enviament ====

def accio_1():
    envia_ordre("ACCIO_1")
def accio_2():
    envia_ordre("ACCIO_2")
def accio_3():
    envia_ordre("ACCIO_3")
def accio_4():
    envia_ordre("ACCIO_4")
def accio_5():
    envia_ordre("ACCIO_5")
def accio_6():
    envia_ordre("ACCIO_6")
def accio_7():
    envia_ordre("ACCIO_7")
def accio_8():
    envia_ordre("ACCIO_8")
def accio_9():
    envia_ordre("ACCIO_9")
def accio_10():
    envia_ordre("ACCIO_10")
