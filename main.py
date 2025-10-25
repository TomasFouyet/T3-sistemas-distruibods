from __future__ import annotations
from sys import argv
from simulator import Simulator

if __name__ == "__main__":
    if len(argv) < 2:
        pass
    else:
        sim = Simulator(argv[1])
        sim.run()
