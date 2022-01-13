import sys

class Parse():
    def __init__(self):
        self.symbol_table = {
            "SP":0, "LCL":1, "ARG":2, "THIS":3, "THAT":4, "SCREEN":16384, "KBD":24576, 
            "M":"001", "D":"010", "MD":"011", "A":"100", "AM":"101", "AD":"110", "AMD":"111",
            "JGT":"001", "JEQ":"010", "JGE":"011", "JLT":"100", "JNE":"101", "JLE":"110", "JMP":"111"
        }
        
        self.comp_table = {
            "0":"0101010", "1":"0111111", "-1":"0111010", "D":"0001100", "A":"0110000", "!D":"0001101",
            "!A":"0110001", "-D":"0001111", "-A":"0110011", "D+1":"0011111", "A+1":"0110111", "D-1":"0001110",
            "A-1":"0110010", "D+A":"0000010", "D-A":"0010011", "A-D":"0000111", "D&A":"0000000", "D|A":"0010101",
            "M":"1110000", "!M":"1110001", "-M":"1110011", "M+1":"1110111", "M-1":"1110010", "D+M":"1000010",
            "D-M":"1010011", "M-D":"1000111", "D&M":"1000000", "D|M":"1010101"
        }

        for i in range(16):
            self.symbol_table["R" + str(i)] = i
        
        self.lineNum = 0
        self.variableCount = 16
    
    def advance(self):
        self.lineNum += 1
    
    # def clean(self, line):
    #     line = line.strip()

    #     if len(line) == 0 or line[0] == "/":
    #         return ""


    #     return line.strip()

    def parse(self, command):
        command = command.strip()

        if len(command) == 0 or command[0] == "/":
            return ""
        if "//" in command:
            command = command[:command.find("//")].strip()
        
        line = command

        if command[0] == "@":
            address = command[1:]
            if address.isdigit():
                command = dec_to_bin_16bit(int(address))
            elif address in self.symbol_table:
                command = dec_to_bin_16bit(self.symbol_table.get(address))
            else:
                self.symbol_table[address] = self.lineNum
                command = dec_to_bin_16bit(self.lineNum)

            self.advance()

        elif command[0] == "(":
            label = command[1:-1]
            if label not in self.symbol_table:
                self.symbol_table[label] = self.lineNum

        else:
            dest = "000"
            if "=" in command:
                dest = command[0:command.find("=")]
                dest = self.symbol_table.get(dest)
                command = command[command.find("=")+1:]

            jump = "000"
            
            if ";" in command:
                jump = command[command.find(";")+1:]
                jump = self.symbol_table.get(jump)
                command = command[:command.find(";")]
            
            comp = ""

            comp = self.comp_table.get(command)
            
            command = "111" + comp + dest + jump

            self.advance()

        return command


        # if result[0] == "@":
        #     result = dec_to_bin_16bit(int(result[1:])) + "\n"
        #     self.advance()
        # elif result[0] == "(":
        #     if result[1:-1] not in self.symbol_table:
        #         self.symbol_table[result[1:-1]] = self.n
        # else:
        #     result += "\n"
        #     self.advance()

        # return result
    



def main():
    out = []

    parse = Parse()

    #read input file
    with open(sys.argv[1], "r") as fh:
        lines = fh.readlines()
        for line in lines:
            line = parse.parse(line)
            if (len(line) > 0):
                out.append(line + "\n")

    #write results to ouput file
    output_filename = sys.argv[1][:-4]
    output_filename += ".hack"

    with open(output_filename, "w") as fh:
        fh.writelines(out)

def dec_to_bin_16bit(dec):
    result = bin(dec)[2:]
    padding = 16 - len(result)
    result = "0" * padding + result
    return result

if __name__ == "__main__":
    main()