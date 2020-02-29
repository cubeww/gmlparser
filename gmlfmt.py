from gmllexer import Lexer
from gmlparser import Parser
from ast import AST
import jsonpickle
import json


def parse_file(filename):
    # 对文本文件进行解析
    with open(filename, 'r', encoding='UTF-8') as f:
        text = f.read()
    parse_text(text)


def parse_text(text):
    # 对文本进行解析

    # 第一步：源文本转换为Token列表
    # 将源文本转化为一个一个的Token，便于后续处理
    lexer = Lexer()
    token_list = lexer.to_token_list(text=text)

    # 第二步：对Token列表进行初步解析
    # 将转化好的Token列表进行初步解析，生成函数、变量名称、变量数值
    parser = Parser()
    parsed_list = parser.to_parsed_list(token_list=token_list)

    # 第三步：将初步解析后的列表转换为语法树
    # 对初步解析后的列表进一步解析，生成语句、分支判断、代码块等
    ast_list = parser.to_ast_list(parsed_list=parsed_list)
    print_json(ast_list)


def print_json(o):
    tmp = json.loads(jsonpickle.dumps(o))
    print(json.dumps(tmp, indent=4))


if __name__ == '__main__':
    # 测试
    parse_file('test.gml')
