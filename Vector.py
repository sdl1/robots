import math

class Vec2d:
  x = []
  def __init__(self, x, y):
    self.x = [x, y]

  # Square brackets
  def __getitem__(self, i):
    return self.x[i]
  def __setitem__(self, key, value):
    self.x[key] = value
  def __str__(self):
    return "[" + str(self.x[0]) + ", " + str(self.x[1]) + "]"

  def copy(self):
    return Vec2d(self.x[0], self.x[1])

  def __add__(self, other):
    return Vec2d(self.x[0] + other.x[0], self.x[1] + other.x[1])
  def __sub__(self, other):
    return Vec2d(self.x[0] - other.x[0], self.x[1] - other.x[1])
  def __mul__(self, other):
    return Vec2d(self.x[0]*other, self.x[1]*other)
  def __rmul__(self, other):
    return Vec2d(self.x[0]*other, self.x[1]*other)
  def __div__(self, other):
    return Vec2d(self.x[0]/other, self.x[1]/other)
  def __neg__(self):
    return Vec2d(-self.x[0], -self.x[1])

  def norm(self):
    return math.sqrt( self.x[0]*self.x[0] + self.x[1]*self.x[1] )
  def length(self):
    return self.norm()
  def normalise(self):
    invNorm = 1 / self.norm()
    self.x[0] *= invNorm
    self.x[1] *= invNorm
    return self
  def unit(self):
    return self / self.norm()

  def dot(self, other):
    return self.x[0]*other.x[0] + self.x[1]*other.x[1]

  def rotate(self, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    x = self.x[0]
    y = self.x[1]
    self.x = [ c*x - s*y, s*x + c*y ]
    return self
  def rotateDegrees(self, angle):
    return self.rotate(angle * math.pi/180)

  # atan(other) - atan(self)
  def angleBetween(self, other):
    return math.atan2(other[1], other[0]) - math.atan2(self[1], self[0])

  # Shortest distance from this point to line given by two points
  def shortestDistanceToLine(self, p1, p2):
    p0 = self
    x0 = p0[0]
    y0 = p0[1]
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    return abs( (x2 - x1)*(y1 - y0) - (x1 - x0)*(y2 - y1) ) / (p2 - p1).norm()

ex = Vec2d(1, 0)
ey = Vec2d(0, 1)




