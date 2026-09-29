# Libraries we need to import
#pip install pyopensky # run in terminal
# pip install traffic # run in terminal
from pyopensky.rest import REST
print("pyopensky OK")
from pyopensky.trino import Trino
print("trino OK")
import pandas as pd
print("pandas OK")
import traffic
print("traffic OK")
import time
print("Time OK")

###############################
# pruebas previas al programa #
###############################
print(" ------------------------------------ Checks to see if everything works ------------------------------------ ")
# aviones que estan ahora en el aire 
rest = REST()

states = rest.states()

#print(states)

# i mprimimos todas las variables para saber que tenemos 
print("Available variables/Variables Disponibles:")
for variable in states.columns:
    print(variable)

# comprobamos cuantos aviones diferentes hay y cuantos registros tiene nuestra base de datos 
print("--------------------------------------------------------")
print("Número de registros/Number of records:", len(states))
print("Aviones diferentes/Different airplanes:", states["icao24"].nunique())

# Conectamos con OpenSky
rest = REST()

###########################################
# Values usesd in functions (to modify)   #
###########################################
MAX_CONSULTAS = 1 # numero consultas en vigilancia normal / number of checks in the function "normal_Surveillance"
TIEMPO_NORMAL = 4 # tiempo de espera despues de cada busqueda en vigilancia normal / time to wait between checks
ALTURA_MINIMA = 100 # altura minima a la que si ocurre algo se sospecha / minimum altitude where we start to become suspicious
DESCENSO_PELIGROSO = 0.1 # descenso peligroso considerado / Vertical descent we consider too fast
n = 7 # numero consultas para el programa intensivo / number of checks in the function "extreme_Surveillance"
t= TIEMPO_NORMAL # tiempo de espera entre consultas para vigilancia intensiva / time between checks in "extreme_Surveillance"
DIFERENCIA_PELIGROSA = 100 
ALTURA_ACCIDENTE=500 
VELOCIDAD_ACCIDENTE = 300 # velocidad minima a la que sospechamos / minimum velocity where we start to suspect 
###########################################
# programa de vigilacia normal #
###########################################

# esta funcion llama a opensky, y obtiene la base de datos de aviones que estan volando a tiempo real, chequea si cumplen 3 condiciones
# entre als cuales estan, comprobar codigos de emergencia, comrpobar altitud y descenso, si cumple que tiene codigo de mergencia, o esta muy alto y tiene un descenso alto 
# entonces los que cumplan las 3 condiciones seran añadidos a una tabla para su posterior analisis.






# the code below is in spanish: 





print(" ------------------------------------ Funcion Vigilancia Normal ------------------------------------ ")
# Funcion para la vigilancia normal, una vez detectada la anomalia, se pasa a vigilancia intensiva en otra funcion
def vigilancia_normal(rest, max_consultas, tiempo_normal):
    
    codigos_emergencia = ["7500", "7600", "7700"]

    for consulta in range(1, max_consultas + 1):

        print(f"\n========== CONSULTA {consulta}/{max_consultas} ==========")

        # Consultamos OpenSky
        states = rest.states()

        print(f"Aviones encontrados: {len(states)}")

        # Buscamos códigos de emergencia
        emergencias = states[
            states["squawk"].astype(str).str.strip().isin(codigos_emergencia)
        ]

        # Buscamos descensos rápidos
        descensos = states[
            states["vertical_rate"] < DESCENSO_PELIGROSO
        ]

        # buscamos aviones por encima de x altura
        altura_considerable = states[
            states["altitude"] > ALTURA_MINIMA 
        ]          

        # Comprobamos si hay algo sospechoso
        if not emergencias.empty or not descensos.empty:

            print("\nACTIVIDAD SOSPECHOSA DETECTADA")

            if not emergencias.empty:
                print("\nAviones con código de emergencia:")
                print("=========================================================================================")
                print(
                    emergencias[
                        [
                            "icao24",
                            "callsign",
                            "origin_country",
                            "altitude",
                            "longitude",
                            "latitude",
                            "groundspeed",
                            "vertical_rate",
                            "squawk"
                        ]
                    ].to_string(index=False)
                )

            if not altura_considerable.empty: 
                print("\nAviones a gran altura:")
                print("=========================================================================================") 
                print( 
                    altura_considerable[
                          [
                                "icao24",
                                "callsign",
                                "origin_country",
                                "altitude",
                                "longitude",
                                "latitude",
                                "groundspeed",
                                "vertical_rate",
                                "squawk" 
                            ] 
                        ].head(10).to_string(index=False) 
                )

            if not descensos.empty:
                print("\nAviones con descenso rápido:")
                print("=========================================================================================")
                print(
                    descensos[
                        [
                            "icao24",
                            "callsign",
                            "origin_country",
                            "altitude",
                            "longitude",
                            "latitude",
                            "groundspeed",
                            "vertical_rate",
                            "squawk"
                        ]
                    ].to_string(index=False)
                )

            # Ahora calculamos el riesgo
            riesgo = states[ 
                  states["squawk"].astype(str).str.strip().isin(codigos_emergencia) 
                  & (states["altitude"] > ALTURA_MINIMA) 
                  & (states["vertical_rate"] < DESCENSO_PELIGROSO) 
                ]
            # en este IF se comprueba si algun avion cumple con los 3 umbrales puestos antes, y si existe, lo imprime por pantalla y lo añade a una tabla nueva 
            if not riesgo.empty: 
                print("\n======================================") 
                print("RIESGO DETECTADO") 
                print("======================================") 
                print( riesgo
                      [ 
                        [ 
                            "icao24", 
                            "callsign", 
                            "altitude", 
                            "vertical_rate", 
                            "squawk", 
                            "latitude", 
                            "longitude",
                            "groundspeed" 
                        ] 
                    ].to_string(index=False) ) 
                # Guardamos los aviones para vigilancia intensiva en una tabla
                aviones_riesgo = riesgo
                [ 
                    [ 
                        "icao24", 
                        "callsign", 
                        "altitude", 
                        "vertical_rate", 
                        "squawk", 
                        "latitude", 
                        "longitude",
                        "groundspeed" 
                    ] 
                ].copy() 
                print("\nPasando a vigilancia intensiva...")

                # Devolvemos SOLO los aviones de riesgo 
                return aviones_riesgo 
            else: 
                print("\nNo hay aviones que cumplan las 3 condiciones.") 
                # Esperar antes de la siguiente consulta 
            if consulta < max_consultas: 
                print(f"Esperando {tiempo_normal} segundos...") 
                time.sleep(tiempo_normal) 
            # ============================================== 
            # # FIN SIN RIESGO 
            # ============================================== 
            print("\n======================================") 
            print("FIN DEL PROGRAMA") 
            print("======================================") 
            print(f"No se detectó riesgo después de {max_consultas} consultas.") 

            return None












def vigilancia_intensiva(aviones_riesgo, n, t, ALTURA_ACCIDENTE, VELOCIDAD_ACCIDENTE):

    # ============================================================
    # TABLA DE POSIBLES ACCIDENTES
    # ============================================================

    aviones_accidente = pd.DataFrame(
        columns=[
            "icao24",
            "callsign",
            "altura_emergencia",
            "groundspeed_emergencia",
            "altura_1",
            "groundspeed_1",
            "altura_2",
            "groundspeed_2"
        ]
    )

    # ============================================================
    # TABLA DE AVIONES QUE VAMOS A VIGILAR
    # ============================================================

    vigilancia = aviones_riesgo[
        [
            "icao24",
            "callsign",
            "altitude",
            "groundspeed"
        ]
    ].copy()

    vigilancia = vigilancia.rename(
        columns={
            "altitude": "altura_emergencia",
            "groundspeed": "groundspeed_emergencia"
        }
    )

    # Convertimos groundspeed de m/s a km/h
    vigilancia["groundspeed_emergencia"] = (
        vigilancia["groundspeed_emergencia"] * 3.6
    )

    # Creamos las columnas para las mediciones posteriores
    vigilancia["altura_1"] = None
    vigilancia["groundspeed_1"] = None

    vigilancia["altura_2"] = None
    vigilancia["groundspeed_2"] = None

    # ============================================================
    # LOOP DE CONSULTAS
    # ============================================================

    for consulta in range(1, n + 1):

        print(
            f"\n========== Consulta Intensiva: "
            f"{consulta}/{n} =========="
        )

        # Nueva consulta a OpenSky
        rest = REST()
        states = rest.states()

        # ========================================================
        # BUSCAMOS CADA AVIÓN
        # ========================================================

        for indice, avion in vigilancia.iterrows():

            icao = avion["icao24"]

            print("\n==============================")
            print("ICAO QUE ESTOY BUSCANDO:", repr(icao))

            filtro = states["icao24"] == icao

            print("Número de coincidencias:", filtro.sum())

            avion_actual = states[filtro]

            print("Filas de avion_actual:", len(avion_actual))
            print("==============================")

            # ----------------------------------------------------
            # Si no aparece en esta consulta
            # ----------------------------------------------------

            if avion_actual.empty:

                print(
                    f"{icao} no aparece en esta consulta."
                )

                continue

            # ----------------------------------------------------
            # OBTENER ALTURA ACTUAL
            # ----------------------------------------------------

            altura_actual = avion_actual.iloc[0]["altitude"]

            if pd.isna(altura_actual):

                print(
                    f"{icao} aparece, pero no tiene "
                    f"altitude disponible."
                )

                continue

            # ----------------------------------------------------
            # OBTENER GROUNDSPEED ACTUAL
            # ----------------------------------------------------

            groundspeed_actual = avion_actual.iloc[0]["groundspeed"]

            if pd.isna(groundspeed_actual):

                print(
                    f"{icao} aparece, pero no tiene "
                    f"groundspeed disponible."
                )

                continue

            # OpenSky proporciona groundspeed en m/s
            # Lo convertimos a km/h

            groundspeed_actual = groundspeed_actual * 3.6

            # ----------------------------------------------------
            # GUARDAR LAS MEDICIONES
            # ----------------------------------------------------

            vigilancia.loc[indice, "altura_1"] = (
                vigilancia.loc[indice, "altura_2"]
            )

            vigilancia.loc[indice, "groundspeed_1"] = (
                vigilancia.loc[indice, "groundspeed_2"]
            )

            vigilancia.loc[indice, "altura_2"] = (
                altura_actual
            )

            vigilancia.loc[indice, "groundspeed_2"] = (
                groundspeed_actual
            )

            # ----------------------------------------------------
            # MOSTRAR DATOS
            # ----------------------------------------------------

            print("\nDATOS DEL AVIÓN")

            print(
                f"ICAO: {icao}"
            )

            print(
                f"Altura emergencia: "
                f"{vigilancia.loc[indice, 'altura_emergencia']}"
            )

            print(
                f"Groundspeed emergencia: "
                f"{vigilancia.loc[indice, 'groundspeed_emergencia']:.2f} km/h"
            )

            print(
                f"Altura 1: "
                f"{vigilancia.loc[indice, 'altura_1']}"
            )

            print(
                f"Groundspeed 1: "
                f"{vigilancia.loc[indice, 'groundspeed_1']}"
            )

            print(
                f"Altura 2: "
                f"{vigilancia.loc[indice, 'altura_2']}"
            )

            print(
                f"Groundspeed 2: "
                f"{vigilancia.loc[indice, 'groundspeed_2']:.2f} km/h"
            )

        # ========================================================
        # COMPROBAR POSIBLES ACCIDENTES
        # ========================================================

        for indice, avion in vigilancia.iterrows():

            altura_1 = avion["altura_1"]
            altura_2 = avion["altura_2"]

            velocidad_1 = avion["groundspeed_1"]
            velocidad_2 = avion["groundspeed_2"]

            # ----------------------------------------------------
            # NECESITAMOS AL MENOS UNA MEDICIÓN ANTERIOR
            # ----------------------------------------------------

            if (
                pd.isna(altura_1)
                or pd.isna(altura_2)
                or pd.isna(velocidad_1)
                or pd.isna(velocidad_2)
            ):
                continue

            # ====================================================
            # CONDICIONES DE POSIBLE ACCIDENTE
            # ====================================================

            # 1. El avión está descendiendo
            esta_descendiendo = altura_2 < altura_1

            # 2. Está a muy baja altura
            altura_muy_baja = altura_2 <= ALTURA_ACCIDENTE

            # 3. Mantiene una velocidad elevada
            velocidad_elevada = (
                velocidad_2 >= VELOCIDAD_ACCIDENTE
            )

            # ====================================================
            # SI CUMPLE LAS TRES CONDICIONES
            # ====================================================

            if (
                esta_descendiendo
                and altura_muy_baja
                and velocidad_elevada
            ):

                print(                    "\n======================================"                )
                print(                    "       POSIBLE ACCIDENTE"                )
                print(                    "======================================"                )

                print(
                    f"Avión: {avion['callsign']} "
                    f"({avion['icao24']})"
                )

                print(
                    f"Altura anterior: "
                    f"{altura_1} ft"
                )

                print(
                    f"Altura actual: "
                    f"{altura_2} ft"
                )

                print(
                    f"Velocidad anterior: "
                    f"{velocidad_1:.2f} km/h"
                )

                print(
                    f"Velocidad actual: "
                    f"{velocidad_2:.2f} km/h"
                )

                # ------------------------------------------------
                # GUARDAR POSIBLE ACCIDENTE
                # ------------------------------------------------

                aviones_accidente.loc[
                    len(aviones_accidente)
                ] = [
                    avion["icao24"],
                    avion["callsign"],
                    avion["altura_emergencia"],
                    avion["groundspeed_emergencia"],
                    altura_1,
                    velocidad_1,
                    altura_2,
                    velocidad_2
                ]

        # ========================================================
        # MOSTRAR ACCIDENTES DETECTADOS
        # ========================================================

        if not aviones_accidente.empty:

            print(
                "\n========== POSIBLES ACCIDENTES =========="
            )

            print(
                aviones_accidente.to_string(
                    index=False
                )
            )

            return aviones_accidente

        # ========================================================
        # ESPERAR ANTES DE LA SIGUIENTE CONSULTA
        # ========================================================

        if consulta < n:

            print(
                f"\nEsperando {t} segundos..."
            )

            time.sleep(t)

        # ============================================================
        # FIN SIN ACCIDENTES
        # ============================================================
        if aviones_accidente.empty:
            print(
                "\nNo se han detectado posibles accidentes."
            )

            return None










# -----------------------------------
# llamamiento a las funciones
# -----------------------------------
#rest = REST()
#aviones_riesgo = vigilancia_normal(rest,MAX_CONSULTAS,TIEMPO_NORMAL)

#una vez creado la funcion de vigilancia intensiva, realizamios el if statement que permitira ejecutar la funcion en caso de ser necesario
#if aviones_riesgo is not None:
#    vigilancia_intensiva(aviones_riesgo,n,t,ALTURA_ACCIDENTE, VELOCIDAD_ACCIDENTE)





# funcion para Ejecutar todo el programa de una y para el bot de telegram
def iniciar_vigilancia():
    rest = REST()
    aviones_riesgo = vigilancia_normal(rest,MAX_CONSULTAS,TIEMPO_NORMAL)

    if aviones_riesgo is not None:

        aviones_accidente = vigilancia_intensiva(aviones_riesgo,n,t,DIFERENCIA_PELIGROSA,VELOCIDAD_ACCIDENTE)

        return aviones_accidente
    else: 
        print("No se encontraron aviones con riesgo de accidente.")
        return None
        

