from Robots import Robot
from Sprites import Missile
import Vector

class objectInView:
  def __init__(self, sprite, relpos):
    self.relativePosition = relpos
    self.colour = -1
    if sprite != None:
      self.colour = sprite.colour
      self.direction = sprite.direction
      self.isARobot = isinstance(sprite, Robot)
      self.isAMissile = isinstance(sprite, Missile)
      self.signal = 0
      if self.isARobot:
        self.signal = sprite.signal
    else:
      self.direction = Vector.Vec2d(0,0)
  def pack(self):
    return [ self.colour, self.direction.x, self.relativePosition.x, self.isARobot, self.isAMissile, self.signal ]
  @staticmethod
  def unpack(packed):
    ret = objectInView(None, Vector.Vec2d(0,0))
    ret.colour = packed[0]
    ret.direction.x = packed[1]
    ret.relativePosition.x = packed[2]
    ret.isARobot = packed[3]
    ret.isAMissile = packed[4]
    ret.signal = packed[5]
    return ret

# Object representing the view a robot has of the world
class WorldState:
  objectsInView = []
  def __init__(self):
    self.objectsInView = []
  def addObjectInView(self, ob):
    self.objectsInView.append(ob)
  def pack(self):
    ret = []
    for o in self.objectsInView:
      ret.append( o.pack() )
    return ret
  @staticmethod
  def unpack(packed):
    ret = WorldState()
    for po in packed:
      ret.addObjectInView( objectInView.unpack(po) )
    return ret





