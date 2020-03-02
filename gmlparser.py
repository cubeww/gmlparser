from gmllexer import Lexer
import copy


def parse_file(filename):
    # 对文本文件进行解析
    with open(filename, 'r', encoding='UTF-8') as f:
        text = f.read()
    return parse_text(text)


def parse_text(text):
    # 对文本进行解析
    # Lexer 工作
    try:
        # 将源文本转化为一个一个的Token，便于后续处理
        lexer = Lexer()
        token_list = lexer.to_token_list(text=text)
    except Exception as err:
        # 输出Lexer错误
        print('Lexer error:')
        print('  %s' % err)
        return
    # Parser 工作
    try:
        # 将转化好的Token列表进行初步解析，生成函数、变量名称、变量数值
        parser = Parser()
        parsed_list = parser.to_parsed_list(token_list=token_list)

        # 对初步解析后的列表进一步解析，生成语句、分支判断、代码块等
        return parser.to_ast_list(parsed_list=parsed_list)
    except Exception as err:
        # 输出Parser错误
        print('Parser error:')
        line = 0
        line_start = 0
        index = parsed_list[parser.index]['index']
        for pos, char in enumerate(text):
            if pos >= index:
                break
            if char == '\n':
                line += 1
                line_start = pos + 1
        print('  line %s' % (line + 1))
        print('    ' + text.splitlines()[line])
        print('    ' + (index - line_start) * ' ' + '^')
        print('SyntaxError: %s' % err)
        raise err
        return


class Parser:
    def __init__(self):
        # Token列表（未解析）
        self.token_list = None

        # 初步解析后的Token列表
        self.parsed_list = None

        # 语法树列表（完全解析后的Token列表）
        self.ast_list = None

        # 当前索引位置
        self.index = 0

    def to_parsed_list(self, token_list):
        # 对Token列表进行初步解析
        self.token_list = token_list
        self.parsed_list = []
        self.index = 0

        for self.index in range(len(self.token_list)):
            # 遍历Token列表，重新创建函数、名称、数值、字符串Token
            if self.token_list[self.index]['token'] == 'Name' and self.token_list[self.index + 1]['token'] == 'Open':
                self.create_functions_token()
            elif self.token_list[self.index]['token'] == 'Name':
                self.create_name_token()
            elif self.token_list[self.index]['token'] == 'Number':
                self.create_value_token()
            elif self.token_list[self.index]['token'] == 'String':
                self.create_string_token()
            else:
                self.create_normal_token()
        return self.parsed_list

    def create_functions_token(self):
        # 创建函数Token
        token = self.token_list[self.index]
        self.parsed_list.append({'token': 'Function', 'index': token['index'], 'text': token['text'], 'children': []})

    def create_name_token(self):
        # 创建变量名Token
        token = self.token_list[self.index]
        self.parsed_list.append({'token': 'Variable', 'index': token['index'], 'text': token['text'], 'children': []})

    def create_value_token(self):
        # 创建数值Token
        token = self.token_list[self.index]
        text = token['text']
        value = None
        if text[0] == '$':
            num = int(text[1:], 16)
            value = num
        else:
            result = 0.0
            try:
                result = float(text)
            except Exception:
                raise Exception("Number %s in incorrect format" % text)
            value = result
        self.parsed_list.append({'token': 'Constant', 'index': token['index'], 'value': value, 'children': []})

    def create_string_token(self):
        # 创建字符串Token
        token = self.token_list[self.index]
        self.parsed_list.append({'token': 'Constant', 'index': token['index'], 'value': token['text'], 'children': []})

    def create_normal_token(self):
        # 创建其它Token
        token = self.token_list[self.index]
        self.parsed_list.append(
            {'token': token['token'], 'index': token['index'], 'text': token['text'], 'children': []})

    def to_ast_list(self, parsed_list):
        # 将初步解析的列表转化为语法树列表
        self.index = 0
        self.ast_list = []
        self.parsed_list = parsed_list
        while self.parsed_list[self.index]['token'] != 'EOF':
            # 遍历初步解析的列表，逐个解析statement
            self.parse_statement(self.ast_list)
        return self.ast_list

    def parse_statement(self, parent):
        # 解析一个statement
        # statement：一条基本语句
        token = self.parsed_list[self.index]['token']
        if token == 'EOF':
            raise Exception('unexpected EOF encountered')
        elif token == 'Var':
            self.parse_var(parent)
        elif token == 'GlobalVar':
            self.parse_globalvar(parent)
        elif token == 'Begin':
            self.parse_block(parent)
        elif token == 'Repeat':
            self.parse_repeat(parent)
        elif token == 'If':
            self.parse_if(parent)
        elif token == 'While':
            self.parse_while(parent)
        elif token == 'For':
            self.parse_for(parent)
        elif token == 'Do':
            self.parse_do(parent)
        elif token == 'With':
            self.parse_with(parent)
        elif token == 'Switch':
            self.parse_switch(parent)
        elif token == 'Case':
            self.parse_case(parent)
        elif token == 'Default':
            self.parse_default(parent)
        elif token == 'Return':
            self.parse_return(parent)
        elif token == 'Function':
            self.parse_function(parent)
        elif token == 'SepStatement':
            pass
        elif token in ('Exit', 'Break', 'Continue'):
            self.ast_list.append(self.clone_current_parsed_token())
            self.index += 1
        else:
            self.parse_assignment(parent)

        while self.parsed_list[self.index]['token'] == 'SepStatement':
            self.index += 1

    def parse_var(self, parent):
        # 解析一个var关键字后的所有名称
        token = self.clone_current_parsed_token('Var')
        self.index += 1
        while self.parsed_list[self.index]['token'] == 'Variable':
            token2 = self.clone_current_parsed_token('Constant')
            token['children'].append(token2)
            self.index += 1
            if self.parsed_list[self.index]['token'] == 'SepArgument':
                self.index += 1
        parent.append(token)

    def parse_globalvar(self, parent):
        # 解析一个globalvar关键字后的所有名称
        token = self.clone_current_parsed_token('GlobalVar')
        self.index += 1
        while self.parsed_list[self.index]['token'] == 'Variable':
            token2 = self.clone_current_parsed_token('Constant')
            token['children'].append(token2)
            self.index += 1
            if self.parsed_list[self.index]['token'] == 'SepArgument':
                self.index += 1
        parent.append(token)

    def parse_block(self, parent):
        # 解析一个代码块{}
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        while self.parsed_list[self.index]['token'] != 'EOF' and self.parsed_list[self.index]['token'] != 'End':
            self.parse_statement(token['children'])
        if self.parsed_list[self.index]['token'] != 'End':
            raise Exception('symbol } expected')
        else:
            self.index += 1

    def parse_repeat(self, parent):
        # 解析一个repeat段落
        self.index += 1
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.parse_expression1(token['children'])

    def parse_expression1(self, parent):
        # 解析一个布尔表达式
        token = self.clone_current_parsed_token('Binary')
        self.parse_expression2(token['children'])
        flag = True
        while self.parsed_list[self.index]['token'] in ('And', 'Or', 'Xor'):
            flag = False
            token['children'].append(self.parsed_list[self.index])
            self.index += 1
            self.parse_expression2(token['children'])
        if flag:
            parent.extend(token['children'])
        else:
            parent.append(token)

    def parse_expression2(self, parent):
        token = self.clone_current_parsed_token('Binary')
        self.parse_expression3(token['children'])
        flag = True
        while self.parsed_list[self.index]['token'] in (
                'Less', 'LessEqual', 'Equal', 'NotEqual', 'Assign', 'Greater', 'GreaterEqual'):
            flag = False
            token['children'].append(self.parsed_list[self.index])
            self.index += 1
            self.parse_expression3(token['children'])
        if flag:
            parent.extend(token['children'])
        else:
            parent.append(token)

    def parse_expression3(self, parent):
        token = self.clone_current_parsed_token('Binary')
        self.parse_expression4(token['children'])
        flag = True
        while self.parsed_list[self.index]['token'] in ('BitOr', 'BitAnd', 'BitXor'):
            flag = False
            token['children'].append(self.parsed_list[self.index])
            self.index += 1
            self.parse_expression4(token['children'])
        if flag:
            parent.extend(token['children'])
        else:
            parent.append(token)

    def parse_expression4(self, parent):
        token = self.clone_current_parsed_token('Binary')
        self.parse_expression5(token['children'])
        flag = True
        while self.parsed_list[self.index]['token'] in ('BitShiftLeft', 'BitShiftRight', 'BitShiftRight'):
            flag = False
            token['children'].append(self.parsed_list[self.index])
            self.index += 1
            self.parse_expression4(token['children'])
        if flag:
            parent.extend(token['children'])
        else:
            parent.append(token)

    def parse_expression5(self, parent):
        token = self.clone_current_parsed_token('Binary')
        self.parse_expression6(token['children'])
        flag = True
        while self.parsed_list[self.index]['token'] in ('Plus', 'Minus'):
            flag = False
            token['children'].append(self.parsed_list[self.index])
            self.index += 1
            self.parse_expression6(token['children'])
        if flag:
            parent.extend(token['children'])
        else:
            parent.append(token)

    def parse_expression6(self, parent):
        token = self.clone_current_parsed_token('Binary')
        self.parse_variable2(token['children'])
        flag = True
        while self.parsed_list[self.index]['token'] in ('Time', 'Divide', 'Div', 'Mod'):
            flag = False
            token['children'].append(self.parsed_list[self.index])
            self.index += 1
            self.parse_variable2(token['children'])
        if flag:
            parent.extend(token['children'])
        else:
            parent.append(token)

    def parse_term(self, parent):
        # 解析一个词汇
        tok = self.parsed_list[self.index]['token']
        if tok == 'Function':
            self.parse_function(parent)
        elif tok == 'Constant':
            parent.append(self.clone_current_parsed_token())
            self.index += 1
        elif tok == 'Open':
            self.index += 1
            self.parse_expression1(parent)
            if self.parsed_list[self.index]['token'] != 'Close':
                raise Exception('Symbol ) expected')
            self.index += 1
        elif tok == 'Variable':
            self.parse_variable(parent)
        elif tok in ('Not', 'Plus', 'Minus', 'BitNegate'):
            token = self.clone_current_parsed_token('Unary')
            self.index += 1
            self.parse_variable2(token['children'])
            parent.append(token)
        else:
            raise Exception('unexpected symbol in expression')

    def parse_variable(self, parent):
        # 解析一个变量，不带有“.”
        if self.parsed_list[self.index]['token'] != 'Variable':
            raise Exception('variable name expected')
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        if self.parsed_list[self.index]['token'] == 'ArrayOpen':
            self.index += 1
            while self.parsed_list[self.index]['token'] != 'ArrayClose' and self.parsed_list[self.index][
                'token'] != 'EOF':
                self.parse_expression1(token['children'])
                if self.parsed_list[self.index]['token'] == 'SepArgument':
                    self.index += 1
                elif self.parsed_list[self.index]['token'] != 'ArrayClose':
                    raise Exception('symbol , or ] expected')
            if self.parsed_list[self.index]['token'] == 'EOF':
                raise Exception('symbol ] expected')
            self.index += 1
            if len(token['children']) >= 3:
                raise Exception('only 1 or 2 dimensional arrays are supported')

    def parse_variable2(self, parent):
        # 解析一个变量名称，可带有“.”
        lst = []
        self.parse_term(lst)
        if self.parsed_list[self.index]['token'] == 'Dot':
            token = self.clone_current_parsed_token('Dot')
            token['children'].extend(lst)
            parent.append(token)
            while self.parsed_list[self.index]['token'] == 'Dot':
                self.index += 1
                self.parse_variable(token['children'])
        else:
            parent.extend(lst)
            pass

    def parse_if(self, parent):
        # 解析一个if段落
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        self.parse_expression1(token['children'])
        if self.parsed_list[self.index]['token'] == 'Then':
            self.index += 1
        self.parse_statement(token['children'])
        if self.parsed_list[self.index]['token'] == 'Else':
            self.index += 1
            self.parse_statement(token['children'])

    def parse_while(self, parent):
        # 解析一个while段落
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        self.parse_expression1(token['children'])
        if self.parsed_list[self.index]['token'] == 'Do':
            self.index += 1
        self.parse_statement(token['children'])

    def parse_for(self, parent):
        # 解析一个for段落
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        if self.parsed_list[self.index]['token'] != 'Open':
            raise Exception('symbol ( expected')
        self.index += 1

        self.parse_statement(token['children'])
        if self.parsed_list[self.index]['token'] == 'SepStatement':
            self.index += 1

        self.parse_expression1(token['children'])
        if self.parsed_list[self.index]['token'] == 'SepStatement':
            self.index += 1

        self.parse_statement(token['children'])
        if self.parsed_list[self.index]['token'] != 'Close':
            raise Exception('symbol ) expected')

        self.index += 1
        self.parse_statement(token['children'])

    def parse_do(self, parent):
        # 解析一个do-until段落
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        self.parse_statement(token['children'])
        if self.parsed_list[self.index]['token'] != 'Until':
            raise Exception('keyword Until expected')
        self.index += 1
        self.parse_expression1(token['children'])

    def parse_with(self, parent):
        # 解析一个with段落
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        self.parse_expression1(token['children'])
        if self.parsed_list[self.index]['token'] == 'Do':
            self.index += 1
        self.parse_statement(token['children'])

    def parse_switch(self, parent):
        # 解析一个switch段落
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        self.parse_expression1(token['children'])
        if self.parsed_list[self.index]['token'] != 'Begin':
            raise Exception('Symbol { expected')
        self.index += 1
        while self.parsed_list[self.index]['token'] != 'End' and self.parsed_list[self.index]['token'] != 'EOF':
            self.parse_statement(token['children'])
        if self.parsed_list[self.index]['token'] != 'End':
            raise Exception('Symbol } expected')
        self.index += 1

    def parse_case(self, parent):
        # 解析一个case分支
        token = self.clone_current_parsed_token()
        self.index += 1
        self.parse_expression1(token['children'])
        if self.parsed_list[self.index]['token'] != 'Label':
            raise Exception('Symbol : expected')
        parent.append(token)
        self.index += 1

    def parse_default(self, parent):
        # 解析一个default分支
        self.index += 1
        item = self.clone_current_parsed_token()
        if self.parsed_list[self.index]['token'] != 'Label':
            raise Exception('Symbol : expected')
        parent.append(item)
        self.index += 1

    def parse_return(self, parent):
        # 解析一个return语句
        token = self.clone_current_parsed_token()
        self.index += 1
        self.parse_expression1(token['children'])
        parent.append(token)

    def parse_function(self, parent):
        # 解析一个函数
        if self.parsed_list[self.index]['token'] != 'Function':
            raise Exception('Function name expected')
        token = self.clone_current_parsed_token()
        parent.append(token)
        self.index += 1
        if self.parsed_list[self.index]['token'] != 'Open':
            raise Exception('Symbol ( expected')
        self.index += 1
        while self.parsed_list[self.index]['token'] != 'EOF' and self.parsed_list[self.index]['token'] != 'Close':
            self.parse_expression1(token['children'])
            if self.parsed_list[self.index]['token'] == 'SepArgument':
                self.index += 1
            elif self.parsed_list[self.index]['token'] != 'Close':
                raise Exception('Symbol , or ) expected')
        if self.parsed_list[self.index]['token'] != 'Close':
            raise Exception('Symbol ) expected')
        else:
            self.index += 1

    def parse_assignment(self, parent):
        # 解析一个赋值语句
        token = self.clone_current_parsed_token("Assign")
        parent.append(token)

        self.parse_variable2(token['children'])
        tok = self.parsed_list[self.index]['token']
        if tok in ('Assign', 'AssignPlus', 'AssignMinus', 'AssignTimes',
                   'AssignDivide', 'AssignOr', 'AssignAnd', 'AssignXor'):
            token['children'].append(self.clone_current_parsed_token())
            self.index += 1
            self.parse_expression1(token['children'])
        else:
            raise Exception('Assignment operator expected')

    def clone_current_parsed_token(self, new_token=None):
        # 拷贝一份当前初步解析的Token
        # 注：这里必须深copy，否则会造成循环引用
        tok = copy.deepcopy(self.parsed_list[self.index])
        if new_token is not None:
            tok['token'] = new_token
        return tok
