#include <iostream>
#include <vector>
#include <HFO.hpp>
#include <cstdlib>

using namespace std;

// First Start the server: $> bin/start.py

int main() {
  // Create the HFO environment
  HFOEnvironment hfo;
  // Connect the agent's server on the given port with the given
  // feature set.  See possible feature sets in src/HFO.hpp.
  hfo.connectToAgentServer(6000, LOW_LEVEL_FEATURE_SET);
  // Play 5 episodes
  for (int episode=0; episode<5; episode++) {
    hfo_status_t status = IN_GAME;
    while (status == IN_GAME) {
      // Grab the vector of state features for the current state
      const std::vector<float>& feature_vec = hfo.getState();
      // Create a dash action
      Action a = {DASH, 0., 0.};
      // Perform the dash and recieve the current game status
      status = hfo.act(a);
    }
    // Check what the outcome of the episode was
    cout << "Episode " << episode << " ended with status: ";
    switch (status) {
      case GOAL:
        cout << "goal" << endl;
        break;
      case CAPTURED_BY_DEFENSE:
        cout << "captured by defense" << endl;
        break;
      case OUT_OF_BOUNDS:
        cout << "out of bounds" << endl;
        break;
      case OUT_OF_TIME:
        cout << "out of time" << endl;
        break;
      default:
        cout << "Unknown status " << status << endl;
        exit(1);
    }
  }
};
