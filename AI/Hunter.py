from Robots import *
import Move

class AI(RobotAI):
  def __init__(self):
    self.firedMissileAgo = 0

  def steerTowards(self, robotstate, relpos):
    alpha = robotstate.direction.angleBetween(relpos)
    if(alpha > 0.0):
      return Move.TURN_LEFT
    else:
      return Move.TURN_RIGHT
  def steerAway(self, robotstate, relpos):
    alpha = robotstate.direction.angleBetween(relpos)
    if(alpha > 0.0):
      return Move.TURN_RIGHT
    else:
      return Move.TURN_LEFT

  def getMove(self, robotstate, worldstate):

    # Get up to speed
    if(robotstate.speed < robotstate.maxspeed):
      return Move.SPEED_UP

    # If just fired missile, evade so don't shoot missile
    if(self.firedMissileAgo < 20):
      self.firedMissileAgo += 1
      return Move.TURN_RIGHT

    objects = worldstate.objectsInView

    # Friendly robots in view
    friends = [r for r in objects if (r.isARobot and r.colour==robotstate.colour)]
    # Enemy robots in view
    enemies = [r for r in objects if (r.isARobot and r.colour!=robotstate.colour)]
    # Missiles in view
    missiles = [r for r in objects if r.isAMissile]

    # If friend directly in front and close, nudge left
    if(len(friends)>0):
      friendangles = [ robotstate.direction.angleBetween(f.relativePosition) for f in friends if f.relativePosition.length()<60]
      critangles = [a for a in friendangles if abs(a)<0.2]
      if(len(critangles)>0):
        if critangles[0]>0:
          return Move.TURN_LEFT
        else:
          return Move.TURN_RIGHT



    # If friend in view signalling red, signal green and go towards him
    redfriends = [r for r in friends if r.signal==Move.Signals.RED]
    if len(redfriends)>0 and len(enemies)==0:
      if robotstate.signal!=Move.Signals.GREEN: return Move.SIGNAL_GREEN
      return self.steerTowards(robotstate, redfriends[0].relativePosition)

    # Turn off signal if no enemies or red friends in view
    if len(enemies)==0 and len(redfriends)==0 and robotstate.signal!=Move.Signals.NONE: return Move.SIGNAL_NONE

    # If friend in view signalling green, go towards him
    greenfriends = [r for r in friends if r.signal==Move.Signals.GREEN]
    if len(greenfriends)>0 and len(enemies)==0:
      return self.steerTowards(robotstate, greenfriends[0].relativePosition)

    # Signal red iff enemy in view
    if len(enemies)!=0 and robotstate.signal!=Move.Signals.RED: return Move.SIGNAL_RED


    # Flock
    if(len(friends)>0 and len(enemies)==0):
      # Min distance to a friend
      minfriend = None
      mindist = 999999
      for f in friends:
        if(f.relativePosition.norm() < mindist):
          minfriend = f
          mindist = f.relativePosition.norm()
      # Separation
      if(mindist<50):
        return self.steerAway(robotstate, f.relativePosition)
      # Average heading of friends
      heading = Vec2d(0,0)
      for f in friends:
        heading += f.direction
      heading.normalise()
      # Average position of friends
      relposition = Vec2d(0,0)
      for f in friends:
        relposition += f.relativePosition

      if(random.random()<0.5):
        # Alignment
        return self.steerTowards(robotstate, heading)
      else:
        # Cohesion
        return self.steerTowards(robotstate, relposition)


    # Track missiles and robots in view
    # TODO track missiles
    if( len(enemies)>0 or len(missiles)>0 ):
      # Prioritise enemies
      if(len(enemies)>0):
        target = enemies[0]
        for e in enemies:
          if(e.relativePosition.length()<target.relativePosition.length()):
            target = e
      else:
        target = missiles[0]

      targetPos = target.relativePosition
      # Track target
      alpha = robotstate.direction.angleBetween(targetPos)
      if(alpha > 0.05):
        return Move.TURN_RIGHT
      elif(alpha < -0.05):
        return Move.TURN_LEFT

      # Target far away
      if(targetPos.length()>400):
        return Move.NONE

      # Fire
      if(robotstate.missilesLeft<=0 or target.isAMissile):
        return Move.FIRE_LASER
      else:
        self.firedMissileAgo = 0
        return Move.FIRE_MISSILE
    # Nothing in view. Move randomly
    else:
      i = random.randint(0, 100)
      if(i<30):
        return Move.TURN_LEFT
      elif(i<60):
        return Move.TURN_RIGHT
      else:

        return Move.NONE
