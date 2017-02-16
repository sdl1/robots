import Move
import Vector

import math
import random
import cairo

class UniqueID:
  uid = random.getrandbits(32)
  @staticmethod
  def getUID():
    UniqueID.uid += 1
    return UniqueID.uid


class Sprite:
  colour = None
  lifetime = None
  age = None
  hitpoints = None
  position = None
  speed = None
  maxspeed = None
  direction = None
  viewangle = 0
  viewdistance = None
  boundingradius = None;
  def __init__(self, pos, maxspeed, dirn, hp, r, lifetime=-1):
    self.UID = UniqueID.getUID()
    self.colour = -1
    self.position = pos.copy()
    self.speed = 0
    self.maxspeed = maxspeed
    self.direction = dirn.copy()
    self.direction.normalise()
    self.hitpoints = hp
    self.boundingradius = r
    self.age = 0
    self.lifetime = lifetime
  def die(self):
    pass
  def gameOver(self):
    pass
  def getMove(self, worldstate):
    return Move.NONE
  def canSeeRelative(self, relpos):
    inRange = ( relpos.norm() < self.viewdistance )
    angleBetween = self.direction.angleBetween(relpos)
    inFieldOfView = ( abs(angleBetween) < self.viewangle*math.pi/180 )
    #return ( inRange and inFieldOfView )
    return inRange 
  # Angle between direction and ex, in (-pi, pi)
  def directionAngle(self):
    theta = math.atan2(self.direction[1], self.direction[0])
    return theta
  def draw(self, cr, simple=False):
    cr.set_line_width(4)
    cr.set_source_rgb(0, 0, 1)

    cr.move_to(0, 0)
    cr.rel_line_to(20*self.direction[0], 20*self.direction[1])
    cr.stroke()

    cr.arc(0, 0, 8, 0, 2 * math.pi)
    cr.stroke_preserve()
    cr.set_source_rgb(1, 1, 1)
    cr.fill()
  def drawViewCone(self, cr):
    #theta = self.directionAngle()
    #cr.rotate(theta)
    #alpha = self.viewangle * math.pi / 180
    #cr.set_source_rgba(0, 0, 1, 0.05)
    #cr.move_to(0, 0)
    #cr.rel_line_to(self.viewdistance * math.cos(alpha), -self.viewdistance * math.sin(alpha))
    #cr.arc(0, 0, self.viewdistance, -alpha, alpha)
    #cr.line_to(0, 0)
    #cr.fill()
    #cr.rotate(-theta)
    dash = [1, 3]
    #cr.set_dash(dash);
    cr.set_line_width(1)
    cr.set_source_rgb(0.6, 0.6, 1)
    cr.arc(0, 0, self.viewdistance, 0, 2*math.pi)
    cr.stroke()
    #cr.set_dash([1,0])


class Missile(Sprite):
  viewangle = 0
  viewdistance = 9999
  damageDone = 9999
  boundingradius = 8
  def __init__(self, pos, maxspeed, dirn):
    hp = 100
    Sprite.__init__(self, pos, maxspeed, dirn, hp, Missile.boundingradius)
  def getMove(self, worldstate):
    return Move.SPEED_UP
  def draw(self, cr, simple=False):
    cr.set_source_rgb(0, 0, 0)
    if simple:
      r = cr.device_to_user_distance(0.3*self.boundingradius, 1.0)[0]
      cr.arc(0, 0, r, 0, 2*math.pi)
      cr.fill()
      return
    cr.set_line_width(2)
    #cr.move_to(0, 0)
    #cr.arc(0, 0, self.boundingradius, 0, 2 * math.pi)
    r = self.boundingradius
    theta = self.directionAngle()
    cr.rotate(theta)
    cr.move_to(-r, -r/2)
    cr.line_to(-r, r/2)
    cr.line_to(r, 0)
    cr.close_path()
    cr.stroke_preserve()
    cr.set_source_rgb(0.7, 0, 0)
    cr.fill()
    cr.rotate(-theta)

class Laser(Sprite):
  viewangle = 0
  viewdistance = 9999
  damageDone = 5
  damageDepreciation = 0.5
  boundingradius = 25
  beamwidth = 6
  def __init__(self, pos, maxspeed, dirn):
    hp = 100000
    lifetime = self.damageDone / self.damageDepreciation
    Sprite.__init__(self, pos, maxspeed, dirn, hp, Laser.boundingradius, lifetime)
    self.speed = self.maxspeed
  def getMove(self, worldstate):
    self.damageDone = max(self.damageDone - self.damageDepreciation, 0)
    return Move.NONE
  def draw(self, cr, simple=False):
    theta = self.directionAngle()
    if simple:
      #r = 100
      #cr.set_source_rgb(1, 0.4, 0)
      #cr.rotate(theta)
      #w = cr.device_to_user_distance(0.3*self.beamwidth, 1.0)[0]
      #cr.set_line_width(w)
      #cr.move_to(0, 0)
      #cr.rel_line_to(r, 0)
      #cr.stroke()
      #cr.rotate(-theta)
      return

    cr.rotate(theta)
    r = self.boundingradius

    #linear = cairo.LinearGradient(0, -self.beamwidth/2, 0, self.beamwidth/2)
    #linear.add_color_stop_rgba(0.0,  1, 0.4, 0.2, 0.7)
    #linear.add_color_stop_rgba(0.5,  1, 1, 1, 1)
    #linear.add_color_stop_rgba(1.0,  1, 0.4, 0.2, 0.7)

  
    #cr.set_source_rgba(1, 0.4, 0, 0.2)
    cr.set_source_rgba(1, 0.4, 0, self.damageDone/float(self.lifetime))
    #cr.set_source(linear)
    cr.set_line_width(self.beamwidth)
    cr.move_to(-r/2.0, 0)
    cr.rel_line_to(r/2.0, 0)
    cr.stroke()

    cr.rotate(-theta)

class Explosion(Sprite):
  def __init__(self, pos):
    maxspeed = 0
    dirn = Vector.Vec2d(1,0)
    hp = 9999999
    boundingradius = 0
    lifetime = 15 #25
    Sprite.__init__(self, pos, maxspeed, dirn, hp, boundingradius, lifetime)
  def draw(self, cr, simple=False):
    frac = self.age/float(self.lifetime)
    intensity = 1.0 - frac
    #intensity = intensity**(3)
    #r = 10 * (self.age ** 1.4)
    r = 10*self.age

    colour = [1 - 0.7*frac, 0.5 - 1.5*frac, 0.5 - 3*frac]
    colour[0] = max(colour[0], 0)
    colour[1] = max(colour[1], 0)
    colour[2] = max(colour[2], 0)

    #cr.move_to(0, 0)

    #radial = cairo.RadialGradient(0, 0, r/2,   0, 0, r)
    #radial.add_color_stop_rgba(0,  1.0, 1.0, 1.0, intensity)
    #radial.add_color_stop_rgba(1,  colour[0], colour[1], colour[2], intensity)
    #cr.set_source(radial)


    if simple:
      #r = cr.device_to_user_distance(r*0.05, 1.0)[0]
      #cr.set_source_rgb(0.6, 0, 0.6)
      #cr.arc(0, 0, r, 0, 2*math.pi)
      #cr.fill()
      return

    cr.set_source_rgba(colour[0], colour[1], colour[2], intensity)
    cr.set_line_width(10)
    cr.move_to(r, 0)
    cr.arc(0, 0, r, 0, 2*math.pi)

    #cr.fill()
    cr.stroke()

class MinorExplosion(Explosion):
  def __init__(self, pos):
    Explosion.__init__(self, pos)
    self.lifetime = 5





