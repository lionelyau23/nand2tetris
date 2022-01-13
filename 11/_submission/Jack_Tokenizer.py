import re
from enum import Enum, auto

class Type_of_token(Enum):
    KEYWORD = auto()
    SYMBOL = auto()
    IDENTIFIER = auto()
    INT_CONST = auto()
    STRING_CONST = auto()

    def __str__(self) -> str:
        if self in {self.KEYWORD, self.SYMBOL, self.IDENTIFIER}:
            return str(self.name).lower()
        elif self is self.INT_CONST:
            return "integerConstant"
        else:
            return "stringConstant"

class Jack_Tokienizer:

    filename: str
    tokens = []
    i: int = 0
    current_token: str = ""
    symbol_table = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"}
    keyword_table = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}

    def __init__(self, filename: str) -> None:
        self.filename = filename

        # regex magic
        with open(filename, "r") as fh:
            # handles // and  /* */ comments, removes newline
            lines = re.sub("//.*?\n|/\*[\s\S]*?\*/|\n", "", fh.read())

            # use single whitespace and symbols as delimiter to create the list
            # also does non-greedy search for string constant inside double quotes as delimiter
            lines = re.split(r'\s|({|}|\(|\)|\[|\]|\.|\,|;|\+|\-|=|\*|/|&|\||<|>|~|".*?")', lines)

        # filter out the empty items (i.e. whitespaces) in the list
        self.tokens = list(filter(None, lines))

    def has_more_tokens(self) -> bool:
        return self.i < len(self.tokens)

    def advance(self) -> None:
        if self.has_more_tokens():
            self.i += 1
            self.current_token = self.tokens[self.i - 1]

    def token_type(self) -> str:
        token = self.tokens[self.i-1]
        if token in self.keyword_table:
            return Type_of_token.KEYWORD
        elif token in self.symbol_table:
            return Type_of_token.SYMBOL
        elif token.isdecimal():
            return Type_of_token.INT_CONST
        elif token[0] == "\"":
            return Type_of_token.STRING_CONST
        else:
            return Type_of_token.IDENTIFIER

    def key_word(self) -> str:
        if self.token_type() == Type_of_token.KEYWORD:
            return self.current_token

    def symbol(self) -> str:
        if self.token_type() == Type_of_token.SYMBOL:
            token = self.current_token
            if token == "<":
                return "&lt;"
            elif token == ">":
                return "&gt;"
            elif token == "\"":
                return "&quot;"
            elif token == "&":
                return "&amp;"
            else:
                return self.current_token

    def identifier(self) -> str:
        if self.token_type() == Type_of_token.IDENTIFIER:
            return self.current_token

    def int_val(self) -> str:
        if self.token_type() == Type_of_token.INT_CONST:
            return self.current_token

    def string_val(self) -> str:
        if self.token_type() == Type_of_token.STRING_CONST:
            return self.current_token[1:-1]
    
    def peek(self, i) -> str:
        if self.i + i < len(self.tokens):
            return self.tokens[self.i + i - 1]

    # debug for printing the T.xml file to show tokens only
    def debug_write(self) -> None:
        with open(str(self.filename[:-5] + "T.xml"), "w") as fh:
            fh.write("<tokens>\n")
            while self.has_more_tokens():
                self.advance()
                if self.token_type() in {Type_of_token.KEYWORD, Type_of_token.IDENTIFIER, Type_of_token.INT_CONST}:
                    token = self.current_token
                elif self.token_type() == Type_of_token.SYMBOL:
                    token = self.symbol()
                else:
                    token = self.string_val()

                fh.write(f"<{self.token_type()}> {token} </{self.token_type()}>\n")

            fh.write("</tokens>\n")
        
        self.i = 0
