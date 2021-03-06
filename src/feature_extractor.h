#ifndef FEATURE_EXTRACTOR_H
#define FEATURE_EXTRACTOR_H

#include <rcsc/player/player_agent.h>
#include <vector>

typedef std::pair<float, float> OpenAngle;

class FeatureExtractor {
public:
  FeatureExtractor();
  virtual ~FeatureExtractor();

  // Updated the state features stored in feature_vec
  virtual const std::vector<float>& ExtractFeatures(const rcsc::WorldModel& wm) = 0;

  // Record the current state
  void LogFeatures();

  // How many features are there?
  inline int getNumFeatures() { return numFeatures; }

public:
  // Determines if a player is a part of the HFO game or is inactive.
  static bool valid(const rcsc::PlayerObject& player);

  // Returns the angle (in radians) from self to a given point
  static float angleToPoint(const rcsc::Vector2D &self,
                            const rcsc::Vector2D &point);

  // Returns the angle (in radians) and distance from self to a given point
  static void angleDistToPoint(const rcsc::Vector2D &self,
                               const rcsc::Vector2D &point,
                               float &ang, float &dist);

  // Returns the angle between three points: Example opponent, self,
  // goal center
  static float angleBetween3Points(const rcsc::Vector2D &point1,
                                   const rcsc::Vector2D &centerPoint,
                                   const rcsc::Vector2D &point2);

  // Find the opponent closest to the given point. Returns the
  // distance and angle (in radians) from point to the closest
  // opponent.
  static void calcClosestOpp(const rcsc::WorldModel &wm,
                             const rcsc::Vector2D &point,
                             float &ang, float &dist);

  // Returns the largest open (in terms of opponents) angle (radians)
  // from self to the slice defined by [angBot, angTop].
  static float calcLargestOpenAngle(const rcsc::WorldModel &wm,
                                    const rcsc::Vector2D &self,
                                    float angTop, float angBot, float maxDist);

  // Returns the angle (in radians) corresponding to largest open shot
  // on the goal.
  static float calcLargestGoalAngle(const rcsc::WorldModel &wm,
                                    const rcsc::Vector2D &self);

  // Returns the largest open angle from self to a given teammate's
  // position.
  static float calcLargestTeammateAngle(const rcsc::WorldModel &wm,
                                        const rcsc::Vector2D &self,
                                        const rcsc::Vector2D &teammate);

  // Helper function to split the open angles by the opponent angles
  static void splitAngles(std::vector<OpenAngle> &openAngles,
                          float oppAngleBottom,
                          float oppAngleTop);

protected:
  // Encodes an angle feature as the sin and cosine of that angle,
  // effectively transforming a single angle into two features.
  void addAngFeature(const rcsc::AngleDeg& ang);

  // Encodes a proximity feature which is defined by a distance as
  // well as a maximum possible distance, which acts as a
  // normalizer. Encodes the distance as [0-far, 1-close]. Ignores
  // distances greater than maxDist or less than 0.
  void addDistFeature(float dist, float maxDist);

  // Add the angle and distance to the landmark to the feature_vec
  void addLandmarkFeatures(const rcsc::Vector2D& landmark,
                           const rcsc::Vector2D& self_pos,
                           const rcsc::AngleDeg& self_ang);

  // Add features corresponding to another player.
  void addPlayerFeatures(rcsc::PlayerObject& player,
                         const rcsc::Vector2D& self_pos,
                         const rcsc::AngleDeg& self_ang);

  // Add a feature without normalizing
  void addFeature(float val);

  // Add a feature and normalize to the range [FEAT_MIN, FEAT_MAX]
  void addNormFeature(float val, float min_val, float max_val);

  // Checks that features are in the range of FEAT_MIN - FEAT_MAX
  void checkFeatures();

protected:
  const static float RAD_T_DEG = 180.0 / M_PI;
  const static float ALLOWED_PITCH_FRAC = 0.33;

  int featIndx;
  std::vector<float> feature_vec; // Contains the current features
  const static float FEAT_MIN = -1;
  const static float FEAT_MAX = 1;
  const static float FEAT_INVALID = -2;

  int numFeatures; // Total number of features
  // Observed values of some parameters.
  const static float observedSelfSpeedMax   = 0.46;
  const static float observedPlayerSpeedMax = 0.75;
  const static float observedStaminaMax     = 8000.;
  const static float observedBallSpeedMax   = 5.0;
  float maxHFORadius; // Maximum possible distance in HFO playable region
  // Useful measures defined by the Server Parameters
  float pitchLength, pitchWidth, pitchHalfLength, pitchHalfWidth,
    goalHalfWidth, penaltyAreaLength, penaltyAreaWidth;
};

#endif // FEATURE_EXTRACTOR_H
