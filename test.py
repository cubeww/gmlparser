import json

import gmlparser

ast = gmlparser.parse_file('test.gml')
print(json.dumps(ast))
