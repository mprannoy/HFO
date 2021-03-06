#!/usr/bin/env python
# encoding: utf-8

import subprocess, os, time, numpy, sys
from signal import SIGKILL

# Global list of all/essential running processes
processes, necProcesses = [], []
# Command to run the rcssserver. Edit as needed.
SERVER_CMD = 'rcssserver'
# Command to run the monitor. Edit as needed.
MONITOR_CMD = 'soccerwindow2'

def getAgentDirCmd(binary_dir, teamname, server_port=6000, coach_port=6002,
                   logDir='log', record=False):
  """ Returns the team name, command, and directory to run a team. """
  cmd = 'start.sh -t %s -p %i -P %i --log-dir %s'%(teamname, server_port,
                                                   coach_port, logDir)
  if record:
    cmd += ' --record'
  cmd = os.path.join(binary_dir, cmd)
  return teamname, cmd

def launch(cmd, necessary=True, supressOutput=True, name='Unknown'):
  """Launch a process.

  Appends to list of processes and (optionally) necProcesses if
  necessary flag is True.

  Returns: The launched process.

  """
  kwargs = {}
  if supressOutput:
    kwargs = {'stdout':open('/dev/null','w'),'stderr':open('/dev/null','w')}
  p = subprocess.Popen(cmd.split(' '),shell=False,**kwargs)
  processes.append(p)
  if necessary:
    necProcesses.append([p,name])
  return p

def main(args, team1='left', team2='right', rng=numpy.random.RandomState()):
  """Sets up the teams, launches the server and monitor, starts the
  trainer.
  """
  if not os.path.exists(args.logDir):
    os.makedirs(args.logDir)
  num_agents   = args.offenseAgents + args.defenseAgents
  binary_dir   = os.path.dirname(os.path.realpath(__file__))
  server_port  = args.port + num_agents
  coach_port   = args.port + num_agents + 1
  olcoach_port = args.port + num_agents + 2
  serverOptions = ' server::port=%i server::coach_port=%i ' \
                  'server::olcoach_port=%i server::coach=1 ' \
                  'server::game_logging=%i server::text_logging=%i ' \
                  'server::game_log_dir=%s server::text_log_dir=%s '\
                  'server::synch_mode=%i ' \
                  'server::fullstate_l=%i server::fullstate_r=%i' \
                  %(server_port, coach_port, olcoach_port,
                    args.logging, args.logging,
                    args.logDir, args.logDir,
                    args.sync,
                    args.fullstate, args.fullstate)
  team1, team1Cmd = getAgentDirCmd(binary_dir, team1, server_port, coach_port,
                                   args.logDir, args.record)
  team2, team2Cmd = getAgentDirCmd(binary_dir, team2, server_port, coach_port,
                                   args.logDir, args.record)
  try:
    # Launch the Server
    server = launch(SERVER_CMD + serverOptions, name='server')
    time.sleep(0.2)
    assert server.poll() is None,\
      '[start.py] Failed to launch Server with command: \"%s\"' \
      %(SERVER_CMD + serverOptions)
    if not args.headless:
      monitorOptions = ' --port=%i'%(server_port)
      launch(MONITOR_CMD + monitorOptions, name='monitor')
    # Launch the Trainer
    from Trainer import Trainer
    trainer = Trainer(args=args, rng=rng, server_port=server_port,
                      coach_port=coach_port)
    trainer.initComm()
    # Start Team1
    launch(team1Cmd,False)
    trainer.waitOnTeam(True) # wait to make sure of team order
    # Start Team2
    launch(team2Cmd,False)
    trainer.waitOnTeam(False)
    # Make sure all players are connected
    trainer.checkIfAllPlayersConnected()
    trainer.setTeams()
    # Run HFO
    trainer.run(necProcesses)
  except KeyboardInterrupt:
    print '[start.py] Exiting for CTRL-C'
  finally:
    print '[start.py] Cleaning up server and other processes'
    for p in processes:
      try:
        p.send_signal(SIGKILL)
      except:
        pass
      time.sleep(0.1)

def parseArgs():
  import argparse
  p = argparse.ArgumentParser(description='Start Half Field Offense.')
  p.add_argument('--headless', dest='headless', action='store_true',
                 help='Run without a monitor')
  p.add_argument('--trials', dest='numTrials', type=int, default=-1,
                 help='Number of trials to run')
  p.add_argument('--frames', dest='numFrames', type=int, default=-1,
                 help='Number of frames to run for')
  p.add_argument('--frames-per-trial', dest='maxFramesPerTrial', type=int,
                 default=1000, help='Max number of frames per trial. '\
                 'Negative values mean unlimited.')
  p.add_argument('--offense-agents', dest='offenseAgents', type=int, default=0,
                 help='Number of offensive agents')
  p.add_argument('--defense-agents', dest='defenseAgents', type=int, default=0,
                 help='Number of defensive agents')
  p.add_argument('--offense-npcs', dest='offenseNPCs', type=int, default=0,
                 help='Number of offensive uncontrolled players')
  p.add_argument('--defense-npcs', dest='defenseNPCs', type=int, default=0,
                 help='Number of defensive uncontrolled players')
  p.add_argument('--no-sync', dest='sync', action='store_false', default=True,
                 help='Run server in non-sync mode')
  p.add_argument('--port', dest='port', type=int, default=6000,
                 help='Agent server\'s port. rcssserver, coach, and ol_coach'\
                 ' will be incrementally allocated the following ports.')
  p.add_argument('--no-logging', dest='logging', action='store_false',
                 default=True, help='Disable rcssserver logging.')
  p.add_argument('--log-dir', dest='logDir', default='log/',
                 help='Directory to store logs.')
  p.add_argument('--record', dest='record', action='store_true',
                 help='Record logs of states and actions.')
  p.add_argument('--agent-on-ball', dest='agent_on_ball', action='store_true',
                 help='Agent starts with the ball.')
  p.add_argument('--fullstate', dest='fullstate', action='store_true',
                 help='Server provides full-state information to agents.')
  args = p.parse_args()
  assert args.offenseAgents + args.offenseNPCs in xrange(0, 11), \
    'Invalid number of offensive players: (choose from [0,10])'
  assert args.defenseAgents + args.defenseNPCs in xrange(0, 12), \
    'Invalid number of defensive players: (choose from [0,11])'
  return args

if __name__ == '__main__':
  main(parseArgs())
