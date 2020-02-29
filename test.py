import gmlparser
import jsonpickle
import json


def print_json(o):
    tmp = json.loads(jsonpickle.dumps(o))
    print(json.dumps(tmp, indent=4))


ast = gmlparser.parse_file('test.gml')
print_json(ast)
