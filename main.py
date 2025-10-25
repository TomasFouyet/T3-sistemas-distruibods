from __future__ import annotations
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
from simulator import Simulator


def main():
    if len(argv) < 2:
        return

    input_path = argv[1]
    data = read_file(input_path)

    # Inicializa el motor desde dict (sin que el simulador escriba archivos)
    sim = Simulator(test_path=input_path)  # test_path solo por compatibilidad
    sim.init_from_dict(data)

    eventos: list[str] = data.get("TRANSACTIONS", [])
    logs: list[str] = []

    for line in eventos:
        line = line.strip()
        if not line:
            continue
        if ver_query(line):
            out_line = query_handler(line, sim)
            logs.append(out_line)
        else:
            sim.apply_txn_event(line)

    final_db = sim.get_final_database()
    stats = sim.get_stats()

    write_results(
        input_path=input_path,
        log_lines=logs,
        final_db=final_db,
        stats=stats,
    )

if __name__ == "__main__":
    main()
