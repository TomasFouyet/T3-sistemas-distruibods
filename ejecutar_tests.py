import subprocess
import os

COMANDO_PYTHON = "python3"


def ejecutar_tests(ruta_entrada, mostrar_prints, tiempo_maximo):
    if mostrar_prints:
        subprocess.run([COMANDO_PYTHON, "main.py", ruta_entrada], timeout=tiempo_maximo)
    else:
        subprocess.run(
            [COMANDO_PYTHON, "main.py", ruta_entrada],
            timeout=tiempo_maximo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def leer_archivo(ruta):
    with open(ruta, encoding="utf-8") as f:
        return [linea.strip() for linea in f.readlines() if linea.strip() != ""]


def clean_list(s):
    x = s.strip("[]").replace("'", "").replace('"', "")
    x = x.split(",")
    return [x.strip() for x in x]


def verificar_tests(test):
    name = test.replace(".jsonc", ".txt")
    archivo_referencia = leer_archivo(os.path.join("logs_esperados", f"{name}"))

    try:
        archivo_alumno = leer_archivo(os.path.join("logs", f"{name}"))
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de logs para {test}")
        return

    index_base_datos_referencia = archivo_referencia.index("##DATABASE##")
    index_base_datos_alumno = archivo_alumno.index("##DATABASE##")

    index_stats_referencia = archivo_referencia.index("##STATS##")
    index_stats_alumno = archivo_alumno.index("##STATS##")

    print(f"\n 💸 Verificando {test}...")

    correctos_logs = 0
    if index_base_datos_referencia != index_base_datos_alumno:
        print("  ⚠️ Alerta ⚠️ - La sección de Logs no es del mismo tamaño que la de solución")
    for i in range(1, index_base_datos_referencia):
        if i >= len(archivo_alumno):
            print("  ❌ Faltan líneas en el log, se deja de verificar esta parte")
            break

        # Se espera una lista
        if "[" in archivo_referencia[i]:
            try:
                lista_referencia = clean_list(archivo_referencia[i])
                lista_alumno = clean_list(archivo_alumno[i])
                set_referencia = set(lista_referencia)
                set_alumno = set(lista_alumno)

                if set_referencia != set_alumno:
                    print(f"  ❌ Error en línea {i+1}:")
                    print(f"       Esperado en la solución: {archivo_referencia[i]}")
                    print(f"       Encontrado en la entrega: {archivo_alumno[i]}")
                    continue
                correctos_logs += 1
                continue
            except Exception:
                print(f"  ❌ Error en línea {i+1}: No se pudo interpretar la lista")
                print(f"       Esperado en la solución: {archivo_referencia[i]}")
                print(f"       Encontrado en la entrega: {archivo_alumno[i]}")
                continue

        # Se espera un dato simple
        else:
            if archivo_alumno[i] != archivo_referencia[i]:
                print(f"  ❌ Error en línea {i+1}:")
                print(f"       Esperado en la solución: {archivo_referencia[i]}")
                print(f"       Encontrado en la entrega: {archivo_alumno[i]}")
                continue
            correctos_logs += 1

    set_db_alumno = set(archivo_alumno[index_base_datos_alumno + 1: index_stats_alumno])
    set_db_referencia = set(
        archivo_referencia[index_base_datos_referencia + 1: index_stats_referencia]
    )

    # Ver cuantos datos correctos del alumno están en la base de datos
    # Descontar si el aluno tiene más datos que la solución
    datos_extras = max(0, len(set_db_alumno) - len(set_db_referencia))
    correctos_db = len(set_db_alumno.intersection(set_db_referencia))

    if datos_extras > 0:
        print("  ❌ Alerta - La base de datos del estudiante tiene más datos de lo esperado")

    stats_esperados = archivo_referencia[index_stats_referencia + 1:]
    stats_esperados_dict = {}
    for line in stats_esperados:
        key, value = line.split("=", 1)
        value = clean_list(value)
        stats_esperados_dict[key] = set(value)

    stats_alumno = archivo_alumno[index_stats_alumno + 1:]
    stats_alumno_dict = {}
    for line in stats_alumno:
        key, value = line.split("=", 1)
        value = clean_list(value)
        stats_alumno_dict[key] = set(value)

    correctas_stats = 0
    for stat in stats_esperados_dict:
        if stat not in stats_alumno_dict:
            print(f"  ❌ Error en stats: No se encontró la estadística '{stat}' en la entrega")
            continue
        if stats_esperados_dict[stat] != stats_alumno_dict[stat]:
            print(f"  ❌ Error en stats: La estadística '{stat}' no coincide con la solución")
            print(f"       Esperado en la solución: {stats_esperados_dict[stat]}")
            print(f"       Encontrado en la entrega: {stats_alumno_dict[stat]}")
            continue
        correctas_stats += 1

    print(f"  Resultados para {test}:")
    print(f"  -- Logs correctos: {correctos_logs}/{index_base_datos_referencia - 1}")
    print(f"  -- Datos de la BD correctos: {correctos_db}/{len(set_db_referencia)}")
    print(f"  -- Datos extras en la BD del estudiante: {datos_extras}")
    print(f"  -- Stats correctos: {correctas_stats}/5")

    puntaje_esperado = len(archivo_referencia) - 3
    puntaje_final = max(correctos_logs + correctos_db + correctas_stats - datos_extras, 0)
    print(f"  => Puntaje final para {test}: {puntaje_final} de {puntaje_esperado}")


if __name__ == "__main__":
    CARPETA_FORWARD = os.path.join("tests_publicos", "forward")
    CARPETA_BACKWARD = os.path.join("tests_publicos", "backward")

    tests_f = [x for x in os.listdir(CARPETA_FORWARD) if x.endswith(".jsonc")]
    tests_b = [x for x in os.listdir(CARPETA_BACKWARD) if x.endswith(".jsonc")]

    mostrar_prints = False
    for test in sorted(tests_f):
        ejecutar_tests(
            ruta_entrada=os.path.join(CARPETA_FORWARD, test),
            mostrar_prints=mostrar_prints,
            tiempo_maximo=1,
        )
        verificar_tests(test=test)

    for test in sorted(tests_b):
        ejecutar_tests(
            ruta_entrada=os.path.join(CARPETA_BACKWARD, test),
            mostrar_prints=mostrar_prints,
            tiempo_maximo=1,
        )
        verificar_tests(test=test)

    ejecutar_tests(
        ruta_entrada=os.path.join("tests_publicos", "ejemplo_enunciado.jsonc"),
        mostrar_prints=mostrar_prints,
        tiempo_maximo=1,
    )
    verificar_tests(test="ejemplo_enunciado.jsonc")

    print("¡Tests finalizados!")
