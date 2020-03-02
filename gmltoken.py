class Token:
    """对GML源代码字符组合的一种表示形式
    Token可以是一个关键字（if，else，for...）、一个名称（apple，orange，watermelon）、
    一个数值（123.456，$12d591，"hello world"）、一个操作符（=，!=，&&）
    每个Token都具有一个字符串token属性，作为Token的类型表示
    如：if -> "If"，>= -> "GreaterEqual"
    """

    def __init__(self, token=None, index=None, text=None, value=None, children=None):
        self.token = token
        self.index = index
        self.text = text
        self.value = value
        if children is None:
            self.children = []
        else:
            self.children = children
