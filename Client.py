#!/usr/bin/python
from lib.PodSixNet.PodSixNet.Connection import connection, ConnectionListener
import time
import WorldStates
import Robots
import Move
import sys
import signal
import getopt

class Client(ConnectionListener):
  def __init__(self, ai, colour, addr=("127.0.0.1", 12345), verbose=True):
    self.ai = ai
    self.colour = colour
    self.verbose = verbose
    self.Connect(addr)
    self.speak("Client connecting to " + addr[0] +  ":" + str(addr[1]))
    self.speak("Ctrl-C to exit")
    self.sendRobot()
    signal.signal(signal.SIGINT, self.resign)

  def speak(self, text):
    if self.verbose:
      print "[client]", text

  def Network(self, data):
    pass
  def Network_chat(self, data):
    if self.verbose: print "[server]", data["text"]
  # Called when server requests a move
  def Network_requestMove(self, data):
    worldstatepacked = data["worldstate"]
    robotstatepacked = data["robotstate"]
    robotstate = Robots.RobotState.unpack( robotstatepacked )
    worldstate = WorldStates.WorldState.unpack( worldstatepacked )
    move = self.ai.getMove(robotstate, worldstate)
    self.sendMove(move)
    if move==Move.RESIGN:
        time.sleep(0.1)
        sys.exit(0)
  # Called when dead / game over
  def Network_kick(self, data):
    self.speak("Got kicked (" + data["reason"] + ")")
    sys.exit(0)
  def Network_informRobotUID(self, data):
    self.speak("Got robot UID " + str(data["uid"]))


  # Send a move to the server
  def sendMove(self, move):
    connection.Send({"action": "move", "move": move})
    connection.Pump()
    self.Pump()
  # Send my robot to the server
  def sendRobot(self):
    connection.Send({"action": "placeRobot", "colour": self.colour})
    self.Pump()
    connection.Pump()
  # Send my resignation (and wait for kick message)
  def resign(self, handler, frame):
    self.speak("Sending resignation.")
    connection.Send({"action": "resign"})
    self.Pump()
    connection.Pump()
    # Sleep for a small amount of time
    # to allow server to process request,
    # so it doesn't try to write to closed connection
    time.sleep(0.1)
    sys.exit(0)

  def Loop(self):
    while True:
      self.Pump()
      connection.Pump()
      time.sleep(0.0001)

# Get around __import__ only importing top-level module
def my_import(name):
  mod = __import__(name)
  components = name.split('.')
  for comp in components[1:]:
    mod = getattr(mod, comp)
  return mod

def usage():
    print "Usage: " + sys.argv[0] + " [-a AIname, --ai=AIname] [-t team, --team=team] [-s host:port, --server=host:port]"

if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hva:t:s:", ["help", "ai=", "team=", "server="])
  except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
  aiName = "ExampleAI"
  verbose = False
  team = 0
  server = "localhost:12345"
  for o, a in opts:
    if o == "-v":
      verbose = True
    elif o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-a", "--ai"):
      aiName = a
    elif o in ("-t", "--team"):
      team = int(a) % Robots.Teams.num
    elif o in ("-s", "--server"):
      server = a
    else:
      assert False, "unhandled option"

  aiString = "AI." + aiName
  aiModule = my_import(aiString)
  ai = aiModule.AI()

  host, port = server.split(":")
  addr = (host, int(port))

  print "Using AI module", aiModule
  print "Joining " + Robots.Teams.Name[team] + " team on " + server
  
  client = Client(ai, team, addr, verbose)
  client.Loop()



