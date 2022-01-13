from enum import Enum, auto

class Variable_Kind(Enum):
    STATIC = auto()
    FIELD = auto()
    ARG = auto()
    VAR = auto()
    NONE = auto()

class Symbol_Table:
    # table = {}
    # static_table = {}
    # field_table = {}
    # arg_table = {}
    # local_table = {}
    class_table = {}
    subroutine_table = {}

    field_n: int
    static_n: int

    local_n: int
    arg_n: int

    def __init__(self) -> None:
        self.class_table = {}
        self.field_n = 0
        self.static_n = 0
        # self.static_table = {}
        # self.field_table = {}

    def start_subroutine(self) -> None:
        self.subroutine_table = {}
        self.local_n = 0
        self.arg_n = 0
        # self.arg_table = {}
        # self.local_table = {}

    def define(self, name: str, type: str, kind: Variable_Kind) -> None:
        if kind in {Variable_Kind.STATIC, Variable_Kind.FIELD}:
            self.class_table[name] = {}
            self.class_table[name]["type"] = type
            self.class_table[name]["kind"] = kind
            # self.class_table[name]["i"] = len([key for key in self.class_table if self.class_table[key][kind] == kind]) - 1

            if kind == Variable_Kind.STATIC:
                self.class_table[name]["index"] = self.static_n
                self.static_n += 1
            else:
                self.class_table[name]["index"] = self.field_n
                self.field_n += 1

        else:
            self.subroutine_table[name] = {}
            self.subroutine_table[name]["type"] = type
            self.subroutine_table[name]["kind"] = kind

            if kind == Variable_Kind.ARG:
                self.subroutine_table[name]["index"] = self.arg_n
                self.arg_n += 1
            else:
                self.subroutine_table[name]["index"] = self.local_n
                self.local_n += 1

    def var_count(self, kind: Variable_Kind) -> int:
        if kind == Variable_Kind.STATIC:
            return self.static_n
        elif kind == Variable_Kind.FIELD:
            return self.field_n
        elif kind == Variable_Kind.VAR:
            return self.local_n
        else:
            return self.arg_n

    def kind_of(self, name: str) -> Variable_Kind:
        if name in self.subroutine_table:
            return self.subroutine_table[name]["kind"]
        elif name in self.class_table:
            return self.class_table[name]["kind"]
        else:
            return Variable_Kind.NONE

    def type_of(self, name: str) -> str:
        if name in self.subroutine_table:
            return self.subroutine_table[name]["type"]
        else:
            return self.class_table[name]["type"]

    def index_of(self, name: str) -> int:
        if name in self.subroutine_table:
            return self.subroutine_table[name]["index"]
        else:
            return self.class_table[name]["index"]