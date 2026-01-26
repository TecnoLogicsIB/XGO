from microbit import *
import xgo

# Inicialitza I2C (HuskyLens)
i2c.init(freq=100000)

# 1) Comprovar connexió
if not xgo.knock():
    display.show(Image.NO)
    sleep(1000)
else:
    display.show(Image.HAPPY)
    sleep(500)

# 2) Posar HuskyLens en reconeixement de cares
if not xgo.set_algorithm(xgo.FACE):
    display.show(Image.SAD)
    sleep(1000)

# 3) Bucle: si detecta ID1 => cara somrient
while True:
    b = xgo.get_block()   # retorna None o un diccionari {"x","y","w","h","id"}
    if b and b["id"] == 1:
        display.show(Image.HAPPY)
    else:
        display.clear()
    sleep(150)
