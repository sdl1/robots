from Sprites import *
from Robots import Robot

def collide(sprite1, sprite2):

  # Laser - Laser
  if(isinstance(sprite1, Laser) and isinstance(sprite2, Laser)):
    return

  # HACK - if laser, check if actually colliding
  #if(isinstance(sprite2, Laser) and not isinstance(sprite1, Laser)):
  #  return collide(sprite2, sprite1)
  #if(isinstance(sprite1, Laser)):
  #  # Shortest distance to line
  #  d = sprite2.position.shortestDistanceToLine(sprite1.position, sprite1.position + sprite1.direction)
  #  # Angle between rel position and beam direction
  #  relpos = sprite2.position - sprite1.position
  #  costheta = relpos.dot(sprite1.direction)
  #  if(d>Laser.beamwidth/2+sprite2.boundingradius or costheta<=0):
  #    return

  # Missile - Laser
  if(isinstance(sprite1, Missile) and isinstance(sprite2, Laser)):
    return collide(sprite2, sprite1)
  # Laser - Missile
  if(isinstance(sprite1, Laser) and isinstance(sprite2, Missile)):
    sprite2.hitpoints = 0
    sprite1.age = sprite1.lifetime
    return Explosion(sprite2.position)

  # Robot - Missile
  if(isinstance(sprite1, Robot) and isinstance(sprite2, Missile)):
    return collide(sprite2, sprite1)

  # Missile - Robot
  if(isinstance(sprite1, Missile) and isinstance(sprite2, Robot)):
    sprite1.hitpoints = 0
    sprite2.hitpoints -= sprite1.damageDone
    if(sprite2.hitpoints <= 0):
      return Explosion(sprite2.position)
    return

  # Robot - Robot
  if(isinstance(sprite1, Robot) and isinstance(sprite2, Robot)):
    if(sprite1.speed==0 and sprite2.speed==0):
      print "Zero-speed collision"
      sprite1.position += 2*(sprite1.boundingradius + sprite2.boundingradius)*sprite1.direction
      return
    if(sprite1.speed==0):
      collide(sprite2, sprite1)
      return
    relpos = (sprite2.position - sprite1.position).normalise()
    projection = sprite1.direction.dot(relpos)
    sprite1.direction -= 2 * projection * relpos
    sprite1.direction.normalise()
    sprite1.position = sprite2.position.copy()
    sprite1.position += sprite1.direction * (sprite1.boundingradius + sprite2.boundingradius + 1)
    #sprite1.hitpoints -= 25
    #sprite2.hitpoints -= 25
    return

  # Explosion - anything
  if(isinstance(sprite1, Explosion) or isinstance(sprite2, Explosion)):
    return

  # Missile - Missile
  if(isinstance(sprite1, Missile) and isinstance(sprite2, Missile)):
    sprite1.hitpoints = 0
    sprite2.hitpoints = 0
    return Explosion(sprite1.position)

  # Robot - Laser
  if(isinstance(sprite1, Robot) and isinstance(sprite2, Laser)):
    return collide(sprite2, sprite1)

  # Laser - Robot
  if(isinstance(sprite1, Laser) and isinstance(sprite2, Robot)):
    sprite2.hitpoints -= sprite1.damageDone
    sprite1.damageDone = max(sprite1.damageDone - 3, 0)
    if(sprite2.hitpoints <= 0):
      return Explosion(sprite2.position)
    return #MinorExplosion(sprite2.position)

  print "Unknown collision between " + str(sprite1.__class__) + " and " + str(sprite2.__class__)



