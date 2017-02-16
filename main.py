#!/usr/bin/python
import gtk
import gtk.gdk as gdk
import math
import random
import gobject
import sys
import signal

from Vector import Vec2d
import Sprites
import Robots
import Move
import WorldStates
import Collisions
import Server
from GameWorld import sprites, windowsize, windowloc, worldsize, addBots
import GameWorld
import cairo

if(len(sys.argv)>1):
  bots = int(sys.argv[1])
  addBots(bots)

servaddr = ('', 12345)
if(len(sys.argv)>2):
  port = int(sys.argv[2])
  servaddr = ('', int(port))
server = Server.MyServer(servaddr)

def drawScoreBoard(cr, mwidth=120):
  cr.set_line_width(1)
  cr.set_source_rgb(0.9,0.9,0.9)
  cr.rectangle(0, 0, mwidth, mwidth)
  cr.fill_preserve()
  cr.set_source_rgb(0,0,0)
  cr.stroke()

  team_in_play = [False]*Robots.Teams.num
  num_team_members = [0]*Robots.Teams.num
  for sprite in sprites:
    if isinstance(sprite, Robots.Robot):
      team_in_play[sprite.colour] = True
      num_team_members[sprite.colour] += 1

  cr.set_font_size( cr.device_to_user_distance(18.0, 18.0)[0] )
  teams_done = 0
  for col in range(0, Robots.Teams.num):
    if team_in_play[col]:
      cr.move_to(mwidth/2-15, teams_done*20+20)
      rgb = Robots.Teams.RGB[col]
      cr.set_source_rgb(rgb[0], rgb[1], rgb[2])
      t = str(num_team_members[col])
      cr.show_text(t)
      teams_done += 1

def drawMiniMap(cr, mwidth=120):
  cr.set_line_width(1)
  cr.set_source_rgb(0.9,0.9,0.9)
  cr.rectangle(0, 0, mwidth, mwidth)
  cr.fill_preserve()
  cr.set_source_rgb(0,0,0)
  cr.stroke()
  scale = mwidth / float(worldsize[0]) # TODO non-square worlds
  cr.scale(scale, scale)
  drawSprites(cr, simple=True)
  cr.transform( GameWorld.worldToWindowTransform() )
  cr.set_line_width( cr.device_to_user_distance(1.0, 1.0)[0] )
  cr.set_source_rgb(1,0,0)
  cr.rectangle(0, 0, GameWorld.windowsize[0], GameWorld.windowsize[1])
  cr.stroke()
  cr.transform( GameWorld.windowToWorldTransform() )
  cr.scale(1.0/scale, 1.0/scale)

def drawSprites(cr, simple=False):
  for sprite in sprites:
    cr.translate(sprite.position[0], sprite.position[1])
    sprite.draw(cr, simple)
    cr.translate(-sprite.position[0], -sprite.position[1])

# Draw the circles and update their positions.
def expose(*args):
  cr = darea.window.cairo_create()
  cr.set_source_rgb(.7,.7,.7)
  cr.paint()
  cr.transform(GameWorld.windowToWorldTransform())
  cr.rectangle(0, 0, worldsize[0], worldsize[1])
  cr.set_source_rgb(.85,.85,.85)
  cr.fill_preserve()
  cr.set_line_width( cr.device_to_user_distance(3.0, 3.0)[0] )
  cr.set_source_rgb(.3,.3,.3)
  cr.stroke()
  drawSprites(cr, simple=(GameWorld.totalZoom()<0.2))
  cr.transform(GameWorld.worldToWindowTransform())

  mmwidth = 120
  cr.translate(windowsize[0]-mmwidth-10, windowsize[1]-mmwidth-10)
  drawMiniMap(cr, mmwidth)
  cr.translate(-(windowsize[0]-mmwidth-10), -(windowsize[1]-mmwidth-10))

  cr.translate(windowsize[0]-mmwidth-10, windowsize[1]-2*mmwidth-20)
  drawScoreBoard(cr, mmwidth)
  cr.translate(-(windowsize[0]-mmwidth-10), -(windowsize[1]-2*mmwidth-20))

  newsprites = []
  doneCollisions = set()
  for sprite in sprites:
    worldstate = WorldStates.WorldState();
    for othersprite in sprites:
      if othersprite==sprite:
        continue
      relpos = othersprite.position - sprite.position
      #TODO see edge of object...
      if(sprite.canSeeRelative(relpos)):
        worldstate.addObjectInView( WorldStates.objectInView(othersprite, relpos) )

    for othersprite in sprites:
      if othersprite==sprite:
        continue
      collisionPair = frozenset([sprite, othersprite])
      if(collisionPair in doneCollisions):
        continue
      doneCollisions.add(collisionPair)
      relpos = othersprite.position - sprite.position
      # Check for collisions
      if(relpos.norm() < sprite.boundingradius + othersprite.boundingradius):
        newsprite = Collisions.collide(sprite, othersprite)
        # Maybe produced a new sprite
        if(newsprite != None):
          print "Collision of " + str(sprite) + " " + str(othersprite) + " produced " + str(newsprite)
          newsprites.append(newsprite)
      # Maybe this sprite got killed
      breakloop = False
      if(sprite.hitpoints<=0):
        print str(sprite) + " was killed during its own collision step"
        sprite.die()
        sprites.remove(sprite)
        breakloop = True
      # Maybe other sprite got killed
      if(othersprite.hitpoints<=0):
        print str(othersprite) + " was killed during " + str(sprite) + "'s collision step"
        othersprite.die()
        sprites.remove(othersprite)
      if(breakloop): break

    move = sprite.getMove(worldstate);
    if(move==Move.RESIGN):
      # Don't call sprites.die() here. We assume the sprite has already killed itself.
      sprites.remove(sprite)
      continue
    elif(move==Move.SPEED_UP):
      if(sprite.speed + 1 <= sprite.maxspeed):
        sprite.speed += 1
    elif(move==Move.SLOW_DOWN):
      if(sprite.speed - 1 >= 0):
        sprite.speed -= 1
    elif(move==Move.TURN_RIGHT):
      sprite.direction.rotateDegrees(2)
    elif(move==Move.TURN_LEFT):
      sprite.direction.rotateDegrees(-2)
    elif(move==Move.FIRE_MISSILE):
      missile = Sprites.Missile(sprite.position + (sprite.boundingradius + Sprites.Missile.boundingradius + 10)*sprite.direction, 10, sprite.direction)
      newsprites.append(missile)
    elif(move==Move.FIRE_LASER):
      # Speed penalty
      #sprite.speed = 0
      laser = Sprites.Laser(sprite.position + (sprite.boundingradius + Sprites.Missile.boundingradius + 25+1)*sprite.direction, 30, sprite.direction)
      newsprites.append(laser)
    elif(move>=Move.SIGNAL and move<Move.SIGNAL + Move.Signals.num):
      sprite.signal = move - Move.SIGNAL

    sprite.position += sprite.speed * sprite.direction
    if sprite.position[0] > worldsize[0] or sprite.position[0] < 0:
        sprite.direction[0] *= -1
    if sprite.position[1] > worldsize[1] or sprite.position[1] < 0:
        sprite.direction[1] *= -1
    if(sprite.position[0] > worldsize[0]):
      sprite.position[0] = worldsize[0]-1
    if(sprite.position[0] < 0):
      sprite.position[0] = 1
    if(sprite.position[1] > worldsize[1]):
      sprite.position[1] = worldsize[1]-1
    if(sprite.position[1] < 0):
      sprite.position[1] = 1

  # Check if any dead
  for sprite in sprites:
    if(sprite.lifetime>=0):
      sprite.age += 1
      if(sprite.age > sprite.lifetime):
        sprite.hitpoints = 0
    if(sprite.hitpoints<=0):
      sprite.die()
      sprites.remove(sprite)

  # Add newsprites
  sprites.extend(newsprites)

  # Pump server
  server.Pump()


# Self-evident?
def timeout():
  darea.queue_draw()
  return True

def quit(arg=None):
  print "Quitting"
  for sprite in sprites:
    sprite.gameOver()
  server.Pump()
  gtk.main_quit()

def quit_handler(handler, frame):
  quit()

def motion_notify_event(widget, event):
  x = event.x
  y = event.y
  state = event.state

  if state & gtk.gdk.BUTTON1_MASK:
    if not motion_notify_event.button_down:
      # Start dragging
      motion_notify_event.startCoords = x,y
      motion_notify_event.button_down = True
      return True
    motion_notify_event.endCoords = x,y
    windowloc[0] -= (motion_notify_event.endCoords[0] - motion_notify_event.startCoords[0])*GameWorld.invscale
    windowloc[1] -= (motion_notify_event.endCoords[1] - motion_notify_event.startCoords[1])*GameWorld.invscale
    motion_notify_event.startCoords = x,y
  else:
    motion_notify_event.button_down = False

  if state & gtk.gdk.BUTTON2_MASK:
    mwidth = 120
    #x -= 0.5*windowsize[0]/float(worldsize[0]) * mwidth
    #y -= 0.5*windowsize[1]/float(worldsize[1]) * mwidth
    #TODO proper dragging of the red square
    windowloc[0] = (x - (windowsize[0]-mwidth)) / float(mwidth) * worldsize[0]
    windowloc[1] = (y - (windowsize[1]-mwidth)) / float(mwidth) * worldsize[1]
    return True

  return True

motion_notify_event.button_down = False
motion_notify_event.startCoords = 0,0
motion_notify_event.endCoords = 0,0

def configure_event(widget, event):
  newrect = darea.get_allocation()
  windowsize[0] = newrect[2]
  windowsize[1] = newrect[3]
  return True

def scroll_event(widget, event):
  x = event.x
  y = event.y
  if event.direction == gtk.gdk.SCROLL_UP:
    GameWorld.zoomIn((x,y))
  elif event.direction == gtk.gdk.SCROLL_DOWN:
    GameWorld.zoomOut((x,y))
    GameWorld.moveWindowTowardsWorldCoords(darea.window.cairo_create(), (GameWorld.worldsize[0]/2.0, GameWorld.worldsize[1]/2.0))
  return True


# Catch SIGINT
signal.signal(signal.SIGINT, quit_handler)

# Initialize the window.
window = gtk.Window()
window.resize(windowsize[0], windowsize[1])
window.connect("destroy", quit)
darea = gtk.DrawingArea()
darea.connect("configure-event", configure_event)
darea.connect("expose-event", expose)
darea.connect("motion_notify_event", motion_notify_event)
darea.connect("scroll_event", scroll_event)
darea.set_events(gtk.gdk.EXPOSURE_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.SCROLL_MASK)
window.add(darea)
window.show_all()



# Self-evident?
#gobject.idle_add(timeout)
gobject.timeout_add(25, timeout)
gtk.main()

