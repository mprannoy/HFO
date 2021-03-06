#ifndef __HFO_HPP__
#define __HFO_HPP__

#include <string>
#include <vector>

// For descriptions of the different feature sets see
// https://github.com/mhauskn/HFO/blob/master/doc/manual.pdf
enum feature_set_t
{
  LOW_LEVEL_FEATURE_SET,
  HIGH_LEVEL_FEATURE_SET
};

// The actions available to the agent
enum action_t
{
  DASH,    // [Low-Level] Dash(power, relative_direction)
  TURN,    // [Low-Level] Turn(direction)
  TACKLE,  // [Low-Level] Tackle(direction)
  KICK,    // [Low-Level] Kick(power, direction)
  MOVE,    // [High-Level] Move(): Reposition player according to strategy
  SHOOT,   // [High-Level] Shoot(): Shoot the ball
  PASS,    // [High-Level] Pass(): Pass to the most open teammate
  DRIBBLE, // [High-Level] Dribble(): Offensive dribble
  QUIT     // Special action to quit the game
};

// The current status of the HFO game
enum hfo_status_t
{
  IN_GAME,
  GOAL,
  CAPTURED_BY_DEFENSE,
  OUT_OF_BOUNDS,
  OUT_OF_TIME
};

struct Action {
  action_t action;
  float arg1;
  float arg2;
};

// Configuration of the HFO domain including the team names and player
// numbers for each team. This can be populated by ParseHFOConfig().
struct HFO_Config {
  std::string offense_team_name;
  std::string defense_team_name;
  int num_offense; // Number of offensive players
  int num_defense; // Number of defensive players
  std::vector<int> offense_nums; // Offensive player numbers
  std::vector<int> defense_nums; // Defensive player numbers
};


class HFOEnvironment {
 public:
  HFOEnvironment();
  ~HFOEnvironment();

  // Parse a message sent from Trainer to construct an HFO config.
  // Returns a bool indicating if the struct was correctly parsed.
  static bool ParseHFOConfig(const std::string& message, HFO_Config& config);

  // Connect to the server that controls the agent on the specified port.
  void connectToAgentServer(int server_port=6000,
                            feature_set_t feature_set=HIGH_LEVEL_FEATURE_SET);

  // Get the current state of the domain. Returns a reference to feature_vec.
  const std::vector<float>& getState();

  // Take an action and recieve the resulting game status
  hfo_status_t act(Action action);

 protected:
  int numFeatures; // The number of features in this domain
  int sockfd; // Socket file desriptor for connection to agent server
  std::vector<float> feature_vec; // Holds the features

  // Handshake with the agent server to ensure data is being correctly
  // passed. Also sets the number of features to expect.
  virtual void handshakeAgentServer(feature_set_t feature_set);
};

#endif
