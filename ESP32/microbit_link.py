# Definició de l'enviament de polsos des de ESP32-S2 en funció de l'acció que volem a XGO

from machine import Pin
from time import sleep_ms

_pin_out = None    # permet definir el pin de comunicació. en el meu cas: 16)

# durada del pols (ms) segon l'ordre a transmetre (personalitzar els noms):
_ORDRES = {
    "A": 60,
    "B": 100,
    "C": 140,
    "D": 180,
    "E": 220,
    "F": 260,
    "G": 300,
    "H": 340,
    "I": 380,
    "J": 420,
}

def init(pin_num=16):    # permet definir al main el pin de comunicació. en el meu cas: 16
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

def a():
    envia_ordre("A")
def b():
    envia_ordre("B")
def c():
    envia_ordre("C")
def d():
    envia_ordre("D")
def e():
    envia_ordre("E")
def f():
    envia_ordre("F")
def g():
    envia_ordre("G")
def h():
    envia_ordre("H")
def i():
    envia_ordre("I")
def j():
    envia_ordre("J")
