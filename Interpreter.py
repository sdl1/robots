#!/usr/bin/python
from lib.PodSixNet.PodSixNet.Connection import connection, ConnectionListener
from lib.PodSixNet.PodSixNet.Channel import Channel
import time
import WorldStates
import Robots
import Move
import sys
import signal
import socket
import json
from Robots import *
import Vector

# Connects to remote robots server.
# Connected internally to InterpreterServer.
class InterpreterClient(ConnectionListener):
  def __init__(self, interpreterServer=None, addr=("127.0.0.1", 12345)):
    self.interpreterServer = interpreterServer
    self.Connect(addr)
    print "Interpreter client connecting to robots server on " + addr[0] +  ":" + str(addr[1])
    print "Ctrl-C to exit"
    signal.signal(signal.SIGINT, self.resign)

  def Network(self, data):
    pass
  def Network_chat(self, data):
    print "[robots server]", data["text"]
  # Called when server requests a move
  def Network_requestMove(self, data):
    worldstatepacked = data["worldstate"]
    robotstatepacked = data["robotstate"]
    robotstate = Robots.RobotState.unpack( robotstatepacked )
    worldstate = WorldStates.WorldState.unpack( worldstatepacked )
    # Request move from InterpreterServer (blocking)
    move = self.interpreterServer.requestMove(robotstate, worldstate)
    self.sendMove(move)
    if(move==Move.RESIGN):
      print "Client resigned."
      self.interpreterServer.hasUserClient = False
      self.interpreterServer.CloseConnection()
  def Network_kick(self, data):
    reason = data["reason"]
    print "Kicked (" + reason + ")"
    # Tell our user client to die
    if(self.interpreterServer.hasUserClient):
      self.interpreterServer.SendToUserClient("die")
      self.interpreterServer.hasUserClient = False
      connection.Pump()
      self.interpreterServer.CloseConnection()
    # Kill self
    exit(0)
  def Network_informRobotUID(self, data):
    print "Got robot UID", data["uid"]

  # Send a move to the robots server
  def sendMove(self, move):
    connection.Send({"action": "move", "move": move})
    connection.Pump()
    self.Pump()
  # Send my robot to the server
  def sendRobot(self, colour):
    connection.Send({"action": "placeRobot", "colour": colour%Robots.Teams.num})
    self.Pump()
    connection.Pump()
  # Send my resignation (and wait for kick message)
  def resign(self, handler, frame):
    # Kill user client
    if(self.interpreterServer.hasUserClient):
      self.interpreterServer.SendToUserClient("die")
      self.interpreterServer.hasUserClient = False
      self.interpreterServer.CloseConnection()
    print "Sending resignation."
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
      # Get a new client
      self.interpreterServer.WaitForConnection()
      while self.interpreterServer.hasUserClient:
        # Pump self, i.e. send/receive to robots server. If robots server requests move, we will delegate request to interpreter server.
        # Otherwise, we don't do anything with the interpreter server.
        self.Pump()
        connection.Pump()
        time.sleep(0.0001)

# This will listen on local machine for
# the user client to connect to.
class InterpreterServer():
  def __init__(self, interpreterClient=None, addr=("127.0.0.1", 23456)):
    self.addr = addr
    self.interpreterClient = interpreterClient
    self.BUFFER_SIZE = 1024
    self.hasUserClient = False
    print 'Interpreter server starting on ' + str(addr)
  def WaitForConnection(self):
    # Wait for user client to connect
    print 'Interpreter server waiting for user client to connect...'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(self.addr)
    s.listen(1)
    self.conn, addr = s.accept()
    self.hasUserClient = True
    print "Interpreter server got connection from user client. Waiting for team colour..."
    colour = self.ReceiveFromUserClient() % Robots.Teams.num
    print "Joining " + Robots.Teams.Name[colour] + " team."
    self.interpreterClient.sendRobot(colour)
  def CloseConnection(self):
    self.conn.close()
  def ReceiveFromUserClient(self):
    data = self.conn.recv(self.BUFFER_SIZE)
    if not data: return
    return int(data)
  def SendToUserClient(self, data):
    # Send a string (char buffer) over TCP
    self.conn.send(data)
  def requestMove(self, robotstate, worldstate):
    # Our interpreter client has requested a move.
    # We first encode the world state in JSON and send to the user client
    state = (robotstate, worldstate)
    state_JSON = self.MyEncoder().encode(state)
    self.SendToUserClient(state_JSON + "\n")
    # Then wait for user client to respond
    move = int(self.ReceiveFromUserClient())
    return move
  class MyEncoder(json.JSONEncoder):
    def default(self, o):
      if isinstance(o, WorldStates.WorldState):
        return o.__dict__
      if isinstance(o, RobotState):
        return o.__dict__
      if isinstance(o, Vector.Vec2d):
        return o.x
      if isinstance(o, WorldStates.objectInView):
        return o.__dict__
      return json.JSONEncoder.default(self, o)

if __name__ == "__main__":
  servaddr = ('', 23456)
  clientaddr = ('localhost', 12345)
  
  iclient = InterpreterClient(clientaddr)
  iserver = InterpreterServer(iclient, servaddr)
  iclient.interpreterServer = iserver

  iclient.Loop()


  


