# microbit_main
# resposta a comandaments de veu amb prefix

from microbit import *
import xgo
import music    # si volem sons d'activació o el que sigui
#import accions

ultima = ""
actiu = False
prefix = False  # només acceptarem una comanda si és True, en rebre un pols A

# ==================================================================

def executa(cmd):
    global ultima
    if cmd == ultima:
        return    # surt de la funció
    ultima = cmd
    
    # no inclourem aqui l'acció associada al pols A, perquè A el reservarem com a prefix dels comandaments 
    # no inclourem aqui l'acció associada al pols K, perquè K només serveix per activar el robot
    if cmd == "B":    
        display.show("B")
    elif cmd == "C":  
        display.show("C")
    elif cmd == "D":  
        display.show("D")
    elif cmd == "E":  
        display.show("E")
    elif cmd == "F":  
        display.show("F")
    elif cmd == "G": 
        display.show("G")
    elif cmd == "H":  
        display.show("H")
    elif cmd == "I":  
        display.show("I")
    elif cmd == "J":  
        display.show("H")
        
# -------------------------------------------

def llegir_cmd():
    if pin1.read_digital() == 1:
        t0 = running_time()
        while pin1.read_digital() == 1:
            sleep(1)
        durada = running_time() - t0
        return classifica(durada)
    return ""

def classifica(durada):
    if 40 <= durada < 80:    # aquest pols es reserva com a prefix
        return "A"
    elif 80 <= durada < 120:
        return "B"
    elif 120 <= durada < 160:
        return "C"
    elif 160 <= durada < 200:
        return "D"
    elif 200 <= durada < 240:
        return "E"
    elif 240 <= durada < 280:
        return "F"
    elif 280 <= durada < 320:
        return "G"
    elif 320 <= durada < 360:
        return "H"
    elif 360 <= durada < 400:
        return "I"
    elif 400 <= durada < 440:
        return "J"
    elif 440 <= durada < 480:    # aquest pols es reserva per activar el robot
        return "K"
    else:
        return ""

# ===================================================

while True:
    cmd = llegir_cmd()

    if not actiu:    
        if cmd == "K":       # activació
            for y in range(5):
                display.set_pixel(0, y, 9)
            music.pitch(1000, 50)    # indicador sonor de robot inicialitzat
            sleep(100)
            xgo.inicialitzar(0xA0)    # aqui ocupem l'UART
            actiu = True
            ultima = ""

    else:   # si el robot està actiu ...
        if cmd == "A":              # si arriva A ...
            prefix = True           # activa el prefix
            music.pitch(500, 10)    # indicador sonor molt curt

        elif cmd != "" and prefix:  # si arriva qualsevol altra comanda després de la A ...
                executa(cmd)        # executa la comanda
                prefix = False      # desactiva el prefix (la A ja s’ha consumit)

    sleep(10)
