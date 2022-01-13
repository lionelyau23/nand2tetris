import os, sys

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
        elif result == "label":
            return "C_LABEL"
        elif result == "goto":
            return "C_GOTO"
        elif result == "if-goto":
            return "C_IF"
        elif result == "function":
            return "C_FUNCTION"
        elif result == "return":
            return "C_RETURN"
        elif result == "call":
            return "C_CALL"
        else:
            return ""

    def arg1(self):
        if self.command_type() == "C_ARITHMETIC":
            return self.lines[self.i-1].split(" ")[0]
        else:
            return self.lines[self.i-1].split(" ")[1]

    def arg2(self):
        if self.command_type() in {"C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"}:
            return self.lines[self.i-1].split(" ")[2]
        else:
            return ""

class Code_Writer():
    def __init__(self, filename):

        self.name = ""
        self.set_filename(filename)

        # store the current function name for labels
        self.function_name = ""

        # store id for local labels
        self.label_id = 0

        # store id for function calls
        self.call_id = 0

        # set RAM to memory segments base address
        # self.fh.write("@256\nD=A\n@SP\nM=D\n")
        # self.fh.write("@300\nD=A\n@LCL\nM=D\n")
        # self.fh.write("@400\nD=A\n@ARG\nM=D\n")
        # self.fh.write("@3000\nD=A\n@THIS\nM=D\n")
        # self.fh.write("@3010\nD=A\n@THAT\nM=D\n")

        # segment dictionary for asm name
        self.asm = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}
        
        # if file is .vm, translate as is, dont add bootstrap code
        if filename[-3:] == ".vm":
            self.fh = open(str(filename[:-3] + ".asm"), "w")
        # if directory is provided, add bootstrap code
        else:
            self.fh = open(str(filename + filename[:-1][filename[:-1].rfind("/")+1:] + ".asm"), "w")
            self.write_init()

    def set_filename(self, filename):
        if filename[-3:] == ".vm":
            self.name = filename[filename.rfind("/")+1:]
            self.name = self.name[:-3]
        else:
            self.name = "Sys"

    def write_init(self):
        self.fh.write("// SP = 256\n")
        self.fh.write("@256\nD=A\n@SP\nM=D\n")
        self.function_name = "Sys.init"
        self.write_call("Sys.init", "0")


    def write_arithmetic(self, command):
        self.fh.write("// " + command + "\n")

        if command == "add":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M\n")
        elif command == "sub":
            self.fh.write("@SP\nAM=M-1\nD=-M\nA=A-1\nM=D+M\n")
        elif command == "neg":
            self.fh.write("@SP\nA=M-1\nM=-M\n")
        
        elif command == "eq":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=D-M\n")
            self.fh.write("@COMP" + str(self.label_id) + "\n")
            self.fh.write("D;JEQ\n@SP\nA=M-1\nM=0\n")
            self.fh.write("@END" + str(self.label_id) + "\n")
            self.fh.write("0;JMP\n")
            self.fh.write("(COMP" + str(self.label_id) + ")\n")
            self.fh.write("@SP\nA=M-1\nM=-1\n")
            self.fh.write("(END" + str(self.label_id) + ")\n")

            self.label_id += 1

        elif command == "gt":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n")
            self.fh.write("@COMP" + str(self.label_id) + "\n")
            self.fh.write("D;JGT\n@SP\nA=M-1\nM=0\n")
            self.fh.write("@END" + str(self.label_id) + "\n")
            self.fh.write("0;JMP\n")
            self.fh.write("(COMP" + str(self.label_id) + ")\n")
            self.fh.write("@SP\nA=M-1\nM=-1\n")
            self.fh.write("(END" + str(self.label_id) + ")\n")

            self.label_id += 1

        elif command == "lt":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=D-M\n")
            self.fh.write("@COMP" + str(self.label_id) + "\n")
            self.fh.write("D;JGT\n@SP\nA=M-1\nM=0\n")
            self.fh.write("@END" + str(self.label_id) + "\n")
            self.fh.write("0;JMP\n")
            self.fh.write("(COMP" + str(self.label_id) + ")\n")
            self.fh.write("@SP\nA=M-1\nM=-1\n")
            self.fh.write("(END" + str(self.label_id) + ")\n")

            self.label_id += 1

        # bitwise and, or , not
        elif command == "and":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n")
        elif command == "or":
            self.fh.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n")
        elif command == "not":
            self.fh.write("@SP\nA=M-1\nM=!M\n")

    def write_push_pop(self, command, segment, index):
        # write vm command on top first
        if command == "C_PUSH":
            self.fh.write("// push ")
        else:
            self.fh.write("// pop ")

        self.fh.write(segment + " " + index + "\n")
        
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

    def write_label(self, label):
        self.fh.write("// label " + label + "\n")

        self.fh.write("(" + self.function_name + "$" + label + ")\n")

    def write_goto(self, label):
        self.fh.write("// goto " + label + "\n")

        self.fh.write("@" + self.function_name + "$" + label + "\n")
        self.fh.write("0;JMP\n")

    def write_if(self, label):
        self.fh.write("// if-goto " + label + "\n")

        self.fh.write("@SP\nAM=M-1\nD=M\n")
        self.fh.write("@END" + str(self.label_id) + "\n")
        self.fh.write("D;JEQ\n")
        self.fh.write("@" + self.function_name + "$" + label + "\n")
        self.fh.write("0;JMP\n")
        self.fh.write("(END"+ str(self.label_id) + ")\n")

    def write_function(self, name, n):
        self.fh.write("// function " + name +  " " + n + "\n")
        
        # set current function name
        self.function_name = name

        output = ""

        output += "(" + self.function_name + ")\n"
        output += "@" + n + "\n"
        output += "D=A\n"
        output += "(LOOP" + str(self.label_id) + ")\n"
        output += "@END" + str(self.label_id) + "\n"
        output += "D;JEQ\n@SP\nA=M\nM=0\n@SP\nM=M+1\nD=D-1\n"
        output += "@LOOP" + str(self.label_id) + "\n"
        output += "0;JMP\n"
        output += "(END" + str(self.label_id) + ")\n"

        self.fh.write(output)

        self.label_id += 1

    def write_call(self, name, n):
        self.fh.write("// call " + name +  " " + n + "\n")

        output = ""

        output += "@" + self.function_name + "$ret." + str(self.call_id) + "\n"
        output += "D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        output += "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        output += "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        output += "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        output += "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        output += "@SP\nD=M\n@5\nD=D-A\n@" + n + "\nD=D-A\n@ARG\nM=D\n"
        output += "@SP\nD=M\n@LCL\nM=D\n"
        output += "@" + name + "\n"
        output += "0;JMP\n"
        output += "(" + self.function_name + "$ret." + str(self.call_id) + ")\n"

        self.fh.write(output)

        self.call_id += 1

    def write_return(self):
        self.fh.write("// return\n")

        output = ""

        output += "@LCL\nD=M\n@R13\nM=D\n"
        output += "@5\nA=D-A\nD=M\n@R14\nM=D\n"
        output += "@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n"
        output += "D=A\n@SP\nM=D+1\n"
        output += "@R13\nAM=M-1\nD=M\n@THAT\nM=D\n"
        output += "@R13\nAM=M-1\nD=M\n@THIS\nM=D\n"
        output += "@R13\nAM=M-1\nD=M\n@ARG\nM=D\n"
        output += "@R13\nAM=M-1\nD=M\n@LCL\nM=D\n"
        output += "@R14\nA=M\n0;JMP\n"

        self.fh.write(output)

    def close(self):
        self.fh.close()

def main():
    # list of files to be translated
    files = []

    # if single vm file passed as argument
    if sys.argv[1][-3:] == ".vm":
        files.append(sys.argv[1])
        code_writer = Code_Writer(sys.argv[1])
    
    # if a directory is passed as argument
    else:
        # append "/" to directory if not already
        path = (lambda a : a + "/" if a[len(a)-1] != "/" else a)(sys.argv[1])

        # add Sys.vm as first file then add other files
        files.append(path + "Sys.vm")
        files.extend(path + x for x in os.listdir(sys.argv[1]) if ".vm" in x and x != "Sys.vm")

        code_writer = Code_Writer(path)

    # print(files)
    # print(code_writer.name)

    for file in files:
        parser = Parser(file)
        code_writer.set_filename(file)
        code_writer.fh.write("////////////////////\n// " + code_writer.name + ".vm\n////////////////////\n")

        while(parser.has_more_commands()):
            parser.advance()

            if parser.command_type() == "C_ARITHMETIC":
                code_writer.write_arithmetic(parser.arg1())
            elif parser.command_type() in {"C_PUSH", "C_POP"}:
                code_writer.write_push_pop(parser.command_type(), parser.arg1(), parser.arg2())
            elif parser.command_type() == "C_LABEL":
                code_writer.write_label(parser.arg1())
            elif parser.command_type() == "C_IF":
                code_writer.write_if(parser.arg1())
            elif parser.command_type() == "C_GOTO":
                code_writer.write_goto(parser.arg1())
            elif parser.command_type() == "C_FUNCTION":
                code_writer.write_function(parser.arg1(), parser.arg2())
            elif parser.command_type() == "C_CALL":
                code_writer.write_call(parser.arg1(), parser.arg2())
            elif parser.command_type() == "C_RETURN":
                code_writer.write_return()
    
    code_writer.close()

if __name__ == "__main__":
    main()