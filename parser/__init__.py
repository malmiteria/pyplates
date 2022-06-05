import re
from parser.ifs import parse_ifs
from parser.fors import parse_fors

def render(file_content, *args, **kwargs):
    file_content = parse_fors(file_content)
    file_content = parse_ifs(file_content)
    return file_content
