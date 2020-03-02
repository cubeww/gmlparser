import json

import jsonpickle

import gmlparser


def print_json(o):
    tmp = json.loads(jsonpickle.dumps(o))
    print(json.dumps(tmp, indent=4))


ast = gmlparser.parse_file('test.gml')
if ast is not None:
    print_json(ast)
