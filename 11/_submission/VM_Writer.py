from enum import Enum, auto
from typing import TextIO

class Segment_Type(Enum):
    CONST = auto()
    ARG = auto()
    LOCAL = auto()
    STATIC = auto()
    THIS = auto()
    THAT = auto()
    POINTER = auto()
    TEMP = auto()

    def __str__(self) -> str:
        if self is self.CONST:
            return "constant"
        elif self is self.ARG:
            return "argument"
        else:
            return str(self.name).lower()

class Command_Type(Enum):
    ADD = auto()
    SUB = auto()
    NEG = auto()
    EQ = auto()
    GT = auto()
    LT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # call Math.multipy()
    MULT = auto()
    # call Math.divide()
    DIV = auto()

    def __str__(self) -> str:
        return str(self.name).lower()

class VM_Writer:
    fh: TextIO

    def __init__(self, filename: str) -> None:
        self.fh = open(f"{filename[:-5]}.vm", "w")

    def write_push(self, segment: Segment_Type, index: int) -> None:
        self.fh.write(f"push {segment} {index}\n")

    def write_pop(self, segment: Segment_Type, index: int) -> None:
        self.fh.write(f"pop {segment} {index}\n")

    def write_arithmetic(self, command: Command_Type) -> None:
        if command is Command_Type.MULT:
            self.write_call("Math.multiply", 2)
        elif command is Command_Type.DIV:
            self.write_call("Math.divide", 2)
        else:
            self.fh.write(f"{command}\n")

    def write_label(self, label: str) -> None:
        self.fh.write(f"label {label}\n")

    def write_goto(self, label: str) -> None:
        self.fh.write(f"goto {label}\n")

    def write_if(self, label: str) -> None:
        self.fh.write(f"if-goto {label}\n")

    def write_call(self, label: str, n_args: int) -> None:
        self.fh.write(f"call {label} {n_args}\n")

    def write_function(self, label: str, n_locals: int) -> None:
        self.fh.write(f"function {label} {n_locals}\n")

    def write_return(self) -> None:
        self.fh.write("return\n")

    def close(self) -> None:
        self.fh.close()
