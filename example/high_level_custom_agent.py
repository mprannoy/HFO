#!/usr/bin/env python
# encoding: utf-8

# First Start the server: $> bin/start.py
import random, threading, argparse
try:
  from hfo import *
except:
  print 'Failed to import hfo. To install hfo, in the HFO directory'\
    ' run: \"pip install .\"'
  exit()

params = {'SHT_DST':1, 'SHT_ANG':-0.8,
          'PASS_ANG':-0.66, 'DRIB_DST':-0.8}

def get_num_of_teammates(state):
  """Returns the number of teammates present

  Assumes at least one opponent is present
  """
  return((len(state) - 10) / 5)

def can_shoot(goal_dist, goal_angle):
  """Returns True if if player can have a good shot at goal"""
  if goal_dist < params['SHT_DST'] and goal_angle > params['SHT_ANG']:
    return True
  else:
    return False

def has_better_pos(dist_to_op, goal_angle, pass_angle, curr_goal_angle):
  """Returns True if teammate is in a better attacking position"""
  if curr_goal_angle > goal_angle:
    return False
  if pass_angle < params['PASS_ANG']:
    return False
  return True

def can_dribble(dist_to_op):
  if dist_to_op > params['DRIB_DST']:
    return True
  else:
    return False

def get_action(state):
  """Returns the action to be taken by the agent"""
  num_teammates = get_num_of_teammates(state)
  goal_dist = state[6]
  goal_op_angle = state[8]
  if can_shoot(goal_dist, goal_op_angle):
    return (HFO_Actions.SHOOT, 0, 0)
  for i in xrange(num_teammates):
    if has_better_pos(dist_to_op = state[10 + num_teammates + i],
                      goal_angle = state[9 + i],
                      pass_angle = state[10 + 2*num_teammates + i],
                      curr_goal_angle = goal_op_angle):
      return (HFO_Actions.PASS, 0, 0)
  if can_dribble(dist_to_op = state[8 + num_teammates + 1]):
    return (HFO_Actions.DRIBBLE, 0, 0)
  # If nothing can be done pass
  return (HFO_Actions.PASS, 0, 0)
    

def play_hfo(num):
  """ Method called by a thread to play 5 games of HFO """
  hfo_env = hfo.HFOEnvironment()
  hfo_env.connectToAgentServer(6000 + num, HFO_Features.HIGH_LEVEL_FEATURE_SET)
  try:
    for episode in xrange(10):
      status = HFO_Status.IN_GAME
      while status == HFO_Status.IN_GAME:
        state = hfo_env.getState()
        if state[5] == 1: # state[5] is 1 when player has the ball 
         tmp = get_action(state)
         print tmp
         status = hfo_env.act(tmp)
        else:
          status = hfo_env.act((HFO_Actions.MOVE, 0, 0))
  except Exception as e:
    print e
  finally:
    print "Agent " + str(num) + " exiting." 
    hfo_env.cleanup()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('num_agents', type=int, help='Number of agents to start. '\
                      'NOTE: server must be started with this number of agents.')
  args = parser.parse_args()
  for i in xrange(args.num_agents):
    t = threading.Thread(target=play_hfo, args=(i,))
    t.start()

if __name__ == '__main__':
  main()
