#include <iostream>
#include <vector>
#include <HFO.hpp>
#include <cstdlib>
#include <thread>
#include "SarsaAgent.h"
#include "CMAC.h"

// Before running this program, first Start HFO server:
// $./bin/HFO --offense-agents numAgents

CMAC **fa;
SarsaAgent **sa;
int basePort = 6000;
int numAgents = 0;

// Variables used
int numEpisodes = 10000;
int numF;
int numA;
double learnR = 0.1;
double eps = 0.001;
char **ldWtFile;
char **svWtFile;
double *range;
double *min;
double *res;
double discFac = 1;

double getReward(int status) {
  double reward;
  if (status==hfo::GOAL) reward = 1;
  else if (status==hfo::CAPTURED_BY_DEFENSE) reward = -1;
  else if (status==hfo::OUT_OF_BOUNDS) reward = -0.8;
  else reward = 0;
  return reward;
}

void offenseAgent(int num) {
  hfo::HFOEnvironment hfo;
  hfo::status_t status;
  hfo::Action a;
  double state[numF];
  int action = -1;
  double reward;
  hfo.connectToAgentServer(basePort + num, hfo::HIGH_LEVEL_FEATURE_SET);
  for (int episode=0; episode < numEpisodes; episode++) {
    status = hfo::IN_GAME;
    action = -1;
    while (status == hfo::IN_GAME) {
        const std::vector<float>& state_vec = hfo.getState();
        //If has ball
        if(state_vec[5] == 1){
          if(action != -1) {
            reward = getReward(status);
            sa[num]->update(state, action, reward, discFac);
          }
          int stateIndex = 0;
          for(int i=0; i<state_vec.size(); i++){
            //Ignore some features
            if(i==5) continue; // Can kick
            int temp = 9+3*(numAgents-1) - i;
            if(temp > 0 && temp%3==0) continue;// Uniform numbers
            state[stateIndex] = state_vec[i];
            stateIndex++;
          }
          action = sa[num]->selectAction(state);
          switch(action) {
            case 0: a={hfo::SHOOT, 0.0, 0.0};
                    break;
            case 1: a={hfo::DRIBBLE, 0.0, 0.0};
                    break;
            default: a={hfo::PASS,
                        state_vec[9+3*(numAgents-1) + (action-1)*3],
                        0.0};
          }

        } else {
            a = {hfo::MOVE, 0.0, 0.0};
        }
        status = hfo.act(a);
    }
    if(action != -1) {
      reward = getReward(status);
      sa[num]->update(state, action, reward, discFac);
      sa[num]->endEpisode();
    }
  }
}

int main(int argc, char **argv) {
  int suffix = 0;
  switch (argc) {
	case 4: suffix = atoi(argv[3]);
	case 3: basePort = atoi(argv[2]);
	case 2: numAgents = atoi(argv[1]);
  }
  std::thread agentThreads[numAgents];
  fa = new CMAC *[numAgents];
  sa = new SarsaAgent *[numAgents];
  ldWtFile = new char *[numAgents];
  svWtFile = new char *[numAgents];
  //Initialise all parameters
  numF = 9 + 5*(numAgents-1);
  numA = 2 + (numAgents-1);
  range = new double[numF];
  min = new double[numF];
  res = new double[numF];
  for(int i=0;i<numF;i++) {
    min[i] = -1;
    range[i] = 2;
    res[i] = 0.01;
  }
  for(int i=0; i<numAgents; i++) {
    fa[i] = new CMAC(numF, numA, range, min, res);
    std::string s = "weights_" + std::to_string(i) +
                    "_" + std::to_string(numAgents) +
                    "_" + std::to_string(suffix);
    svWtFile[i] = &s[0u];
    ldWtFile[i] = &s[0u];
    sa[i] = new SarsaAgent(numF, numA, learnR, eps,
                           fa[i], ldWtFile[i], svWtFile[i]);
  }
  for (int agent = 0; agent < numAgents; agent++) {
    agentThreads[agent] = std::thread(offenseAgent, agent);
  }
  for (int agent = 0; agent < numAgents; agent++) {
    agentThreads[agent].join();
  }
  return 0;
}
