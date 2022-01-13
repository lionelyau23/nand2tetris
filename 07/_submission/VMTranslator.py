import sys

class Parser():
    def __init__(self, filename):
        self.lines = []

        with open(filename, "r") as fh:
            for line in fh:
                line = line.strip()
                if len(line) > 0 and line[0] != "/":
                    if "/" in line:
                        line = line[:line.find("/")].strip()
                    self.lines.append(line)

        self.i = 0

    def has_more_commands(self):
        return self.i < len(self.lines)

    def advance(self):
        if self.has_more_commands():
            self.i += 1

    def command_type(self):
        if self.i == 0:
            return ""

        result = self.lines[self.i-1].split(" ")[0]

        if result in {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}:
            return "C_ARITHMETIC"
        elif result == "push":
            return "C_PUSH"
        elif result == "pop":
            return "C_POP"
        else:
            return ""

    def arg1(self):
        return self.lines[self.i-1].split(" ")[0]

    def arg2(self):
        if self.command_type() in {"C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"}:
            return self.lines[self.i-1].split(" ")[1]
        else:
            return ""

class Code_Writer():
    def __init__(self, filename):
        self.name = filename[:-3]
        self.fh = open(str(self.name + ".asm"), "w")

        # process filename for static variable
        self.name = self.name[self.name.rfind("/")+1:]

        # counter for comparison labelling
        self.comp_i = 0

        # set RAM to memory segments base address
        # self.fh.write("@256\nD=A\n@SP\nM=D\n")
        # self.fh.write("@300\nD=A\n@LCL\nM=D\n")
        # self.fh.write("@400\nD=A\n@ARG\nM=D\n")
        # self.fh.write("@3000\nD=A\n@THIS\nM=D\n")
        # self.fh.write("@3010\nD=A\n@THAT\nM=D\n")

        # segment dictionary for asm name
        self.asm = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}

    def write_arithmetic(self, command):
        # self.fh.write("// " + command + "\n")

        if command == "add":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M\n")
        elif command == "sub":
            self.fh.write("@SP\nAM=M-1\nD=-M\nA=A-1\nM=D+M\n")
        elif command == "neg":
            self.fh.write("@SP\nA=M-1\nM=-M\n")
        
        elif command == "eq":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=D-M\n")
            self.fh.write("@COMP" + str(self.comp_i) + "\n")
            self.fh.write("D;JEQ\n@SP\nA=M-1\nM=0\n")
            self.fh.write("@END" + str(self.comp_i) + "\n")
            self.fh.write("0;JMP\n")
            self.fh.write("(COMP" + str(self.comp_i) + ")\n")
            self.fh.write("@SP\nA=M-1\nM=-1\n")
            self.fh.write("(END" + str(self.comp_i) + ")\n")

            self.comp_i += 1

        elif command == "gt":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n")
            self.fh.write("@COMP" + str(self.comp_i) + "\n")
            self.fh.write("D;JGT\n@SP\nA=M-1\nM=0\n")
            self.fh.write("@END" + str(self.comp_i) + "\n")
            self.fh.write("0;JMP\n")
            self.fh.write("(COMP" + str(self.comp_i) + ")\n")
            self.fh.write("@SP\nA=M-1\nM=-1\n")
            self.fh.write("(END" + str(self.comp_i) + ")\n")

            self.comp_i += 1

        elif command == "lt":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=D-M\n")
            self.fh.write("@COMP" + str(self.comp_i) + "\n")
            self.fh.write("D;JGT\n@SP\nA=M-1\nM=0\n")
            self.fh.write("@END" + str(self.comp_i) + "\n")
            self.fh.write("0;JMP\n")
            self.fh.write("(COMP" + str(self.comp_i) + ")\n")
            self.fh.write("@SP\nA=M-1\nM=-1\n")
            self.fh.write("(END" + str(self.comp_i) + ")\n")

            self.comp_i += 1

        # bitwise and, or , not
        elif command == "and":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n")
        elif command == "or":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n")
        elif command == "not":
            self.fh.write("@SP\nA=M-1\nM=!M\n")


    def write_push_pop(self, command, segment, index):
        # write vm command on top first
        # if command == "C_PUSH":
        #     self.fh.write("// push ")
        # else:
        #     self.fh.write("// pop ")

        # self.fh.write(segment + " " + index + "\n")
        
        # for push command
        if command == "C_PUSH":
            if segment == "constant":
                self.fh.write("@" + index + "\n")
                self.fh.write("D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment in self.asm:
                self.fh.write("@" + index + "\n")
                self.fh.write("D=A\n")
                self.fh.write("@" + self.asm[segment] + "\n")
                self.fh.write("A=D+M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "temp":
                self.fh.write("@" + index + "\n")
                self.fh.write("D=A\n@5\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "static":
                self.fh.write("@" + self.name + "." + index + "\n")
                self.fh.write("D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "pointer":
                if index == "0":
                    self.fh.write("@THIS\n")
                else:
                    self.fh.write("@THAT\n")
                self.fh.write("D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")


        # for pop command
        else:
            if segment in self.asm:
                self.fh.write("@" + index + "\n")
                self.fh.write("D=A\n")
                self.fh.write("@" + self.asm[segment] + "\n")
                self.fh.write("D=D+M\n@SP\nA=M\nM=D\n@SP\nAM=M-1\nD=M\n@SP\nA=M+1\nA=M\nM=D\n")
            elif segment == "temp":
                self.fh.write("@" + index + "\n")
                self.fh.write("D=A\n")
                self.fh.write("@5\n")
                self.fh.write("D=D+A\n@SP\nA=M\nM=D\n@SP\nAM=M-1\nD=M\n@SP\nA=M+1\nA=M\nM=D\n")
            elif segment == "static":
                self.fh.write("@SP\nAM=M-1\nD=M\n")
                self.fh.write("@" + self.name + "." + index + "\n")
                self.fh.write("M=D\n")
            elif segment == "pointer":
                self.fh.write("@SP\nAM=M-1\nD=M\n")
                if index == "0":
                    self.fh.write("@THIS\n")
                else:
                    self.fh.write("@THAT\n")
                self.fh.write("M=D\n")


    def close(self):
        self.fh.close()

def main():
    parser = Parser(sys.argv[1])
    code_writer = Code_Writer(sys.argv[1])

    while(parser.has_more_commands()):
        parser.advance()

        if parser.command_type() == "C_ARITHMETIC":
            code_writer.write_arithmetic(parser.arg1())

        elif parser.command_type() in {"C_PUSH", "C_POP"}:
            code_writer.write_push_pop(parser.command_type(), parser.arg2(), parser.lines[parser.i-1].split(" ")[2])
        else:
            pass

    code_writer.close()

if __name__ == "__main__":
    main()