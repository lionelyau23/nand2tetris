import os, sys
from Compilation_Engine import Compliation_Engine
from Jack_Tokenizer import Jack_Tokienizer, Type_of_token
from Symbol_Table import Symbol_Table, Variable_Kind

def main():
    files = []
    # files.append("tests/Seven/Main.jack")

    if (sys.argv[1][-5:] == ".jack"):
        files.append(sys.argv[1])
    else:
        path = (lambda a : a + "/" if a[len(a)-1] != "/" else a)(sys.argv[1])
        files.extend(path + x for x in os.listdir(sys.argv[1]) if ".jack" in x)

    for file in files:
        tokenizer = Jack_Tokienizer(file)
        # print(Type_of_token.STRING_CONST)
        # tokenizer.debug_write()
        # with open(str(file[:-5] + ".xml"), "w") as fh:
        ce = Compliation_Engine(file, tokenizer)
        ce.compile_class()
        ce.close()

if __name__ == "__main__":
    main()