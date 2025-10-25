import re
import json
import typing

_JSONC_COMMENT_RE = re.compile(r"//.*?$", flags=re.MULTILINE)

def read_file(file_path: str) -> dict:
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content_cleaned = re.sub(_JSONC_COMMENT_RE, '', content)
    data = json.loads(content_cleaned)
    
    return data