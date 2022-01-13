// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
@256
D=A

@rows
M=D     //set no. of rows to 256

@32
D=A

@cols
M=D     //set no. of cols to 32

(KEY)
@SCREEN
D=A

@loc
M=D     //set screen RAM location to loc

@KBD
D=M

@WHITE
D;JEQ

@pixel
M=-1

@PRINT
0;JMP

(WHITE)
@pixel
M=0     //set the pixel flag to 0 to print white screen initially

(PRINT)
@row_num
M=0     //start at row 0

(LOOP_ROW)  //start LOOP thru rows
@rows
D=M

@row_num
D=D-M

@KEY
D;JEQ   //end if row reaches end

@col_num
M=0     //start at col 0

@row_num
M=M+1   //increment to next row

(LOOP_COL)  //start LOOP thru cols
@cols
D=M

@col_num
D=D-M

@LOOP_ROW
D;JEQ

@pixel
D=M

@loc
A=M
M=D

@loc
M=M+1   //update screen loc

@col_num
M=M+1

@LOOP_COL
0;JMP
