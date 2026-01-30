''' anomenar hysky.py
    desar a microbit
    a main.py cridar husky.executar() en comptes de test.executar() '''

from microbit import *
import xgo
#import radio
import music

i2c.init (freq=100000)          # inicialitza I2C (HuskyLens) 
xgo.set_algorithm (xgo.FACE)    # posa huskylens en mode reconeixement de cares

def executar():
    blk = xgo.get_block()    
    if blk and blk["id"] == 1:   # si veu una cara i reconeix ID1 ...
        music.pitch (880, 150)   # confirmació

while True:
    executar()
    sleep(100)