class Token:
    def __init__(self, token=None, index=None, text=None, value=None, children=None):
        self.token = token
        self.index = index
        self.text = text
        self.value = value
        if children is None:
            self.children = []
        else:
            self.children = children
