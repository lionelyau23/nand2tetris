import os, sys
from Compilation_Engine import Compliation_Engine
from Jack_Tokenizer import Jack_Tokienizer
from Compilation_Engine import Compliation_Engine

def main():
    files = []

    if (sys.argv[1][-5:] == ".jack"):
        files.append(sys.argv[1])
    else:
        path = (lambda a : a + "/" if a[len(a)-1] != "/" else a)(sys.argv[1])
        files.extend(path + x for x in os.listdir(sys.argv[1]) if ".jack" in x)

    for file in files:
        tokenizer = Jack_Tokienizer(file)
        # tokenizer.debug_write()
        fh = open(str(file[:-5] + ".xml"), "w")
        ce = Compliation_Engine(fh, tokenizer)
        ce.compile_class()
        fh.close()

if __name__ == "__main__":
    main()