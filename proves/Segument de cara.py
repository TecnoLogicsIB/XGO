def executar():
    husky.knock()
    husky.set_algorithm(husky.FACE)

    # --- ZONA DE CALIBRACIÓN (Ajusta estos valores aquí) ---
    # 0x80 es STOP. 
    # Valores menores (0x70...) giran a la derecha.
    # Valores mayores (0x90...) giran a la izquierda.
    

    # -------------------------------------------------------

    CENTRE = 160
    MARGE = 20
    W_MAX = 100
    estat_actual = "PARAT"
    temps_referencia = running_time() 
    fase_busqueda = 0 

    xgo.posicio_inicial_estable()

    while True:
        b = husky.get_block()

        if b and b["id"] == 1:
            display.show(Image.HAPPY)
            temps_referencia = running_time() 
            fase_busqueda = 0
            
            x = b["x"]
            w = b["w"]
            if w < W_MAX:
                if CENTRE - MARGE < x < CENTRE + MARGE:
                    if estat_actual != "CAMINANT":
                        xgo.caminar(0xC0, 0x03)
                        estat_actual = "CAMINANT"
                elif x <= CENTRE - MARGE:
                    if estat_actual != "GIRANT_ESQUERRA":
                        xgo.girar(0x9A, 0x03) # Usa la velocidad calibrada
                        estat_actual = "GIRANT_ESQUERRA"
                elif x >= CENTRE + MARGE:
                    if estat_actual != "GIRANT_DRETA":
                        xgo.girar(0x76, 0x03) # Usa la velocidad calibrada
                        estat_actual = "GIRANT_DRETA"
            else:
                if estat_actual != "PARAT":
                    xgo.stop()
                    estat_actual = "PARAT"

        else:
            display.show(Image.SAD)
            ahora = running_time()
            diferencia = ahora - temps_referencia 

            if fase_busqueda == 0:
                if diferencia < 2000:
                    if estat_actual != "INI_DRETA":
                        xgo.girar(0x76, 0x03)
                        estat_actual = "INI_DRETA"
                else:
                    xgo.stop()
                    sleep(500)
                    fase_busqueda = 1
                    temps_referencia = running_time()

            elif fase_busqueda == 1:
                if diferencia < 5000: 
                    if estat_actual != "BARRIDO_IZQ":
                        xgo.girar(0x9A, 0x03)
                        estat_actual = "BARRIDO_IZQ"
                else:
                    xgo.stop()
                    sleep(500)
                    fase_busqueda = 2
                    temps_referencia = running_time()

            elif fase_busqueda == 2:
                if diferencia < 5000:
                    if estat_actual != "BARRIDO_DER":
                        xgo.girar(0x76, 0x03)
                        estat_actual = "BARRIDO_DER"
                else:
                    xgo.stop()
                    sleep(500)
                    fase_busqueda = 1
                    temps_referencia = running_time()

        sleep(40)
