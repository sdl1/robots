import time
import math
from lib.PodSixNet.PodSixNet.Channel import Channel
from lib.PodSixNet.PodSixNet.Server import Server
from Vector import Vec2d
import Robots
import GameWorld
import Move

# The server-side representation of the client ai
class NetworkAI(Robots.RobotAI):
  def __init__(self, channel):
    self.channel = channel
  def getMove(self, robotstate, worldstate):
    move = self.channel.move
    if(move!=Move.RESIGN):
      self.channel.requestMove(robotstate, worldstate)
      self.channel.move = Move.NONE
    return move
  def die(self):
    self.channel.sendChat("You dead sucka!")
    self.channel.Send({"action": "kick", "reason": "dead"})
  def gameOver(self):
    self.channel.sendChat("It's game over.")
    self.channel.Send({"action": "kick", "reason": "game over"})
  def decorateSprite(self, cr):
    cr.set_source_rgb(0.3, 0.3, 0.3)
    cr.move_to(-25, -25)
    cr.set_font_size( cr.device_to_user_distance(10.0, 10.0)[0] )
    cr.show_text(str(self.channel.addr[0]))

def addNetworkedRobot(channel, colour):
  uids = GameWorld.addBots(1, colour, NetworkAI(channel))
  return uids[0]

# The server-side representation of the client channel
class ClientChannel(Channel):
  def __init__(self, conn=None, addr=(), server=None, map=None):
    self.move = Move.NONE
    Channel.__init__(self, conn, addr, server, map)
  def Network(self, data):
    pass
  def Network_chat(self, data):
    print "[client]", data["text"]
  def Network_move(self, data):
    self.move = data["move"]
  def Network_placeRobot(self, data):
    colour = data["colour"] % Robots.Teams.num
    robot_uid = addNetworkedRobot(self, colour)
    print "New robot on " + Robots.Teams.Name[colour] + " team (UID: " + str(robot_uid) + ")"
    self.sendRobotUID(robot_uid)
  def Network_resign(self, data):
    print "Resignation from :" + str(self)
    self.move = Move.RESIGN
  def sendChat(self, text):
    self.Send({"action": "chat", "text": text})
  def requestMove(self, robotstate, worldstate):
    # Send a move request to client
    self.Send({"action": "requestMove", "worldstate": worldstate.pack(), "robotstate": robotstate.pack()})
  def sendRobotUID(self, uid):
    # Tell client the UID of their new robot
    self.Send({"action": "informRobotUID", "uid": uid})

class MyServer(Server):
  channelClass = ClientChannel

  def __init__(self, addr=("127.0.0.1", 12345)):
    Server.__init__(self, localaddr=addr)
    print "Server started on " + addr[0] +  ":" + str(addr[1])
    print "Ctrl-C to exit"

  def Connected(self, channel, addr):
    print 'New connection:', channel
    channel.sendChat("Thanks for connecting.")

if __name__ == "__main__":
  myserver = MyServer()
  while True:
    myserver.Pump()
    time.sleep(0.0001)

