# ==== imports ====
from microbit import *
import xgo
import husky
from veu import VeuDF2301Q
import radio
import music

i2c.init(freq=100000)    # inicialització de l'I2C
sensor = VeuDF2301Q()    # inicialització mòdul veu (DF2301Q)
sensor.configurar (volum=7, wake_time=20, mute=False)  # wake_time: temps despert (segons)

mode ='A'

def executar():          # funció principal cridada des de main.py
    global mode
    xgo.posicio_inicial_estable()  # posició inicial del robot
    
    while True:
        pkt = radio.receive_full()
        
        if pkt:
            data = pkt[0]
            if data:                
                if b"XGO:C" in data:
                    display.show('C')
                    mode = 'C'
                elif b"XGO:SURT" in data:
                    return
        
        if mode =='C':
            display.show('C')
            reconeix_veu()

        sleep(50)

def reconeix_veu():
    cmd = sensor.get_cmdid()    # obté l'id del que escolta (0 si no reconeix)
    
    if cmd == 5:      
        xgo.executar_accio (17)
        
    elif cmd == 6:    
        xgo.executar_accio (11)
        
    elif cmd == 7:    
        xgo.executar_accio (19)
        
    elif cmd == 8:    
        xgo.executar_accio (18)     
       
    sleep(500)

