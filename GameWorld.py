from Vector import Vec2d, ex
import Robots
import AI.ExampleAI
import AI.DumbAI
import random
import math
import cairo

# The world size
worldsize = [600 * 5, 600 * 5]
# The window size.
windowsize = [600, 600]
# Location of top left corner of window
windowloc = [0, 0]
# Scale factor - less than 1 means zoom out
scale = 1
invscale = 1.0/scale

scalingFixedPoint = (0, 0)

sprites = []

zoomFactor = 1.1

zoomMatrix = cairo.Matrix(xx = 1.0, yx = 0.0, xy = 0.0, yy = 1.0, x0 = 0.0, y0 = 0.0)

def setScale(s):
  global scale, invscale
  scale = float(s)
  invscale = 1.0/s

def multiplyScaleBy(m):
  global scale, invscale
  scale *= float(m)
  invscale = 1.0/scale

def totalZoom():
  xx, yx, xy, yy, x0, y0 = zoomMatrix
  return abs(xx)

def zoomIn(x):
  global zoomFactor, windowloc, windowsize, scalingFixedPoint, zoomMatrix, scale, invscale
  # The more zoomed in we are (the higher the scale), the less we should zoom)
  realZoomFactor = 1 + 0.1*zoomFactor/scale
  multiplyScaleBy(realZoomFactor)
  newZoomMatrix = cairo.Matrix()

  newZoomMatrix.translate(x[0], x[1])
  newZoomMatrix.scale(realZoomFactor, realZoomFactor)
  newZoomMatrix.translate(-x[0], -x[1])

  zoomMatrix = zoomMatrix.multiply(newZoomMatrix)

def zoomOut(x):
  global zoomFactor, scalingFixedPoint, scale, invscale, zoomMatrix
  realZoomFactor = 1.0/1.1 #1.0/zoomFactor
  multiplyScaleBy(realZoomFactor)
  newZoomMatrix = cairo.Matrix()
  newZoomMatrix.translate(x[0], x[1])
  newZoomMatrix.scale(realZoomFactor, realZoomFactor)
  newZoomMatrix.translate(-x[0], -x[1])

  zoomMatrix = zoomMatrix.multiply(newZoomMatrix)


def windowToWorldTransform():
  global zoomMatrix, windowloc
  t = cairo.Matrix()
  t = t.multiply(zoomMatrix)

  tmp = cairo.Matrix()
  tmp.translate(-windowloc[0], -windowloc[1])

  t = tmp.multiply(t)

  return t

def worldToWindowTransform():
  t = windowToWorldTransform()
  t.invert()
  return t

def worldCoordsToWindowCoords(cr, x):
  # Find world centre in window coords
  matrix = cr.get_matrix()
  cr.set_matrix(windowToWorldTransform())
  wc = cr.user_to_device( x[0], x[1] )
  cr.set_matrix(matrix)
  return wc

def moveWindowTowardsWorldCoords(cr, x):
  x = worldCoordsToWindowCoords(cr, x)
  global windowloc, windowsize
  windowcentre = (windowsize[0]/2, windowsize[1]/2)
  dx = (x[0] - windowcentre[0], x[1] - windowcentre[1])
  windowloc[0] += 0.02*dx[0]
  windowloc[1] += 0.02*dx[1]

def getSpawnPoint(colour=0):
  # Spawn locations
  spawn = [ Vec2d(worldsize[0]/5, worldsize[1]/5), Vec2d(worldsize[0]/5, 4*worldsize[1]/5), Vec2d(4*worldsize[0]/5, worldsize[1]/5), Vec2d(4*worldsize[0]/5, 4*worldsize[1]/5) ]
  return spawn[ colour%4 ] + Vec2d(  (1-2*random.random())*worldsize[0]/5, (1-2*random.random())*worldsize[1]/5)

def addBots(num, col=Robots.Teams.RED, ai=AI.ExampleAI.AI()):
  maxspeed = 2
  hp = 100
  uids = []
  for i in range(num):
    r = Robots.Robot(col, getSpawnPoint(col), maxspeed, ex.rotate(random.random()*2*math.pi), hp, ai)
    sprites.append(r)
    uids.append(r.UID)
  return uids


