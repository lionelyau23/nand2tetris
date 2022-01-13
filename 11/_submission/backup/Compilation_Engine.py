from typing import TextIO
from Jack_Tokenizer import Jack_Tokienizer, Type_of_token
from Symbol_Table import Symbol_Table, Variable_Kind
from VM_Writer import VM_Writer, Segment_Type, Command_Type

class Compliation_Engine:
    fh: TextIO
    tokenizer: Jack_Tokienizer
    indent: int
    symbol_table: Symbol_Table
    vm_writer: VM_Writer
    class_name: str
    label_i: int

    def __init__(self, filename: str, tokenizer: Jack_Tokienizer) -> None: 
        self.fh = open(f"{filename[:-5]}.xml", "w")
        self.tokenizer = tokenizer
        self.tokenizer.advance()
        self.symbol_table = Symbol_Table()
        self.vm_writer = VM_Writer(filename)

        self.indent = 0
        self.label_i = 0

    # class className { classVarDec* subroutineDec* }
    def compile_class(self):
        self.open_tag("class")
        self.parse_keyword()

        self.class_name = self.tokenizer.identifier()
        self.parse_identifier()

        self.parse_symbol()

        self.compile_class_var_dec()
        self.compile_subroutine_dec()

        self.parse_symbol()
        self.close_tag("class")
        self.vm_writer.close()
        print(self.symbol_table.class_table)

    # (static|field) type varName (, varName)* ;
    def compile_class_var_dec(self):
        while self.tokenizer.key_word() in {"static", "field"}:
            kind = self.get_kind(self.tokenizer.key_word())
            self.open_tag("classVarDec")

            self.parse_keyword()
            type = self.tokenizer.current_token
            self.parse()
            name = self.tokenizer.identifier()
            self.parse_identifier()
            self.symbol_table.define(name, type, kind)
            # print(self.symbol_table.class_table)

            while self.tokenizer.symbol() == ",":
                self.parse_symbol()
                name = self.tokenizer.identifier()
                self.parse_identifier()
                self.symbol_table.define(name, type, kind)
                # print(self.symbol_table.class_table)

            self.parse_symbol()

            self.close_tag("classVarDec")

    # (constructor|function|method) (void|type) subroutineName ( parameterList ) subroutineBody
    def compile_subroutine_dec(self):
        while self.tokenizer.key_word() in {"constructor", "function", "method"}:
            self.symbol_table.start_subroutine()
            if self.tokenizer.key_word() == "method":
                self.symbol_table.define("this", self.class_name, Variable_Kind.ARG)

            self.open_tag("subroutineDec")

            self.parse_keyword()
            self.parse()
            self.parse_identifier()

            self.parse_symbol()
            self.compile_parameter_list()
            self.parse_symbol()

            self.compile_subroutine_body()

            self.close_tag("subroutineDec")
            print(self.symbol_table.subroutine_table)

    # ((type varName) (, type varName)*)?
    def compile_parameter_list(self):
        self.open_tag("parameterList")

        if self.tokenizer.token_type() in {Type_of_token.KEYWORD, Type_of_token.IDENTIFIER}:
            kind = self.get_kind("arg")
            type = self.tokenizer.current_token
            self.parse()
            name = self.tokenizer.identifier()
            self.parse_identifier()
            self.symbol_table.define(name, type, kind)

            while self.tokenizer.symbol() == ",":
                self.parse_symbol()
                type = self.tokenizer.current_token
                self.parse()
                name = self.tokenizer.identifier()
                self.parse_identifier()
                self.symbol_table.define(name, type, kind)


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

            kind = self.get_kind(self.tokenizer.key_word())
            self.parse_keyword()
            type = self.tokenizer.current_token
            self.parse()
            name = self.tokenizer.identifier()
            self.parse_identifier()
            self.symbol_table.define(name, type, kind)

            while self.tokenizer.symbol() == ",":
                self.parse_symbol()
                name = self.tokenizer.identifier()
                self.parse_identifier()
                self.symbol_table.define(name, type, kind)

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

        self.label_i += 1
        label = self.label_i
        self.vm_writer.write_arithmetic(Command_Type.NOT)
        self.vm_writer.write_if(f"L{label}")

        self.parse_symbol()
        self.compile_stataments()
        self.parse_symbol()

        if self.tokenizer.key_word() == "else":
            self.parse_keyword()

            self.label_i += 1
            label_e = self.label_i
            self.vm_writer.write_goto(f"L{label_e}")
            self.vm_writer.write_label(f"L{label}")

            self.parse_symbol()
            self.compile_stataments()
            self.parse_symbol()

            self.vm_writer.write_label(f"L{label_e}")
        else:
            self.vm_writer.write_label(f"L{label}")
        

        self.close_tag("ifStatement")      

    # while ( expression ) { statements }
    def compile_while(self):
        self.open_tag("whileStatement")

        self.label_i += 1
        label = self.label_i
        self.vm_writer.write_label(f"L{label}")

        self.parse_keyword()
        self.parse_symbol()
        self.compile_expression()
        self.parse_symbol()

        self.label_i += 1
        label_e = self.label_i
        self.vm_writer.write_arithmetic(Command_Type.NOT)
        self.vm_writer.write_if(f"L{label_e}")

        self.parse_symbol()
        self.compile_stataments()
        self.parse_symbol()

        self.vm_writer.write_goto(f"L{label}")
        self.vm_writer.write_label(f"L{label_e}")

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
            operation = self.tokenizer.symbol()
            self.parse_symbol()
            self.compile_term()
            self.vm_writer.write_arithmetic(self.get_operation(operation))

        self.close_tag("expression")

    # integerConstant|stringConstant|keywordConstant|varName|
    # varName [ expression ]|subroutineCall| ( expression )|
    # unaryOp term
    def compile_term(self):
        self.open_tag("term")              

        # integerConstant
        if self.tokenizer.token_type() is Type_of_token.INT_CONST:
            self.vm_writer.write_push(Segment_Type.CONST, int(self.tokenizer.current_token))
            self.parse_int_val()
        # stringConstant
        elif self.tokenizer.token_type() is Type_of_token.STRING_CONST:
            string = self.tokenizer.string_val()
            self.vm_writer.write_push(Segment_Type.CONST, len(string))
            self.vm_writer.write_call("String.new", 1)
            for c in string:
                self.vm_writer.write_push(Segment_Type.CONST, ord(c))
                self.vm_writer.write_call("String.appendChar", 2)
            self.parse_string_val()
        # keywordConstant
        elif self.tokenizer.key_word() in {"true", "false", "null", "this"}:
            value = self.tokenizer.key_word()
            if value == "true":
                self.vm_writer.write_push(Segment_Type.CONST, 1)
                self.vm_writer.write_arithmetic(Command_Type.NEG)
            elif value in {"false", "null"}:
                self.vm_writer.write_push(Segment_Type.CONST, 0)
            else:
                self.vm_writer.write_push(Segment_Type.POINTER, 0)
            self.parse_keyword()
        # ( expression )
        elif self.tokenizer.symbol() == "(":
            self.parse_symbol()
            self.compile_expression()
            self.parse_symbol()
        # unaryOp term
        elif self.is_unaryOp(self.tokenizer.symbol()):
            operation = self.tokenizer.symbol()
            self.parse_symbol()
            self.compile_term()
            self.vm_writer.write_arithmetic(self.get_unaryOp(operation))
        else:
            # subroutineCall
            if self.tokenizer.peek(1) in {"(", "."}:
                self.compile_subroutine_call()
            else:
                # varName
                # identifier = self.tokenizer.identifier()
                # self.vm_writer.write_push(self.get_segment(identifier), self.symbol_table.index_of(identifier))
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
        if self.tokenizer.token_type() == Type_of_token.KEYWORD:
            self.parse_keyword()
        elif self.tokenizer.token_type() == Type_of_token.SYMBOL:
            self.parse_symbol()
        elif self.tokenizer.token_type() == Type_of_token.INT_CONST:
            self.parse_int_val()
        elif self.tokenizer.token_type() == Type_of_token.STRING_CONST:
            self.parse_string_val()
        else:
            self.parse_identifier()

    def parse_keyword(self):
        if self.tokenizer.token_type() != Type_of_token.KEYWORD:
            print("expected keyword")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write(f"<keyword> {self.tokenizer.key_word()} </keyword>\n")
            self.tokenizer.advance()
        
    def parse_symbol(self):
        if self.tokenizer.token_type() != Type_of_token.SYMBOL:
            print("expected symbol")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write("<symbol> ")
            self.fh.write(self.tokenizer.symbol())
            self.fh.write(" </symbol>\n")
            self.tokenizer.advance()

    def parse_identifier(self):
        if self.tokenizer.token_type() != Type_of_token.IDENTIFIER:
            print("expected identifier")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()

    def parse_int_val(self):
        if self.tokenizer.token_type() != Type_of_token.INT_CONST:
            print("expected integer")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write("<integerConstant> ")
            self.fh.write(self.tokenizer.int_val())
            self.fh.write(" </integerConstant>\n")
            self.tokenizer.advance()

    def parse_string_val(self):
        if self.tokenizer.token_type() != Type_of_token.STRING_CONST:
            print("expected string")
            exit()
        else:
            self.fh.write("  " * self.indent)
            self.fh.write("<stringConstant> ")
            self.fh.write(self.tokenizer.string_val())
            self.fh.write(" </stringConstant>\n")
            self.tokenizer.advance()

    def close(self):
        self.fh.close()

    # for printing the open and closing tage for structures
    def open_tag(self, tag):
        indent = "  " * self.indent
        self.fh.write(f"{indent}<{tag}>\n")
        self.indent += 1

    def close_tag(self, tag):
        self.indent -= 1
        indent = "  " * self.indent
        self.fh.write(f"{indent}</{tag}>\n")

    def is_op(self, token):
        return token in { "+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="}

    def is_unaryOp(self, token):
        return token in {"-", "~"}

    def get_kind(self, kind: str) -> Variable_Kind:
        return{
            "static": Variable_Kind.STATIC,
            "field": Variable_Kind.FIELD,
            "var": Variable_Kind.VAR,
            "arg": Variable_Kind.ARG
        }[kind]
        # if kind == "static":
        #     return Variable_Kind.STATIC
        # elif kind == "field":
        #     return Variable_Kind.FIELD
        # elif kind == "var":
        #     return Variable_Kind.VAR
        # else:
        #     return Variable_Kind.ARG
    
    def get_segment(self, identifier: str) -> Segment_Type:
        return{

        }[identifier]

    def get_operation(self, operation: str) -> Command_Type:
        return{
            "+": Command_Type.ADD,
            "-": Command_Type.SUB,
            "*": Command_Type.MULT,
            "/": Command_Type.DIV,
            "&amp;": Command_Type.AND,
            "|": Command_Type.OR,
            "&lt;": Command_Type.LT,
            "&gt;": Command_Type.GT,
            "=" : Command_Type.EQ
        }[operation]
    
    def get_unaryOp(self, operation: str) -> Command_Type:
        return{
            "-": Command_Type.NEG,
            "~": Command_Type.NOT
        }[operation]

    # debug use only, skip token until reach symbols
    def debug_skip_symbol(self, symbol):
        while self.tokenizer.symbol() != symbol:
            self.tokenizer.advance()