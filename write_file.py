import os
import json

LOGS_HEADER = "##LOGS##"
DB_HEADER = "##DATABASE##"
STATS_HEADER = "##STATS##"

def create_dir() -> None:
    os.makedirs("logs", exist_ok=True)


def base_name(input_path: str) -> str:
    name = os.path.basename(input_path)
    return os.path.splitext(name)[0]

def write_finals_results(
    input_path: str,
    log_lines: list[str],
    db: dict[str, str],
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
    if len(db) == 0:
        lines.append("No hay datos")
    else:
        for k, v in db.items():
            lines.append(f"{k}={v}")

    lines.append(STATS_HEADER)
    estados = ["ABIERTA", "ABORTADA", "CONFIRMADA", "EN_PREPARACION", "INVALIDA"]
    for estado in estados:
        arr = stats.get(estado, [])
        lines.append(f"{estado}={json.dumps(arr)}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
