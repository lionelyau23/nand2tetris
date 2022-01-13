class Compliation_Engine():
    def __init__(self, fh, tokenizer):
        self.fh = fh
        self.tokenizer = tokenizer
        self.indent = 1
        self.tokenizer.advance()

    # class className { classVarDec* subroutineDec* }
    def compile_class(self):
        self.fh.write("<class>\n")
        self.parse_keyword()
        self.parse_identifier()
        self.parse_symbol()

        self.compile_class_var_dec()
        self.compile_subroutine_dec()

        self.parse_symbol()
        self.fh.write("</class>\n")

    # (static|field) type varName (, varName)* ;
    def compile_class_var_dec(self):
        while self.tokenizer.key_word() in {"static", "field"}:
            self.open_tag("classVarDec")

            self.parse_keyword()
            self.parse()
            self.parse_identifier()

            while self.tokenizer.symbol() == ",":
                self.parse_symbol()
                self.parse_identifier()

            self.parse_symbol()

            self.close_tag("classVarDec")

    # (constructor|function|method) (void|type) subroutineName ( parameterList ) subroutineBody
    def compile_subroutine_dec(self):
        while self.tokenizer.key_word() in {"constructor", "function", "method"}:
            self.open_tag("subroutineDec")

            self.parse_keyword()
            self.parse()
            self.parse_identifier()

            self.parse_symbol()
            self.compile_parameter_list()
            self.parse_symbol()

            self.compile_subroutine_body()

            self.close_tag("subroutineDec")

    # ((type varName) (, type varName)*)?
    def compile_parameter_list(self):
        self.open_tag("parameterList")

        if self.tokenizer.token_type() in {"KEYWORD", "IDENTIFIER"}:
            self.parse()
            self.parse_identifier()
            while self.tokenizer.symbol() == ",":
                self.parse_symbol()
                self.parse()
                self.parse_identifier()

        self.close_tag("parameterList")

    # { varDec* statements }
    def compile_subroutine_body(self):
        self.open_tag("subroutineBody")

        self.parse_symbol()
        self.compile_var_dec()
        self.compile_stataments()
        self.parse_symbol()

        self.close_tag("subroutineBody")

    # var type varName (, varName)* ;
    def compile_var_dec(self):
        while self.tokenizer.key_word() == "var":
            self.open_tag("varDec")

            self.parse_keyword()
            self.parse()
            self.parse_identifier()

            while self.tokenizer.symbol() == ",":
                self.parse_symbol()
                self.parse_identifier()

            self.parse_symbol()

            self.close_tag("varDec")

    # statement*
    def compile_stataments(self):
        self.open_tag("statements")
        while self.tokenizer.key_word() in {"let", "if", "while", "do", "return"}:
            temp = self.tokenizer.key_word()
            if temp == "let":
                self.compile_let()
            elif temp == "if":
                self.compile_if()
            elif temp == "while":
                self.compile_while()
            elif temp == "do":
                self.compile_do()
            else:
                self.compile_return()

        self.close_tag("statements")

    # let varName ( [ expression ] )? = expression ;
    def compile_let(self):
        self.open_tag("letStatement")      

        self.parse_keyword()
        self.parse_identifier()

        if self.tokenizer.symbol() == "[":
            self.parse_symbol()
            self.compile_expression()
            self.parse_symbol()
        
        self.parse_symbol()
        self.compile_expression()
        self.parse_symbol()

        self.close_tag("letStatement")      

    # if ( expression ) { statements } (else { statements } )?
    def compile_if(self):
        self.open_tag("ifStatement")      
        
        self.parse_keyword()

        self.parse_symbol()
        self.compile_expression()
        self.parse_symbol()

        self.parse_symbol()
        self.compile_stataments()
        self.parse_symbol()

        if self.tokenizer.key_word() == "else":
            self.parse_keyword()
            self.parse_symbol()
            self.compile_stataments()
            self.parse_symbol()

        self.close_tag("ifStatement")      

    # while ( expression ) { statements }
    def compile_while(self):
        self.open_tag("whileStatement")      
        
        self.parse_keyword()
        self.parse_symbol()
        self.compile_expression()
        self.parse_symbol()

        self.parse_symbol()
        self.compile_stataments()
        self.parse_symbol()

        self.close_tag("whileStatement")      

    # do subroutineCall ;
    def compile_do(self):
        self.open_tag("doStatement")      
        
        self.parse_keyword()

        # subroutineCall
        self.compile_subroutine_call()

        self.parse_symbol()

        self.close_tag("doStatement")
         
    # subroutineCall
    # subroutineName ( expressionList ) |
    # (className|varName) . subroutineName ( expressionList )
    def compile_subroutine_call(self):
        self.parse_identifier()

        if self.tokenizer.symbol() == ".":
            self.parse_symbol()
            self.parse_identifier()

        self.parse_symbol()
        self.compile_expression_list()
        self.parse_symbol()


    # return expression? ;
    def compile_return(self):
        self.open_tag("returnStatement")      
        
        self.parse_keyword()

        if self.tokenizer.symbol() != ";":
            self.compile_expression()
        
        self.parse_symbol()

        self.close_tag("returnStatement")

    # term (op term)*
    def compile_expression(self):
        self.open_tag("expression")              

        self.compile_term()

        while self.is_op(self.tokenizer.symbol()):
            self.parse_symbol()
            self.compile_term()

        self.close_tag("expression")

    # integerConstant|stringConstant|keywordConstant|varName|
    # varName [ expression ]|subroutineCall| ( expression )|
    # unaryOp term
    def compile_term(self):
        self.open_tag("term")              

        # integerConstant|stringConstant
        if self.tokenizer.token_type() in {"INT_CONST", "STRING_CONST"}:
            self.parse()
        # keywordConstant
        elif self.tokenizer.key_word() in {"true", "false", "null", "this"}:
            self.parse_keyword()
        # ( expression )
        elif self.tokenizer.symbol() == "(":
            self.parse_symbol()
            self.compile_expression()
            self.parse_symbol()
        # unaryOp term
        elif self.is_unaryOp(self.tokenizer.symbol()):
            self.parse_symbol()
            self.compile_term()
        else:
            # subroutineCall
            if self.tokenizer.peek(1) in {"(", "."}:
                self.compile_subroutine_call()
            else:
                # varName
                self.parse_identifier()

                # varName [ expression ]
                if self.tokenizer.symbol() == "[":
                    self.parse_symbol()
                    self.compile_expression()
                    self.parse_symbol()

        self.close_tag("term")

    # (expression ( , expression))?
    def compile_expression_list(self):
        self.open_tag("expressionList")

        if self.tokenizer.symbol() != ")":
            self.compile_expression()
            while self.tokenizer.symbol() == ",":
                self.parse_symbol()
                self.compile_expression()

        self.close_tag("expressionList")
    
    # parse the token from tokenizer into desired format
    def parse(self):
        if self.tokenizer.token_type() == "KEYWORD":
            self.parse_keyword()
        elif self.tokenizer.token_type() == "SYMBOL":
            self.parse_symbol()
        elif self.tokenizer.token_type() == "INT_CONST":
            self.parse_int_val()
        elif self.tokenizer.token_type() == "STRING_CONST":
            self.parse_string_val()
        else:
            self.parse_identifier()

    def parse_keyword(self):
        if self.tokenizer.token_type() != "KEYWORD":
            print("expected keyword")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write("<keyword> ")
            self.fh.write(self.tokenizer.key_word())
            self.fh.write(" </keyword>\n")
            self.tokenizer.advance()
        
    def parse_symbol(self):
        if self.tokenizer.token_type() != "SYMBOL":
            print("expected symbol")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write("<symbol> ")
            self.fh.write(self.tokenizer.symbol())
            self.fh.write(" </symbol>\n")
            self.tokenizer.advance()

    def parse_identifier(self):
        if self.tokenizer.token_type() != "IDENTIFIER":
            print("expected identifier")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write("<identifier> ")
            self.fh.write(self.tokenizer.identifier())
            self.fh.write(" </identifier>\n")
            self.tokenizer.advance()

    def parse_int_val(self):
        if self.tokenizer.token_type() != "INT_CONST":
            print("expected integer")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write("<integerConstant> ")
            self.fh.write(self.tokenizer.int_val())
            self.fh.write(" </integerConstant>\n")
            self.tokenizer.advance()

    def parse_string_val(self):
        if self.tokenizer.token_type() != "STRING_CONST":
            print("expected string")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write("<stringConstant> ")
            self.fh.write(self.tokenizer.string_val())
            self.fh.write(" </stringConstant>\n")
            self.tokenizer.advance()
    
    # for printing the open and closing tage for structures
    def open_tag(self, tag):
        self.fh.write("  " * self.indent)
        self.fh.write("<" + tag + ">\n")
        self.indent += 1

    def close_tag(self, tag):
        self.indent -= 1
        self.fh.write("  " * self.indent)
        self.fh.write("</" + tag + ">\n")

    def is_op(self, token):
        return token in { "+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="}

    def is_unaryOp(self, token):
        return token in {"-", "~"}

    # debug use only, skip token until reach symbols
    def debug_skip_symbol(self, symbol):
        while self.tokenizer.symbol() != symbol:
            self.tokenizer.advance()