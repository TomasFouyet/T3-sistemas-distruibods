from __future__ import annotations  # Solo lo dejo por si lo necesitan. Lo pueden eliminar
from sys import argv
import json

# Librerías adicionales por si las necesitan
# No son obligatorias y tampoco tienen que usarlas todas
# No puedes agregar ningún otro import que no esté en esta lista
import re
import os
import typing
import collections
import itertools
import dataclasses
import enum

from read_file import read_file
from write_file import write_results
from consultas import ver_query, query_handler

def main():
    if len(argv) < 2:

        return

    input_path = argv[1]
    data = read_file(input_path)

    initial_db: dict[str, str] = data.get("DATA", {})
    servers: list[str] = data.get("SERVERS", [])
    validation: str = data.get("VALIDATION", "forward")
    eventos: list[str] = data.get("TRANSACTIONS", [])
    print("Inicializando sistema con:")
    print("- Base de datos inicial:", initial_db)
    print("- Servidores:", servers)
    print("- Modo de validación:", validation)
    print("- Eventos de transacciones:", eventos)

    
    
    ## FALTA INSTANCIAR MOTOR DE TRANSACCIONES
    
    
    logs: list[str] = []

    for linea in eventos:
        
        line = line.strip()
        print("Procesando línea:", line)
        if not line:
            continue

        if ver_query(line):
            print("Es una consulta.")
            out_line = query_handler(line, tm)
            print("Resultado de la consulta:", out_line)
            logs.append(out_line)
        else:
            print("Es un comando de transacción.")
            # Comandos de transacciones (Parte A)
            ## FALTA IMPLEMENTAR EL MANEJADOR DE EVENTOS
            

    # Salida final
    ## FALTA OBTENER BASE DE DATOS FINAL Y ESTADÍSTICAS
    write_results(
        input_path=input_path,
        log_lines=logs,
        ## AGREGAR BASE DE DATOS FINAL Y ESTADÍSTICAS
    )


if __name__ == "__main__":
    main()