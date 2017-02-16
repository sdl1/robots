from Robots import *
import Move

class AI(RobotAI):
  def getMove(self, robotstate, worldstate):
      return Move.TURN_RIGHT
