from Sprites import Sprite, Missile
from Vector import Vec2d
import Move
import math
import random

class Teams:
  BLUE = 0
  RED = 1
  GREEN = 2
  ORANGE = 3
  Name = [ "BLUE", "RED", "GREEN", "ORANGE" ]
  RGB = [ [0,0,1], [1,0,0], [0,0.6,0], [1,0.5,0] ]
  num = len(Name)

class RobotState:
  def __init__(self, robot=None):
    if(robot==None):
      self.position = Vec2d(0,0)
      self.direction = Vec2d(0,0)
      return
    self.UID = robot.UID
    self.colour = robot.colour
    self.position = robot.position.copy()
    self.direction = robot.direction.copy()
    self.speed = robot.speed
    self.maxspeed = robot.maxspeed
    self.hitpoints = robot.hitpoints
    self.missilesLeft = robot.missilesLeft
    self.signal = robot.signal
  def pack(self):
    return [ self.UID, self.colour, self.position.x, self.direction.x, self.speed, self.maxspeed, self.hitpoints, self.missilesLeft, self.signal ]
  @staticmethod
  def unpack(packed):
    ret = RobotState()
    ret.UID = packed[0]
    ret.colour = packed[1]
    ret.position.x = packed[2]
    ret.direction.x = packed[3]
    ret.speed = packed[4]
    ret.maxspeed = packed[5]
    ret.hitpoints = packed[6]
    ret.missilesLeft = packed[7]
    ret.signal = packed[8]
    return ret

class Robot(Sprite):
  colour = 0
  viewangle = 180
  viewdistance = 900
  staticMissile = Missile(Vec2d(0,0), 0, Vec2d(1,0))
  def __init__(self, col, pos, maxspeed, dirn, hp, ai):
    self.signal = Move.Signals.NONE
    self.missilesLeft = 1
    self.laser_cooldown = 0
    self.laser_max_cooldown = 2
    self.laser_overheated = False
    rad = 8
    self.ai = ai
    Sprite.__init__(self, pos, maxspeed, dirn, hp, rad)
    self.colour = col
  def die(self):
    self.ai.die()
  def gameOver(self):
    self.ai.gameOver()
  def draw(self, cr, simple=False):
    cr.set_line_width(4)
    rgb = Teams.RGB[self.colour]
    cr.set_source_rgb(rgb[0], rgb[1], rgb[2])

    if simple:
      r = cr.device_to_user_distance(0.3*self.boundingradius, 1.0)[0]
      cr.arc(0, 0, r, 0, 2*math.pi)
      cr.fill()
      return


    cr.move_to(0, 0)
    cr.rel_line_to(20*self.direction[0], 20*self.direction[1])
    cr.stroke()

    cr.arc(0, 0, self.boundingradius, 0, 2 * math.pi)
    cr.stroke_preserve()
    health = self.hitpoints / float(100)
    cr.set_source_rgb(health, health, health)
    cr.fill()

    cr.set_source_rgb(0, 0, 1)
    theta = self.directionAngle()
    cr.rotate(theta)
    cr.scale(0.5, 0.5)
    for i in range(0, self.missilesLeft):
      #cr.arc(-2 + 6*i, self.boundingradius*2, 2, 0, 2 * math.pi)
      #cr.fill()
      cr.translate(0, self.boundingradius*4 + 15*i)
      Robot.staticMissile.draw(cr)
      cr.translate(0, -self.boundingradius*4 - 15*i)
    if not self.signal==Move.Signals.NONE:
      rgb = Move.Signals.RGB[self.signal]
      cr.set_source_rgb(rgb[0], rgb[1], rgb[2])
      cr.translate(0, -self.boundingradius*5)
      cr.arc(0, 0, 11, 0, 2 * math.pi)
      cr.fill()
      cr.translate(0, self.boundingradius*5)
    cr.scale(2.0, 2.0)
    cr.rotate(-theta)

    #Sprite.drawViewCone(self, cr)

    self.ai.decorateSprite(cr)
  def getMove(self, worldstate):
    robotstate = RobotState(self)
    move = self.ai.getMove(robotstate, worldstate)
    if(move == Move.FIRE_MISSILE):
      if(self.missilesLeft>0):
        self.missilesLeft -= 1
        return move
      else:
        move = Move.NONE
    if(move == Move.FIRE_LASER):
      if(self.laser_overheated):
        self.laser_cooldown -= 1
        if(self.laser_cooldown==0): self.laser_overheated = False
        move = Move.NONE
      else:
        self.laser_cooldown += 1
        if(self.laser_cooldown==self.laser_max_cooldown): self.laser_overheated = True
        return move
    return move


class RobotAI:
  def __init__(self):
    return
  def getMove(self, robotstate, worldstate):
    return Move.NONE
  def die(self):
    pass
  def gameOver(self):
    pass
  def decorateSprite(self, cr):
    pass

