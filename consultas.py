import json
import typing

def ver_query(line: str) -> bool:
    print("Verificando si es query:", line)
    return line.startswith("C;")

def query_handler(line: str, txn_manager) -> str:
    _, query, var = line.split(";", 2)
    var = var.strip()

    if query == "READ_POSSIBLE_VALUES":
        print("Manejando READ_POSSIBLE_VALUESs para variable:", var)
       ## FALTA IMPLEMENTAR READ_POSSIBLE_VALUES
        #return json.dumps(list(values))

    if query == "READ_COMMIT":
        print("Manejando READ_COMMIT para variable:", var)
         ## FALTA IMPLEMENTAR READ_COMMIT
        #return val if val is not None else "NULL"

    print("Tipo de query desconocido:", query)
    return ""