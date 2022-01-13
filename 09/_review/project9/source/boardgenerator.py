"""
bitmasking:
    left = 1
    up = 2
    right = 4
    down = 8
    horizontalJump = 16
    verticalJump = 32 (not yet implemented)
    normal dot = 64
    big dot = 128 (not yet implemented)
"""


class BoardGenerator(object) :
    def __init__(self):
        # all 2D arrays are indexed as arr[y][x]
        self.txt = []       # 2D array of each character in map2.txt (each row just saved as a string)
        self.grid = []      # 2D array of grid points - 64 wide (x) by 32 tall (y)
        self.tiles = []     # 2D array of 8x8 tiles - 64 wide (x) by 32 tall (y)
        self.bitmap = []    # 2D array of each pixel in the 512 (x) by 256 (y) screen : #=white, ' '=black
        self.screen = []    # 2D array of memory addresses - 32 wide (x: 16-pixel registers) by 256 tall (y)
        self.charStart = {} # starting points of pacman and ghosts charStart[characterNumber]=(x,y), where pacman = 0 and ghosts = 1-4
        self.jumpColumns = set()
        self.numDots = 0    # total number of dots in the map


    def loadMap(self, mapFile):
        with open(mapFile, 'r') as f:
            for line in f.readlines():
                row = []
                for c in line:
                    if c not in '|\n':
                        row.append(c)
                self.txt.append(row)


    def makeGridAndTiles(self):
        for y in range(32):
            gridRow = []
            tileRow = []
            for x in range(64):
                gridValue = 0
                tileValue = None
                symbol = self.txt[y][x]
                if symbol == '-':
                    gridValue = self.makePathPoint(x, y)
                    tileValue = self.makeDotTile();
                elif symbol == '.':
                    gridValue = self.makePathPoint(x, y, dot=False)
                elif symbol in '01234:':
                    gridValue = self.makePathPoint(x, y, dot=False, ghostHouse=(symbol in '234:'))
                    self.charStart[symbol] = (x, y)
                elif symbol == '=':
                    gridValue = self.makePathPoint(x, y, dot=False, jump=True)
                elif symbol == '#':
                    tileValue = self.makeWallTile(x, y)
                elif symbol == '~':
                    tileValue = self.makeWallTile(x, y, ghostWall=True)
                elif symbol == ' ':
                    pass
                else:
                    print (f'WARNING: unexpected character in map file: [{symbol}]')
                gridRow.append(gridValue)
                tileRow.append(tileValue)
            self.grid.append(gridRow)
            self.tiles.append(tileRow)


    def makePathPoint(self, x, y, dot=True, jump=False, ghostHouse=False):
        if dot:
            self.numDots += 1
        pathSymbols = '-.=01234'
        bitmaskValue = 0
        # basic directions
        if self.txt[y][x-1] in pathSymbols: bitmaskValue += 1 # left
        if self.txt[y-1][x] in pathSymbols: bitmaskValue += 2 # up
        if self.txt[y][x+1] in pathSymbols: bitmaskValue += 4 # right
        if self.txt[y+1][x] in pathSymbols: bitmaskValue += 8 # down
        # ghosts make a decision if there are 3 or more options
        # ghost direction choices are same as above but times 256
        # decode as (bitmask & 3840 / 256)
        if bitmaskValue in [7,11,13,14,15]:
            bitmaskValue += bitmaskValue * 256
        if jump:
                bitmaskValue += 16
                self.jumpColumns.add(x)
        if ghostHouse:
                bitmaskValue += 32
        if dot: bitmaskValue += 64
        # superdot would be 128, not yet implemented
        return bitmaskValue


    def makeDotTile(self):
        out = [ '        ',
                '        ',
                '        ',
                '    ##  ',
                '    ##  ',
                '        ',
                '        ',
                '        ']
        out = self._stringsToMatrix(out)
        return out;


    def makeWallTile(self, x, y, ghostWall=False):
        adjMap = [  [self._wadj(x-1,y-1), self._wadj(x,y-1), self._wadj(x+1,y-1)],
                    [self._wadj(x-1,y),   self._wadj(x,y),   self._wadj(x+1,y)],
                    [self._wadj(x-1,y+1), self._wadj(x,y+1), self._wadj(x+1,y+1)]]

        if ghostWall:           # pretty special case, handle this first
            out = [ '        ',
                    '        ',
                    '        ',
                    '        ',
                    '        ',
                    '        ',
                    '        ',
                    # ' # # # #',
                    '# # # # ']
            out = self._stringsToMatrix(out)
            if self._wadj(x,y-1) == '#':    # if this is the lower of the two ghost walls...
                out = self._rotate(out)
                out = self._rotate(out)
            return out

        out = None
        i = 0
        while i < 8 and out is None:
            if self._adjMatch(adjMap,
                   [[' ',' ',' '],
                    [' ','#','#'],
                    [' ','#','-']]): out = ['  ######',
                                            ' #######',
                                            '###     ',
                                            '##      ',
                                            '##      ',
                                            '##      ',
                                            '##      ',
                                            '##      ']; test = True
            elif self._adjMatch(adjMap,
                   [['?','?','?'],
                    ['#','#','#'],
                    ['?','-','?']]): out = ['########',
                                            '########',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '        ']
            elif self._adjMatch(adjMap,
                   [['?','-','-'],
                    ['#','#','-'],
                    ['?','#','?']]): out = ['        ',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '#       ',
                                            '##      ']
            elif self._adjMatch(adjMap,
                   [[' ',' ',' '],
                    ['#','#',' '],
                    ['-','-',' ']]): out = ['########',
                                            '########',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '        ',
                                            '        ']
            elif self._adjMatch(adjMap,
                   [['?','?','?'],
                    ['?','#','#'],
                    ['?','#','-']]): out = ['########',
                                            '########',
                                            '###     ',
                                            '##      ',
                                            '##      ',
                                            '##      ',
                                            '##      ',
                                            '##      ']
            elif self._adjMatch(adjMap,
                   [['?',' ','?'],
                    ['#','#','#'],
                    ['#','#','#']]): out = ['########',
                                            '########',
                                            '########',
                                            '########',
                                            '########',
                                            '########',
                                            '########',
                                            '########']
            elif self._adjMatch(adjMap,
                   [['#','#','#'],
                    ['#','#','#'],
                    ['#','#','#']]): out = ['########',
                                            '########',
                                            '########',
                                            '########',
                                            '########',
                                            '########',
                                            '########',
                                            '########']
            else:
                adjMap = self._rotate(adjMap)
                i += 1
                if i == 4:
                    adjMap = self._flip(adjMap)

        if out is not None:
            out = self._stringsToMatrix(out)
            if i == 0:
                return out
            if i < 4:
                while i < 4:
                    out = self._rotate(out)
                    i += 1
            elif i == 4:
                out = self._flip(out)
            else:
                while i < 8:
                    out = self._rotate(out)
                    i += 1
                out = self._flip(out)
            return out

        else:
            print('==== unhandled wall configuration: ====')
            printMatrix(out)
            print(f'==== at ({x}, {y}) ====')
            import IPython; IPython.embed(); raise

    def _adjMatch(self, actual, template):
        for i in range(3):
            for j in range(3):
                if not (template[i][j] == '?' or template[i][j] == actual[i][j]):
                    return False
        return True

    def _wadj(self, x, y):
        if self.txt[y][x] in '#~':
            return '#'
        if self.txt[y][x] in '-.=01234:':
            return '-'
        return ' '

    def _rotate(self, m):
        for row in m:
            row.reverse()
        for i in range(len(m)):
            for j in range(i):
                m[i][j], m[j][i] = m[j][i], m[i][j]
        return m

    def _flip(self, m):
        for row in m:
            row.reverse()
        return m

    def _stringsToMatrix(self, strings):
        m = []
        for string in strings:
            row = []
            for c in string:
                row.append(c)
            m.append(row)
        return m


    def makeBitmap(self):
        for y in range(32):
            rows = ['','','','','','','','']
            for x in range(64):
                if self.tiles[y][x] is None:
                    for i in range(8):
                        rows[i] += '        '
                else:
                    for i, tileRow in enumerate(self.tiles[y][x]):
                        for c in tileRow:
                            rows[i] += c
            for row in rows:
                self.bitmap.append(row)

    def offsetBitmap(self):
        vOffset = -4
        hOffset = '                                    '
        self.bitmap = self.bitmap[vOffset:] + self.bitmap[:vOffset]
        for i in range(len(self.bitmap)):
            self.bitmap[i] = hOffset + self.bitmap[i]


    def writeSetupCode(self):
        outCode =  ['class Setup {\n',
                    '    constructor Setup new() { return this; }\n',
                    '\n',
                    '    function void loadGrid(Grid grid) {\n']
        outCode += self.gridCode()
        outCode += ['    return;\n',
                    '    }\n',
                    '\n',
                    '    function void drawInitScreen() {\n',
                    '        do Screen.setColor(true);\n',
                    '        do Screen.drawRectangle(0, 0, 511, 255);\n']
        outCode += self.screenCode()
        outCode += ['    return;\n',
                    '    }\n',
                    # '\n',
                    # '    method void dispose() {\n',
                    # '        do Memory.deAlloc(this);\n',
                    # '        return;\n',
                    # '    }\n',
                    '}\n']
        with open('Setup.jack', 'w') as f:
            f.writelines(outCode)

    def gridCode(self):
        outCode = []
        for y in range(32):
            for x in range(64):
                val = self.grid[y][x]
                if val != 0:
                    arrLoc = y*64+x
                    outCode.append(f'        do grid.set({arrLoc}, {val});\n')
        return outCode

    def otherSetupCode(self):
        pass

    def screenCode(self):
        outCode = []
        for y in range(256):     # 256
            for j in range(32):      #32
                val = 0
                for k in range(16):
                    x = j*16+k
                    if self.bitmap[y][x] == ' ':
                        if k <= 14:
                            val += 2**k
                        else:
                            val -= 2**k
                if val != -1:
                    memAddress = 16384 + y*32 + j
                    outCode.append(f'        do Memory.poke({memAddress}, {val});\n')
        return outCode


    def writeBitmap(self):
        with open('bitmap.txt', 'w') as f:
            for row in self.bitmap:
                line = ''
                for c in row:
                    line += c
                line += '\n'
                f.write(line)

def printMatrix(m):
    for row in m:
        s = ''
        for entry in row:
            s += str(entry)
        print(s)




if __name__ == '__main__':
    bg = BoardGenerator()
    bg.loadMap('map2.txt')
    bg.makeGridAndTiles()
    bg.makeBitmap()
    bg.offsetBitmap()
    bg.writeBitmap()
    bg.writeSetupCode()
    print(f'character start points: {bg.charStart}')
    print(f'jump columns: {bg.jumpColumns}')
    print(f'number of dots at beginning of game: {bg.numDots}')
