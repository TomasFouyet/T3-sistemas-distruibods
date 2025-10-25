import json

def ver_query(line: str) -> bool:
    # print("linea empieza con C; ", line.startswith("C;"))
    return line.startswith("C;")

def query_handler(line: str, engine) -> str:
    # print( line)
    
    parts = [p.strip() for p in line.split(";", 2)]
    if len(parts) < 3:
        return ""
    _, query, var = parts

    if query == "READ_POSSIBLE_VALUES":
        # print("ENTRE AQUI EN READ POSSIBLE VALUES")
        values = engine.get_possible_values(var)
        return json.dumps(list(values))

    if query == "READ_COMMIT":
        # print("ENTRE AQUI EN READ COMMIT")
        val = engine.get_committed_value(var)
        return val if val is not None else "NULL"

    return ""
