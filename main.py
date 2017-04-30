import json
import random


class Tetris:
    """ The Tetris Class"""
    # blockType     0-6
    # centerX
    # centerY
    # orientation   0-3
    blockShape = [
        [
            [0, 0, 1, 0, -1, 0, -1, -1],
            [0, 0, 0, 1, 0, -1, 1, -1],
            [0, 0, -1, 0, 1, 0, 1, 1],
            [0, 0, 0, -1, 0, 1, -1, 1]
        ],
        [
            [0, 0, -1, 0, 1, 0, 1, -1],
            [0, 0, 0, -1, 0, 1, 1, 1],
            [0, 0, 1, 0, -1, 0, -1, 1],
            [0, 0, 0, 1, 0, -1, -1, -1]
        ],
        [
            [0, 0, 1, 0, 0, -1, -1, -1],
            [0, 0, 0, 1, 1, 0, 1, -1],
            [0, 0, -1, 0, 0, 1, 1, 1],
            [0, 0, 0, -1, -1, 0, -1, 1]
        ],
        [
            [0, 0, -1, 0, 0, -1, 1, -1],
            [0, 0, 0, -1, 1, 0, 1, 1],
            [0, 0, 1, 0, 0, 1, -1, 1],
            [0, 0, 0, 1, -1, 0, -1, -1]
        ],
        [
            [0, 0, -1, 0, 0, 1, 1, 0],
            [0, 0, 0, -1, -1, 0, 0, 1],
            [0, 0, 1, 0, 0, -1, -1, 0],
            [0, 0, 0, 1, 1, 0, 0, -1]
        ],
        [
            [0, 0, 0, -1, 0, 1, 0, 2],
            [0, 0, 1, 0, -1, 0, -2, 0],
            [0, 0, 0, 1, 0, -1, 0, -2],
            [0, 0, -1, 0, 1, 0, 2, 0]
        ],
        [
            [0, 0, 0, 1, -1, 0, -1, 1],
            [0, 0, -1, 0, 0, -1, -1, -1],
            [0, 0, 0, -1, 1, -0, 1, -1],
            [0, 0, 1, 0, 0, 1, 1, 1]
        ]
    ]

    def __init__(self, blockType, centerX=-1, centerY=-1, orientation=-1):
        self.blockType = blockType
        self.centerX = centerX
        self.centerY = centerY
        self.orientation = orientation
        self.shape = Tetris.blockShape[self.blockType]

    def isValid(self, blockMap, centerX=-1, centerY=-1, orientation=-1):
        if centerX == -1:
            centerX = self.centerX
        if centerY == -1:
            centerY = self.centerY
        if orientation == -1:
            orientation = self.orientation

        if orientation < 0 or orientation > 3:
            return False

        for i in range(0, 4):
            tmpX = centerX + self.shape[orientation][2 * i]
            tmpY = centerY + self.shape[orientation][2 * i + 1]
            if tmpX < 1 or tmpX > Player._MAX_WIDTH_ or tmpY < 1 or tmpY > Player._MAX_HEIGHT_ or blockMap.data[tmpY][tmpX] != 0:
                return False

        return True

    def onGround(self, blockMap):
        return self.isValid(blockMap) and (not self.isValid(blockMap, -1, self.centerY - 1))

    def place(self, blockMap):
        if not self.onGround(blockMap):
            return False

        for i in range(0, 4):
            tmpX = self.centerX + self.shape[self.orientation][2 * i]
            tmpY = self.centerY + self.shape[self.orientation][2 * i + 1]
            blockMap.data[tmpY][tmpX] = 2

        return True

    def rotation(self, blockMap, orientation):
        if orientation < 0 or orientation > 3:
            return False

        if orientation == self.orientation:
            return True

        fromO = self.orientation
        while True:
            if not self.isValid(blockMap, -1, -1, fromO):
                return False

            if fromO == orientation:
                break

            fromO = (fromO + 1) % 4

        return True


class Player:
    """ The Player Class """
    # color - [0, 1]
    # blockNumber - list (size 7)
    # map

    _MAX_WIDTH_ = 10
    _MAX_HEIGHT_ = 20

    def __init__(self, color):
        self.color = color
        self.blockNumber = [0, 0, 0, 0, 0, 0, 0]
        self.score = 0
        self.map = BlockMap(color, Player._MAX_HEIGHT_, Player._MAX_WIDTH_)

    def __format__(self, format_spec):
        return 'color {}, blockNumber {}, score {}'.format(self.color, self.blockNumber, self.score)


class Game:
    """ The Game Class """
    # players

    def __init__(self, redPlayer, bluePlayer):
        self.players = (redPlayer, bluePlayer)

    def __format__(self, format_spec):
        return 'Red Player\t[{}]\nBlue Player\t[{}]'.format(self.players[0], self.players[1])


class BlockMap:
    # data
    # transCount
    # maxHeight
    # elimTotal
    # color

    elimBonus = [0, 1, 3, 5, 7]

    def __init__(self, color, height, width):
        self.color = color
        self.data = [[0 for x in range(width + 2)] for y in range(height + 2)]
        self.transCount = 0
        self.trans = [[0 for x in range(width + 2)] for y in range(4)]
        self.maxHeight = 0
        self.elimTotal = 0

        # init
        for i in range (0, width + 2):
            self.data[0][i] = -2
            self.data[height + 1][i] = -2
        for i in range (0, height + 2):
            self.data[i][0] = -2
            self.data[i][width + 1] = -2

    def checkDirectDropTo(self, blockType, centerX, centerY, orientation):
        _def = Tetris.blockShape[blockType][orientation]
        for j in range(centerY, Player._MAX_HEIGHT_ + 1):
            for i in range(4):
                _x = _def[i * 2] + centerX
                _y = _def[i * 2 + 1] + j

                if _y > Player._MAX_HEIGHT_:
                    continue

                if _y < 1 or _x < 1 or _x > Player._MAX_WIDTH_ or self.data[_y][_x]:
                    # print(x, y, o, 'ha!')
                    return False

        return True

    def eliminate(self):
        self.transCount = 0
        self.maxHeight = Player._MAX_HEIGHT_
        for i in range(1, Player._MAX_HEIGHT_ + 1):
            emptyFlag = 1
            fullFlag = 1
            for j in range(1, Player._MAX_WIDTH_ + 1):
                if self.data[i][j] == 0:
                    fullFlag = 0
                else:
                    emptyFlag = 0

            if fullFlag:
                for j in range(1, Player._MAX_WIDTH_ + 1):
                    if self.data[i][j] == 1:
                        self.trans[self.transCount][j] = 1
                    else:
                        self.trans[self.transCount][j] = 0
                    self.data[i][j] = 0
                self.transCount += 1
            elif emptyFlag:
                self.maxHeight = i - 1
                break
            else:
                for j in range(1, Player._MAX_WIDTH_ + 1):
                    if self.data[i][j] > 0:
                        self.data[i - self.transCount][j] = 1
                    else:
                        self.data[i - self.transCount][j] = self.data[i][j]

                    if self.transCount:
                        self.data[i][j] = 0

        self.maxHeight -= self.transCount
        self.elimTotal += BlockMap.elimBonus[self.transCount]

    @staticmethod
    def transfer(first, second):
        if first.transCount == 0 and second.transCount == 0:
            return -1

        if first.transCount == 0 or second.transCount == 0:
            if first.transCount == 0 and second.transCount > 0:
                (second, first) = (first, second)
            h2 = second.maxHeight + first.transCount
            second.maxHeight = h2

            if h2 > Player._MAX_HEIGHT_:
                return second.color

            for i in range(h2, first.transCount, -1):
                for j in range(1, Player._MAX_WIDTH_ + 1):
                    second.data[i][j] = second.data[i - first.transCount][j]

            for i in range(first.transCount, 0, -1):
                for j in range(1, Player._MAX_WIDTH_ + 1):
                    second.data[i][j] = first.trans[i - 1][j]

            return -1
        else:
            h1 = first.maxHeight + second.transCount
            h2 = second.maxHeight + first.transCount

            first.maxHeight = h1
            second.maxHeight = h2

            if h1 > Player._MAX_HEIGHT_:
                return first.color
            if h2 > Player._MAX_HEIGHT_:
                return second.color

            for i in range(h2, first.transCount, -1):
                for j in range(1, Player._MAX_WIDTH_ + 1):
                    second.data[i][j] = second.data[i - first.transCount][j]

            for i in range(first.transCount, 0, -1):
                for j in range(1, Player._MAX_WIDTH_ + 1):
                    second.data[i][j] = first.trans[i - 1][j]

            for i in range(h1, second.transCount, -1):
                for j in range(1, Player._MAX_WIDTH_ + 1):
                    first.data[i][j] = first.data[i - second.transCount][j]

            for i in range(second.transCount, 0, -1):
                for j in range(1, Player._MAX_WIDTH_ + 1):
                    first.data[i][j] = second.trans[i - 1][j]

            return -1

    def canPut(self, blockType):
        for y in range(Player._MAX_HEIGHT_, 0, -1):
            for x in range(1, Player._MAX_WIDTH_ + 1):
                for orientation in range(4):
                    t = Tetris(blockType, x, y, orientation)
                    if t.isValid(self) and self.checkDirectDropTo(blockType, x, y, orientation):
                        return True

        return False

    def print(self):
        i2s = ['~~', '~~', '  ', '[]', '##']

        for y in range(Player._MAX_HEIGHT_ + 1, -1, -1):
            print([i2s[self.data[y][x] + 2] for x in range(Player._MAX_WIDTH_ + 2)])


data = json.loads(input())

turnId = len(data['responses']) + 1
first = data['requests'][0]

blockType = first['block']
currBotColor = first['color']
enemyColor = 1 - currBotColor
nextTypeForColor = [blockType, blockType]

players = [Player(i) for i in range(2)]
botPlayer = players[currBotColor]
enemyPlayer = players[enemyColor]

botPlayer.blockNumber[blockType] += 1
enemyPlayer.blockNumber[blockType] += 1

for i in range(1, turnId):
    currTypeForColor = [nextTypeForColor[0], nextTypeForColor[1]]
    myOutput = data['responses'][i - 1]
    blockType = myOutput['block']
    x = myOutput['x']
    y = myOutput['y']
    o = myOutput['o']

    myBlock = Tetris(currTypeForColor[currBotColor], x, y, o)
    myBlock.place(botPlayer.map)

    enemyPlayer.blockNumber[blockType] += 1
    nextTypeForColor[enemyColor] = blockType

    myInput = data['requests'][i]
    blockType = myInput['block']
    x = myInput['x']
    y = myInput['y']
    o = myInput['o']
    enemyBlock = Tetris(currTypeForColor[enemyColor], x, y, o)
    enemyBlock.place(enemyPlayer.map)

    botPlayer.blockNumber[blockType] += 1
    nextTypeForColor[currBotColor] = blockType

    botPlayer.map.eliminate()
    enemyPlayer.map.eliminate()
    BlockMap.transfer(players[0].map, players[1].map)

# players[0].map.print()
# players[1].map.print()

def determine(_blockType, bot):
    for y in range(1, Player._MAX_HEIGHT_ + 1):
        for x in range(1, Player._MAX_WIDTH_ + 1):
            for o in range(4):
                block = Tetris(_blockType, x, y, o)

                if block.isValid(bot.map) and bot.map.checkDirectDropTo(block.blockType, x, y, o):
                    return (x, y, o)

(finalX, finalY, finalO) = determine(nextTypeForColor[currBotColor], botPlayer)

maxCount = 0
minCount = 99
for i in range(7):
    if enemyPlayer.blockNumber[i] > maxCount:
        maxCount = enemyPlayer.blockNumber[i]
    if enemyPlayer.blockNumber[i] < minCount:
        minCount = enemyPlayer.blockNumber[i]

if maxCount - minCount >= 2:
    for blockForEnemy in range(7):
        if not enemyPlayer.blockNumber[blockForEnemy] == maxCount:
            break
else:
    blockForEnemy = random.randrange(7)

output = {}
output["response"] = {}
output["response"]["block"] = blockForEnemy
output["response"]["x"] = finalX
output["response"]["y"] = finalY
output["response"]["o"] = finalO

print(json.dumps(output))
# tetris = Game(redPlayer, bluePlayer)
# print('{}'.format(tetris))