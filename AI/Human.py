from Robots import *
import Move

import Tkinter as tk
root = tk.Tk()
move = -4
def keypress(event):
    global move
    if event.keysym == 'Escape':
        move = Move.RESIGN
        root.destroy()
    x = event.char
    if x == "w":
        move = Move.SPEED_UP
    elif x == "a":
        move = Move.TURN_LEFT
    elif x == "s":
        move = Move.SLOW_DOWN
    elif x == "d":
        move = Move.TURN_RIGHT
    elif x == " ":
        move = Move.FIRE_LASER
    elif x == "m":
        move = Move.FIRE_MISSILE
    else:
        print x
    root.quit()

class AI(RobotAI):
    def __init__(self):
        print "Press a key (Escape key to exit):"
        root.bind_all('<Key>', keypress)
        # don't show the tk window
        #root.withdraw()
        #root.mainloop()
    def getMove(self, robotstate, worldstate):
        root.mainloop()
        return move
# respond to a key without the need to press enter
