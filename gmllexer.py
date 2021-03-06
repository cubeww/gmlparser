class Lexer:
    def __init__(self):
        # 当前字符位置
        self.index = 0
        # GML文本
        self.text = ''

    def to_token_list(self, text):
        # 将源文本转化为Token列表
        self.text = text
        self.index = 0
        token_list = []

        flag = False
        while not flag:
            # 如果当前Token不是EOF，就继续读取下一个Token
            token = self.next_token()
            token_list.append(token)

            if token['token'] == 'EOF':
                flag = True
        # 返回解析好的Token列表
        return token_list

    def skip_whitespace(self):
        # 跳过空白符（空格，换行符，制表符）
        flag = False
        while not flag:
            while self.index < len(self.text) and self.text[self.index].isspace():
                # 如果当前字符是空白符，将索引位置加一
                self.index += 1
            if self.index < len(self.text) and self.text[self.index] == '/':
                # 如果当前字符是/，紧接着判断下一个字符是单行注释/还是多行注释*
                if self.index + 1 < len(self.text):
                    # 如果是*，读取到*/位置
                    if self.text[self.index + 1] == '*':
                        self.index += 2
                        while self.index < len(self.text) and (
                                self.text[self.index] != '*' or self.text[self.index + 1] != '/'):
                            # 不满足当前字符和下一个字符依次是*和/，继续读取
                            self.index += 1
                        if self.index >= len(self.text):
                            # 未在字符串最后发现*/，抛出异常
                            raise Exception('unclosed comment (/*) at tend of script')
                        else:
                            # 读取到*/，跳过这两个字符，继续
                            self.index += 2
                    elif self.text[self.index + 1] == '/':
                        # 读取到单行注释
                        self.index += 2
                        while self.index < len(self.text) and self.text[self.index] != '\n' and self.text[
                            self.index] != '\r':
                            # 向后读取，直到当前字符是换行符
                            self.index += 1
                        # 读取到换行符，跳过这个字符，继续
                        self.index += 1
                    else:
                        # 读取到非空白符，退出
                        flag = True
                else:
                    flag = True
            else:
                flag = True

    def next_token(self):
        # 读取下一个Token
        # 跳过空白符
        self.skip_whitespace()
        # 超出长度检查
        if self.index >= len(self.text):
            return {'token': 'EOF', 'index': self.index, 'text':None}
        # 获取当前字符
        c = self.text[self.index]
        # 为字母，读取下一个名称
        if c.isalpha():
            return self.next_name()
        # 为数字，读取下一个数值
        if c.isdigit():
            return self.next_value()
        # 为$，读取下一个十六进制值
        if c == '$':
            return self.next_hex()
        # 为"，读取下一个字符串
        elif c in ('"', "'"):
            return self.next_string()
        else:
            # 特殊符号检测
            if self.index + 1 < len(self.text) and self.text[self.index] == '.' and self.text[self.index + 1].isdigit():
                # 开头为小数点，读取数值
                return self.next_value()
            # 单个符号检测
            if c == '{':
                tok = {'token': 'Begin', 'index': self.index, 'text': '{'}
                self.index += 1
                return tok
            elif c == '}':
                tok = {'token': 'End', 'index': self.index, 'text': '{'}
                self.index += 1
                return tok
            elif c == '(':
                tok = {'token': 'Open', 'index': self.index, 'text': '('}
                self.index += 1
                return tok
            elif c == ')':
                tok = {'token': 'Close', 'index': self.index, 'text': ')'}
                self.index += 1
                return tok
            elif c == '[':
                tok = {'token': 'ArrayOpen', 'index': self.index, 'text': '['}
                self.index += 1
                return tok
            elif c == ']':
                tok = {'token': 'ArrayClose', 'index': self.index, 'text': ']'}
                self.index += 1
                return tok
            elif c == ';':
                tok = {'token': 'SepStatement', 'index': self.index, 'text': ';'}
                self.index += 1
                return tok
            elif c == ',':
                tok = {'token': 'SepArgument', 'index': self.index, 'text': ','}
                self.index += 1
                return tok
            elif c == '.':
                tok = {'token': 'Dot', 'index': self.index, 'text': '.'}
                self.index += 1
                return tok
            elif c == '~':
                tok = {'token': 'BitNegate', 'index': self.index, 'text': '~'}
                self.index += 1
                return tok
            # 多重符号检测
            elif c == '!':
                self.index += 1
                if self.index >= len(self.text) or self.text[self.index] != '=':
                    tok = {'token': 'Not', 'index': self.index - 1, 'text': '!'}
                    return tok
                else:
                    tok = {'token': 'NotEqual', 'index': self.index - 2, 'text': '!='}
                    self.index += 1
                    return tok
            elif c == '=':
                self.index += 1
                if self.index >= len(self.text) or self.text[self.index] != '=':
                    tok = {'token': 'Assign', 'index': self.index - 1, 'text': '='}
                    return tok
                else:
                    tok = {'token': 'Equal', 'index': self.index - 2, 'text': '=='}
                    self.index += 1
                    return tok
            elif c == ':':
                self.index += 1
                if self.index >= len(self.text) or self.text[self.index] != '=':
                    tok = {'token': 'Label', 'index': self.index - 1, 'text': ':'}
                    return tok
                else:
                    tok = {'token': 'Assign', 'index': self.index - 2, 'text': ':='}
                    self.index += 1
                    return tok
            elif c == '+':
                self.index += 1
                if self.index >= len(self.text) or self.text[self.index] != '=':
                    tok = {'token': 'Plus', 'index': self.index - 1, 'text': '+'}
                    return tok
                else:
                    tok = {'token': 'AssignPlus', 'index': self.index - 2, 'text': '+='}
                    self.index += 1
                    return tok
            elif c == '-':
                self.index += 1
                if self.index >= len(self.text) or self.text[self.index] != '=':
                    tok = {'token': 'Minus', 'index': self.index - 1, 'text': '-'}
                    return tok
                else:
                    tok = {'token': 'AssignMinus', 'index': self.index - 2, 'text': '-='}
                    self.index += 1
                    return tok
            elif c == '*':
                self.index += 1
                if self.index >= len(self.text) or self.text[self.index] != '=':
                    tok = {'token': 'Time', 'index': self.index - 1, 'text': '*'}
                    return tok
                else:
                    tok = {'token': 'AssignTimes', 'index': self.index - 2, 'text': '*='}
                    self.index += 1
                    return tok
            elif c == '/':
                self.index += 1
                if self.index >= len(self.text) or self.text[self.index] != '=':
                    tok = {'token': 'Divide', 'index': self.index - 1, 'text': '/'}
                    return tok
                else:
                    tok = {'token': 'AssignDivide', 'index': self.index - 2, 'text': '/='}
                    self.index += 1
                    return tok
            elif c == '<':
                if self.index + 1 < len(self.text):
                    if self.text[self.index + 1] == '>':
                        self.index += 2
                        tok = {'token': 'NotEqual', 'index': self.index, 'text': '<>'}
                        return tok
                    elif self.text[self.index + 1] == '<':
                        self.index += 2
                        tok = {'token': 'BitShiftLeft', 'index': self.index, 'text': '<<'}
                        return tok
                    elif self.text[self.index + 1] == '=':
                        self.index += 2
                        tok = {'token': 'LessEqual', 'index': self.index, 'text': '<='}
                        return tok
                    else:
                        tok = {'token': 'Less', 'index': self.index, 'text': '<'}
                        self.index += 1
                        return tok
            elif c == '>':
                if self.index + 1 < len(self.text):
                    if self.text[self.index + 1] == '>':
                        self.index += 2
                        tok = {'token': 'BitShiftRight', 'index': self.index, 'text': '>>'}
                        return tok
                    elif self.text[self.index + 1] == '=':
                        self.index += 2
                        tok = {'token': 'GreaterEqual', 'index': self.index, 'text': '>='}
                        return tok
                    else:
                        tok = {'token': 'Greater', 'index': self.index, 'text': '>'}
                        self.index += 1
                        return tok
            elif c == '|':
                if self.index + 1 < len(self.text):
                    if self.text[self.index + 1] == '|':
                        self.index += 2
                        tok = {'token': 'Or', 'index': self.index, 'text': '||'}
                        return tok
                    elif self.text[self.index + 1] == '=':
                        self.index += 2
                        tok = {'token': 'AssignOr', 'index': self.index, 'text': '|='}
                        return tok
                    else:
                        tok = {'token': 'BitOr', 'index': self.index, 'text': '|'}
                        self.index += 1
                        return tok
            elif c == '&':
                if self.index + 1 < len(self.text):
                    if self.text[self.index + 1] == '&':
                        self.index += 2
                        tok = {'token': 'And', 'index': self.index, 'text': '&&'}
                        return tok
                    elif self.text[self.index + 1] == '=':
                        self.index += 2
                        tok = {'token': 'AssignAnd', 'index': self.index, 'text': '&='}
                        return tok
                    else:
                        tok = {'token': 'BitAnd', 'index': self.index, 'text': '&'}
                        self.index += 1
                        return tok
            elif c == '^':
                if self.index + 1 < len(self.text):
                    if self.text[self.index + 1] == '^':
                        self.index += 2
                        tok = {'token': 'Xor', 'index': self.index, 'text': '^^'}
                        return tok
                    elif self.text[self.index + 1] == '=':
                        self.index += 2
                        tok = {'token': 'AssignXor', 'index': self.index, 'text': '^='}
                        return tok
                    else:
                        tok = {'token': 'BitXor', 'index': self.index, 'text': '^'}
                        self.index += 1
                        return tok

    def next_name(self):
        # 读取下一个名称
        text = ''
        index = self.index
        text += self.text[self.index]
        self.index += 1
        while self.index < len(self.text) and (
                self.text[self.index].isdigit() or self.text[self.index].isalpha() or self.text[self.index] == '_'):
            # 如果当前字符为标识符（字母数字下划线），就加入text
            text += self.text[self.index]
            self.index += 1
        # 关键字检测
        if text == 'var':
            return {'token': 'Var', 'index': index, 'text': text}
        elif text == 'if':
            return {'token': 'If', 'index': index, 'text': text}
        elif text == 'end':
            return {'token': 'End', 'index': index, 'text': text}
        elif text == 'else':
            return {'token': 'Else', 'index': index, 'text': text}
        elif text == 'while':
            return {'token': 'While', 'index': index, 'text': text}
        elif text == 'do':
            return {'token': 'Do', 'index': index, 'text': text}
        elif text == 'for':
            return {'token': 'For', 'index': index, 'text': text}
        elif text == 'begin':
            return {'token': 'Begin', 'index': index, 'text': text}
        elif text == 'then':
            return {'token': 'Then', 'index': index, 'text': text}
        elif text == 'with':
            return {'token': 'With', 'index': index, 'text': text}
        elif text == 'until':
            return {'token': 'Until', 'index': index, 'text': text}
        elif text == 'repeat':
            return {'token': 'Repeat', 'index': index, 'text': text}
        elif text == 'exit':
            return {'token': 'Exit', 'index': index, 'text': text}
        elif text == 'return':
            return {'token': 'Return', 'index': index, 'text': text}
        elif text == 'break':
            return {'token': 'Break', 'index': index, 'text': text}
        elif text == 'continue':
            return {'token': 'Continue', 'index': index, 'text': text}
        elif text == 'switch':
            return {'token': 'Switch', 'index': index, 'text': text}
        elif text == 'case':
            return {'token': 'Case', 'index': index, 'text': text}
        elif text == 'default':
            return {'token': 'Default', 'index': index, 'text': text}
        elif text == 'and':
            return {'token': 'And', 'index': index, 'text': text}
        elif text == 'or':
            return {'token': 'Or', 'index': index, 'text': text}
        elif text == 'not':
            return {'token': 'Not', 'index': index, 'text': text}
        elif text == 'div':
            return {'token': 'Div', 'index': index, 'text': text}
        elif text == 'mod':
            return {'token': 'Mod', 'index': index, 'text': text}
        elif text == 'xor':
            return {'token': 'BitXor', 'index': index, 'text': text}
        elif text == 'globalvar':
            return {'token': 'GlobalVar', 'index': index, 'text': text}
        else:
            return {'token': 'Name', 'index': index, 'text': text}

    def next_value(self):
        # 读取下一个数值
        text = ''
        index = self.index
        text += self.text[self.index]
        self.index += 1
        while self.index < len(self.text) and (self.text[self.index].isdigit() or self.text[self.index] == '.'):
            # 如果当前字符为数字或小数点，就加入text
            text += self.text[self.index]
            self.index += 1
        return {'token': 'Number', 'index': index, 'text': text}

    def next_hex(self):
        # 读取下一个十六进制值
        text = ''
        index = self.index
        text += self.text[self.index]
        self.index += 1
        while self.index < len(self.text) and (self.text[self.index].isdigit() or (
                ord(self.text[self.index].lower()) >= ord('a') and ord(self.text[self.index]) <= ord('f'))):
            # 如果当前字符是a~f，就加入text
            text += self.text[self.index]
            self.index += 1
        return {'token': 'Number', 'index': index, 'text': text}

    def next_string(self):
        # 读取下一个字符串
        text = ''
        index = self.index
        c = self.text[self.index]
        self.index += 1
        while self.index < len(self.text) and c != self.text[self.index]:
            # 如果当前字符不是'，就加入text
            text += self.text[self.index]
            self.index += 1
        if self.index < len(self.text):
            self.index += 1
        return {'token': 'String', 'index': index, 'text': text}
