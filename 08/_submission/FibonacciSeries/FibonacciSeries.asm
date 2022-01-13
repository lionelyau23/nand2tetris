////////////////////
// FibonacciSeries.vm
////////////////////
// push argument 1
@1
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@SP
AM=M-1
D=M
@THAT
M=D
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 0
@0
D=A
@THAT
D=D+M
@SP
A=M
M=D
@SP
AM=M-1
D=M
@SP
A=M+1
A=M
M=D
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 1
@1
D=A
@THAT
D=D+M
@SP
A=M
M=D
@SP
AM=M-1
D=M
@SP
A=M+1
A=M
M=D
// push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=-M
A=A-1
M=D+M
// pop argument 0
@0
D=A
@ARG
D=D+M
@SP
A=M
M=D
@SP
AM=M-1
D=M
@SP
A=M+1
A=M
M=D
// label MAIN_LOOP_START
(FibonacciSeries.$MAIN_LOOP_START)
// push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// if-goto COMPUTE_ELEMENT
@SP
AM=M-1
D=M
@END0
D;JEQ
@FibonacciSeries.$COMPUTE_ELEMENT
0;JMP
(END0)
// goto END_PROGRAM
@FibonacciSeries.$END_PROGRAM
0;JMP
// label COMPUTE_ELEMENT
(FibonacciSeries.$COMPUTE_ELEMENT)
// push that 0
@0
D=A
@THAT
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push that 1
@1
D=A
@THAT
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=D+M
// pop that 2
@2
D=A
@THAT
D=D+M
@SP
A=M
M=D
@SP
AM=M-1
D=M
@SP
A=M+1
A=M
M=D
// push pointer 1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=D+M
// pop pointer 1
@SP
AM=M-1
D=M
@THAT
M=D
// push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=-M
A=A-1
M=D+M
// pop argument 0
@0
D=A
@ARG
D=D+M
@SP
A=M
M=D
@SP
AM=M-1
D=M
@SP
A=M+1
A=M
M=D
// goto MAIN_LOOP_START
@FibonacciSeries.$MAIN_LOOP_START
0;JMP
// label END_PROGRAM
(FibonacciSeries.$END_PROGRAM)
