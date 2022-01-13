import re

class Jack_Tokienizer():
    def __init__(self, filename):
        self.filename = filename
        self.tokens = []
        self.i = 0
        self.current_token = ""

        self.symbol_table = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"}
        self.keyword_table = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}

        # regex magic
        with open(filename, "r") as fh:
            # handles // and  /* */ comments, removes newline
            lines = re.sub("//.*?\n|/\*[\s\S]*?\*/|\n", "", fh.read())

            # use single whitespace and symbols as delimiter to create the list
            # also does non-greedy search for string constant inside double quotes
            lines = re.split(r'\s|({|}|\(|\)|\[|\]|\.|\,|;|\+|=|\*|/|&|\||<|>|~|".*?")', lines)

        # filter out the empty items (i.e. whitespaces) in the list
        self.tokens = list(filter(None, lines))

    def has_more_tokens(self):
        return self.i < len(self.tokens)

    def advance(self):
        if self.has_more_tokens():
            self.i += 1
            self.current_token = self.tokens[self.i - 1]

    def token_type(self):
        token = self.tokens[self.i-1]
        if token in self.keyword_table:
            return "KEYWORD"
        elif token in self.symbol_table:
            return "SYMBOL"
        elif token.isdecimal():
            return "INT_CONST"
        elif token[0] == "\"":
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def key_word(self):
        if self.token_type() == "KEYWORD":
            return self.tokens[self.i - 1]

    def symbol(self):
        if self.token_type() == "SYMBOL":
            token = self.tokens[self.i - 1]
            if token == "<":
                return "&lt;"
            elif token == ">":
                return "&gt;"
            elif token == "\"":
                return "&quot;"
            elif token == "&":
                return "&amp;"
            else:
                return self.tokens[self.i - 1]

    def identifier(self):
        if self.token_type() == "IDENTIFIER":
            return self.tokens[self.i - 1]

    def int_val(self):
        if self.token_type() == "INT_CONST":
            return self.tokens[self.i - 1]

    def string_val(self):
        if self.token_type() == "STRING_CONST":
            return self.tokens[self.i - 1].replace("\n", "")[1:-1]
    
    def peek(self, i):
        if self.i + i < len(self.tokens):
            return self.tokens[self.i + i - 1]

    # debug for printing the T.xml file to show tokens only
    def debug_write(self):
        with open(str(self.filename[:-5] + "T.xml"), "w") as fh:
            fh.write("<tokens>\n")
            while self.has_more_tokens():
                self.advance()
                if self.token_type() in {"KEYWORD", "IDENTIFIER"}:
                    tag = self.token_type().lower()
                    token = self.current_token
                elif self.token_type() == "SYMBOL":
                    tag = self.token_type().lower()
                    token = self.symbol()
                elif self.token_type() == "INT_CONST":
                    tag = "integerConstant"
                    token = self.int_val()
                else:
                    tag = "stringConstant"
                    token = self.string_val()

                fh.write("<" + tag + "> " + token + " </" + tag + ">\n")

            fh.write("</tokens>\n")
        
        self.i = 0
