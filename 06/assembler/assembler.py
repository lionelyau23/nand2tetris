import sys

class Parser:
    def __init__(self, filename):
        self.lines = []

        #add lines from file into lines list
        with open(filename, "r") as file:
            for line in file:
                #clean unrelated content before append
                line = line.strip()
                if len(line) > 0 and line[0] != "/":
                    if "//" in line:
                        line = line[:line.find("//")].strip()
                    self.lines.append(line)
        
        self.i = 0
        self.current_command = ""    

    def has_more_commands(self):
        return self.i < len(self.lines)

    def advance(self):
        if self.has_more_commands():
            self.current_command = self.lines[self.i]
            self.i += 1


    def command_type(self):
        if self.i == 0:
            return ""
        elif self.current_command[0] == "@":
            return "A"
        elif self.current_command[0] == "(":
            return "L"
        else:
            return "C"

    def symbol(self):
        if self.command_type() == "A":
            return self.current_command[1:]
        elif self.command_type() == "L":
            return self.current_command[1:-1]
        else:
            return ""

    def dest(self):
        if self.command_type() != "C":
            return ""
        else:
            if "=" in self.current_command:
                return self.current_command[:self.current_command.find("=")]
            else:
                return ""

    def comp(self):
        if self.command_type() != "C":
            return ""
        else:
            temp = self.current_command
            if "=" in temp:
                temp = temp[temp.find("=")+1:]
            
            if ";" in temp:
                temp = temp[:temp.find(";")]
            
            return temp

    def jump(self):
        if self.command_type() != "C":
            return ""
        else:
            if ";" in self.current_command:
                return self.current_command[self.current_command.find(";")+1:]
            else:
                return ""
    
    def reset(self):
        self.i = 0

class Code:
    def __init__(self):
        self.dest_table = {
            "M":"001", "D":"010", "MD":"011", "A":"100", "AM":"101", "AD":"110", "AMD":"111", "":"000"
        }

        self.jump_table = {
            "JGT":"001", "JEQ":"010", "JGE":"011", "JLT":"100", "JNE":"101", "JLE":"110", "JMP":"111", "":"000"
        }

        self.comp_table = {
            "0":"0101010", "1":"0111111", "-1":"0111010", "D":"0001100", "A":"0110000", "!D":"0001101",
            "!A":"0110001", "-D":"0001111", "-A":"0110011", "D+1":"0011111", "A+1":"0110111", "D-1":"0001110",
            "A-1":"0110010", "D+A":"0000010", "D-A":"0010011", "A-D":"0000111", "D&A":"0000000", "D|A":"0010101",
            "M":"1110000", "!M":"1110001", "-M":"1110011", "M+1":"1110111", "M-1":"1110010", "D+M":"1000010",
            "D-M":"1010011", "M-D":"1000111", "D&M":"1000000", "D|M":"1010101"
        }

    def dest(self, input):
        if len(input) == 0:
            return "000"
        return self.dest_table[input]

    def comp(self, input):
        return self.comp_table[input]

    def jump(self, input):
        if len(input) == 0:
            return "000"
        return self.jump_table[input]

class Symbol_Table:
    def __init__(self):
        self.table = {
            "SP":0, "LCL":1, "ARG":2, "THIS":3, "THAT":4, "SCREEN":16384, "KBD":24576
        }

        for i in range(16):
            self.table["R" + str(i)] = i
        
        self.variable_add = 16

    #add free variable
    def add_variable(self, symbol):
        self.add_entry(symbol, self.variable_add)
        self.variable_add += 1
    
    def add_entry(self, symbol, address):
        self.table[symbol] = address

    def contains(self, symbol):
        return symbol in self.table

    def get_address(self, symbol):
        return self.table[symbol]

def main():
    out = []

    #read input file
    parser = Parser(sys.argv[1])
    code = Code()
    symbol_table = Symbol_Table()

    #1st pass for building symbol table
    line_i = 0
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "L":
            #add labels into symbol table
            symbol_table.add_entry(parser.symbol(), line_i)
        else:
            line_i += 1

    parser.reset()


    #2nd pass for translation
    while parser.has_more_commands():
        parser.advance()
        output = ""

        #parse A command
        if parser.command_type() == "A":
            #if address has no symbol
            if parser.symbol().isdigit():
                address = str(bin(int(parser.symbol()))[2:])
                output = "0" * (16 - len(address)) + address
            else:
                #if address symbol not in symbol table
                if not symbol_table.contains(parser.symbol()):
                    symbol_table.add_variable(parser.symbol())

                #find address from symbol table
                address = str(bin(symbol_table.get_address(parser.symbol()))[2:])
                output = "0" * (16 - len(address)) + address

        #parse C command
        elif parser.command_type() == "C":
            output = "111" + code.comp(parser.comp()) + code.dest(parser.dest()) + code.jump(parser.jump())

        #output into output list if not labels
        if parser.command_type() != "L":
            out.append(output + "\n")

    #write results to ouput file
    output_filename = sys.argv[1][:-4]
    output_filename += ".hack"

    with open(output_filename, "w") as fh:
        fh.writelines(out)

if __name__ == "__main__":
    main()