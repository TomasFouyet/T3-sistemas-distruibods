import os
import json
import typing

LOGS_HEADER = "##LOGS##"
DB_HEADER = "##DATABASE##"
STATS_HEADER = "##STATS##"

def create_dir() -> None:
    os.makedirs("logs", exist_ok=True)


def base_name(input_path: str) -> str:
    name = os.path.basename(input_path)
    return os.path.splitext(name)[0]

def write_results(
    input_path: str,
    log_lines: list[str],
    final_db: dict[str, str],
    stats: dict[str, list[str]],
) -> None:
    
    create_dir()
    out_name = f"{base_name(input_path)}.txt"
    out_path = os.path.join("logs", out_name)

    lines: list[str] = []
    lines.append(LOGS_HEADER)
    if len(log_lines) == 0:
        lines.append("No hubo logs")
    else:
        lines.extend(log_lines)

    lines.append(DB_HEADER)
    if len(final_db) == 0:
        lines.append("No hay datos")
    else:
        for k, v in final_db.items():
            lines.append(f"{k}={v}")

    lines.append(STATS_HEADER)
    order = ["ABIERTA", "ABORTADA", "CONFIRMADA", "EN_PREPARACION", "INVALIDA"]
    for key in order:
        arr = stats.get(key, [])
        lines.append(f"{key}={json.dumps(arr)}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
