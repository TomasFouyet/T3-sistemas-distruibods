from __future__ import annotations
from sys import argv
import json

import re
import os
import typing
import collections
import itertools
import dataclasses
import enum

from read_file import read_file
from write_file import write_finals_results
from consultas import ver_query, query_handler
from simulator import Simulator


def main():
    if len(argv) < 2:
        return

    input_path = argv[1]
    data = read_file(input_path)

    sim = Simulator(test_path=input_path)
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

    write_finals_results(
        input_path=input_path,
        log_lines=logs,
        db=final_db,
        stats=stats,
    )

if __name__ == "__main__":
    main()
