from Robots import *
import Move

class AI(RobotAI):
  def __init__(self):
    self.firedMissileAgo = 0
  def getMove(self, robotstate, worldstate):
    # Get up to speed
    if(robotstate.speed < robotstate.maxspeed):
      return Move.SPEED_UP
    # If just fired missile, evade so don't shoot missile
    if(self.firedMissileAgo < 10):
      self.firedMissileAgo += 1
      return Move.TURN_RIGHT
    # Track missiles and robots in view
    objects = worldstate.objectsInView
    if( len(objects)>0 and ( (objects[0].isARobot and objects[0].colour != robotstate.colour) or objects[0].isAMissile) ):
      targetPos = worldstate.objectsInView[0].relativePosition
      alpha = robotstate.direction.angleBetween(targetPos)
      if(alpha > 0.1):
        return Move.TURN_RIGHT
      elif(alpha < -0.1):
        return Move.TURN_LEFT
      if(robotstate.missilesLeft<=0 or abs(alpha) < 0.05 or objects[0].isAMissile):
        return Move.FIRE_LASER
      else:
        self.firedMissileAgo = 0
        return Move.FIRE_MISSILE
    # Otherwise move randomly
    else:
      i = random.randint(0, 100)
      if(i<30):
        return Move.TURN_LEFT
      elif(i<60):
        return Move.TURN_RIGHT
      else:

        return Move.NONE
