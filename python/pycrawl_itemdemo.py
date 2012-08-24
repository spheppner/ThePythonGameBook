# pycrawl_itemdemo
# my very own rogulike game
# because i play far too much dungeon crawl stone soup
# 2012 by Horst JENS   horstjens@gmail.com
# license: gpl3 see http://www.gnu.org/copyleft/gpl.html
# this game is a part of http://ThePythonGameBook.com

# this is a demo where the player (@) runs around in some small rooms.
# the player can pick up and drop items. he also has an inventory
# later on, certain monsters should also be able to pick up at last one item
#
# some ideas were the items are placed vertically:
# each "thing" in a level should have a z coordinate
# z 0 is the floor, some items on it are on z 1
# monsters and players are on z 2
# ( i have to stop myself now and not invent pycraft, made out of blocks in 3 dimensions )
#
# there can be several Items (trap, loot etc. ) on the same x y position
# there can only be one single monster or player at the same x y position ( but several items !)
# there can only be one single floor tile ( wall, empty, shop, ladder, door) at the same x y position

# a dead monster is no longer an instance of the monster class but instead an instance of the item class ( a dead body )
# monsters are placed in the level and are also running around
# monsters have a primitive state machine (moods): if they run around some time, they get tired and sleep for a while
# if a monster runs over a trap too often it dies and drops an monster corpse item


#architecture:

import random



class Game(object):
    """super class, conaining all other stuff"""
    player = None # the player will instance will be stored here
    level = {} # dict with level instances key = levelnumber
    score = 0
    turns = 0
    history = ""
    #            key, x, y # y from top to down, x from left to right
    dirs ={"7":(-1,-1),
                 "4":(-1, 0),
                 "1":(-1, 1),
                 "8":( 0,-1),
                 "5":( 0, 0),
                 "2":( 0, 1),
                 "9":( 1,-1),
                 "6":( 1, 0),
                 "3":( 1, 1)}  # this is a constant
    #            char : [z, short text, long text ], ...
    tiledict = { "X": ["an outer wall", "an outer wall of the level. You can not go there" ] , 
                 "#": ["an inner wall", "an inner wall. You may destroy this wall with the right tools or spells"] , 
                 ".": ["a floor tile", "an empty boring space. There is really nothing here." ], 
                 "d": ["a door", "an (open) door" ],
                 "D": ["a door", "a (closed) door" ],   
                 "<": ["a stair up", "a stair up to the previous level"],
                 ">": ["a stair down", "a stair down to the next deeper level"],
                 "s": ["a shop", "a shop of a friendly merchant"] ,
                 "t": ["a trap", "a dangerous trap !"],
                 "m": ["a dead monster", "a dead monster. Did you kill it?"],
                 "?": ["a heap of loot", "a heap of loot. Feel yourself enriched" ],
                 "b": ["a box", "a box. You wonder what is inside. And if it is trapped"], 
                 ":": ["a single item", "a single item. add one more item and you have a heap of loot"],
                 "@": ["the player", "the player. that is you."],
                 "M": ["a living monster", "a living monster. You can kill it. It can kill you !"],
                 "Z": ["a sleeping monster","a sleeping monster. You can kill it while it sleeps !"]
                }
    output = None # output instance

class Level(object):
    """a representation of the current level (lots of GameObjects)"""
    
    def __init__(self, rawlevel, levelnumber):
        #self.monsterdict = {} # monsters in this level (not player)
        #self.itemdict = {}    # items laying around on this level
        self.levelnumber = levelnumber 
        Game.level[self.levelnumber] = self  # store level instance into game class
        #rawmap is a list of lists of chars
        self.rawmap = list(map(list, rawlevel.split())) # at them moment all stuff
        #print(self.rawmap)
        self.rows = len(self.rawmap)  # width of the level in chars
        self.cols = len(self.rawmap[0]) # height of the level in chars
        # make real level from rawmap
        #self.coords = [(r,c) for r in range(self.rows) for c in ranbe(self.cols)]
        self.pos = {}
        for r in range(self.rows):
            for c in range(self.cols):
                self.pos[c,r] = -1 # not defined game object number # [".", [], None] # ground, itemlist, monster?
        self.monsterkeys = []
        self.itemkeys = []
        self.interpret_rawlevel()
        Game.output = Output(self.rows, self.cols)
        Game.output.drawlevel(self.levelnumber)
        
    
    def interpret_rawlevel(self):
        """generating a 'real'  level info from the rawmap, The rawmap includes traps, walls, monster, player etc. No more random placement needed except for
        generating loot items and single items as indicated in rawmap"""
        for y in range(self.rows):
            for x in range(self.cols):
                rawchar = self.rawmap[y][x]
                if not rawchar in Game.tiledict:
                    raise UserWarning("Bad rawmap char found in rawmap but not in Games.tiledict: %s" % rawchar)
                # create GameObject
                # create Item
                # create Items
                # create Monster
                #print("rawchar", rawchar)
                if rawchar in "dDs#X<>": # not a floor tile but a wall 
                    # create not-floor tile
                    self.pos[(x,y)] = GameObject(x,y,self.levelnumber, rawchar).number
                    #print("non-floor", GameObject.book[self.pos[(x,y)]].char)
                else:
                    # create floor tile
                    self.pos[(x,y)] = GameObject(x,y,self.levelnumber, ".").number
                    #print("floor!")
                if rawchar == "@":
                    if not Game.player:
                        Game.player = Player(x, y, self.levelnumber, "@")
                    else:
                        Game.player.x = x
                        Game.player.y = y
                        Game.player.levelnumber = self.levelnumber
 
                elif rawchar in "MZ": # monster  
                    self.monsterkeys.append(Monster(x,y,self.levelnumber, rawchar).number)
                #elif rawchar == "Z": # sleeping monster
                #    self.monsterkeys.append(Monster(,x,y,self.levelnumber, " sleeping=True).number)    
                elif rawchar in "tbm:": #item        
                    # create Item
                    self.itemkeys.append(Item(x,y,self.levelnumber, rawchar).number)
                elif rawchar == "?": # heap of random items    
                    for a in range(random.randint(2,6)):
                        self.itemkeys.append(Item(x,y,self.levelnumber,":").number)
                
    def pickup(self,x,y):
        ilist = []
        for i in self.itemkeys:
            if GameObject.book[i].x == x and GameObject.book[i].y == y:
                ilist.append(i)
        return ilist
                    
    def __getitem__(self, xy):
        x,y = xy
        return self.pos[(x,y)] # stuff like [ground, itemlist, monster] ?
    
    def __setitem__(self, xy, stuff):
        x,y = xy
        self.pos[(x,y)] = stuff
     

class Output(object):
    """the ascii-map from where the actual output is generated"""
    def __init__(self, rows, cols):
        #print("rows, cols:",rows, cols)
        self.rows = rows
        self.cols = cols
        self.map = [] # self.ground_map = list(map(list, rawlevel.split()))
        #row = cols * "." # create dummy string of empty tiles
        self.map = [["." for x in range(cols)] for y in range(rows)]

        #print("map:", self.map)
    
    def drawlevel(self, levelnumber):
        level = Game.level[levelnumber]
        for y in range(level.rows):
            for x in range(level.cols):
                # ground
                char = GameObject.book[level.pos[(x,y)]].char
                # items
                itemcount = 0
                for i in level.itemkeys:
                    if GameObject.book[i].x == x and GameObject.book[i].y == y:
                        char = GameObject.book[i].char  #overwrite floor with item
                        itemcount += 1
                if itemcount > 1:
                    char = "?"
                # monsters
                for m in level.monsterkeys:
                    if GameObject.book[m].x == x and GameObject.book[m].y == y:
                        char = GameObject.book[m].char  #overwrite floor with item
                # player
                if Game.player.x == x and Game.player.y == y:
                    char = "@"
                #print("y,x",y,x)
                self.map[y][x] = char # set char    
    
    def make_screenstring(self):
        return "\n".join(self)
    
    def __iter__(self):
        return ("".join(row) for row in self.map)

    def __getitem__(self, xy):
        x, y = xy
        return self.map[y][x] # row, col

    def __setitem__(self, xy, char):
        x, y = xy
        self.map[y][x] = char # row, col


class GameObject(object):
    number = 0
    book = {}
    """each obect in the game Monster, Item, Player, Wall has some shared attributes"""
    def __init__(self, x, y, levelnumber, char, **kwargs):
        self.x = x
        self.y = y
        self.levelnumber = levelnumber
        self.number = GameObject.number
        GameObject.number += 1
        GameObject.book[self.number] = self
        self.char = char
        

class Item(GameObject):
    """individual Item with all attributes"""
    def __init__(self, x, y, levelnumber, char, **kwargs):
        GameObject.__init__(self,x,y,levelnumber, char, **kwargs)
        self.shorttext = Game.tiledict[self.char][0]
        if self.char == ":": # single item
            self.longtext = self.generate_text()
        else:
            self.longtext = Game.tiledict[self.char][1]

    def generate_text(self):
        """generate a random description for this item for the very lazy coder"""
        word1 = random.choice(("a big", "a small", "a medium", "an epic", "a handsome","a rotting", "an expensive", "a cheap"))
        word2 = random.choice(("yellow", "green", "blue", "red", "white", "black","rusty", "shiny", "blood-smeared"))
        word3 = random.choice(("ring", "drink", "flower", "wand", "fruit"))
        return " ".join((word1, word2, word3)) # put space between words

class Monster(GameObject):
    """individual Monster"""
    def __init__(self,x,y,levelnumber, char, **kwargs):
        GameObject.__init__(self, x,y,levelnumber, char, **kwargs)
        self.itemkeys = [] # list of of itemkeys that the monster carry
        self.hitpoints = 5
        self.mood = "roam"
        self.energy = random.randint(15,25)
        self.lowenergy = 10
        self.highenergy = 30
        
    def update(self):
        if self.mood == "roam":
            # move around
            self.energy -= 1 # roaming cost energy
            if self.energy < self.lowenergy:
                self.mood = "sleep"
        elif self.mood == "sleep":
            self.energy += 1 # sleeping regains energy
            if self.energy > self.highenergy:
                self.mood = "roam"
        
    
class Player(GameObject):
    """the player"""
    def __init__(self,x,y,levelnumber, char, **kwargs):
        GameObject.__init__(self, x,y,levelnumber, char, **kwargs)
        self.itemkeys = [] # list of itemkeys that the player carrys
        self.hitpoints = 50
        self.msg = ""
        
    def checkmove(self,dx, dy):
        newx = self.x + dx
        newy = self.y + dy
        newgroundcharnumber = Game.level[self.levelnumber].pos[(newx, newy)]
        newgroundchar = GameObject.book[newgroundcharnumber].char
        if newgroundchar in "#X":
            self.msg = "Moving not possible. You can not walk into %s" % Game.tiledict[newgroundchar][0]
            return False
        else:
            return True
        
    def move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy
        self.msg = "Moving (dx: %i dy: %i) sucessfull" % (dx, dy)
    
    def pickup(self):
        foundlist = Game.level[self.levelnumber].pickup(self.x, self.y)
        if len(foundlist) == 0:
            self.msg = "i found no items here to pick up"
        else:
            for f in foundlist:
                self.itemkeys.append(f)
                i = Game.level[self.levelnumber].itemkeys.index(f)
                del Game.level[self.levelnumber].itemkeys[i]
            self.msg = "%i item(s) picked up and added to inventory" % len(foundlist)
    
    def show_inventory(self):
        """returns a big sting with each itemnumber and itemdescription of the player's inventory"""
        if len(self.itemkeys) == 0:
           return "The inventory is empty!"
        t = ""
        for k in self.itemkeys:
            t += str(k)+ " : " + GameObject.book[k].longtext+ "\n"
        return t
    
    def drop(self, itemnumber):
        """drop item with itemnumber on the floor, removing it from inventory and adding it to level"""
        if itemnumber in self.itemkeys:
            # update Item x,y with player x,y
            GameObject.book[itemnumber].x = self.x
            GameObject.book[itemnumber].y = self.y
            Game.level[self.levelnumber].itemkeys.append(itemnumber)
            i = self.itemkeys.index(itemnumber)
            del self.itemkeys[i]
            self.msg = "item dropped"
        else:
            self.msg = "illegal itemnumber. dropping canceled"
    
# allowed moves ?
# monster states ?



#mylevel = """\
#XXXXXX
#X.@M.X
#XXXXXX\
#"""

def main():

    rawlevel ="""\
XXXXXXXXXXXXXXXXXX
X??....?...##.?..X
X....?..:...d....X
Xtb....t..?##...>X
X.<........##..t.X
X..........##t.<.X
X....tt....dd....X
X..........##....X
X#######..####.##X
X#######..####d##X
X..........#....:X
X..b...:...##M@:?X
X.s....?...######X
X.t........##tt.tX
XXXXXXXXXXXXXXXXXX"""
     
     
     
    # init level 1
    ln = 1
    mylevel = Level(rawlevel, ln)
    p = Game.player
    print("output:")
    print(Game.output.make_screenstring())
    gameloop = True
    while gameloop:
        print("press: (numpad key): move (q): quit (p): pickup (d): drop ")
        i = input(">")
        i = i.lower()
        if i == "q":
           gameloop = False
        elif i in Game.dirs.keys():
            dx, dy = Game.dirs[i]
            if p.checkmove(dx, dy):
                p.move(dx,dy)
                Game.output.drawlevel(ln)
                print(Game.output.make_screenstring())
        elif i == "p": #pickup
            p.pickup()
        elif i == "d": # drop
            print(p.show_inventory())
            i = input("enter number to drop or (c) to cancel")
            p.drop(int(i))
        print(p.msg)
    print("game over. bye !")

if __name__ == '__main__':
    main()



## old code , use , move, and delete:

#    def __init__(self, char, **kwargs):
#        for attr in kwargs.keys(): 
#            if attr in self.__dict__:
#                self.__dict__[attr] = kwargs[attr]
#    def showStats(object):
#        """display all stats of an class instance"""
#        for key in object.__dict__:
#            print( key, ":", object.__dict__[key])



