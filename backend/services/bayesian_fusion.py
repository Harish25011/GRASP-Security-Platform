"""
Bayesian Fusion Engine - probabilistic combination of agent scores.

Replaces simple averaging with Bayesian posterior estimation:
  P(attack | all_evidence) = Bayesian update over each agent's score.
  
Each agent provides:
  - score: P(attack | this_agent's_evidence)
  - confidence: reliability weight for this agent
"""
import numpy as np
import logging

logger = logging.getLogger("bayesian_fusion")


def bayesian_fuse(agent_scores: dict, agent_confidences: dict,
                  prior: float = 0.1) -> float:
    """
    Bayesian fusion of agent scores using log-odds update.

    Args:
        agent_scores: {agent_name: risk_score} where score in [0, 1]
        agent_confidences: {agent_name: confidence} where confidence in [0, 1]
        prior: P(attack) prior probability (default 10%)

    Returns:
        posterior: P(attack | all evidence) in [0, 1]
    """
    # Start with prior log-odds
    prior = max(0.001, min(0.999, prior))
    log_odds = np.log(prior / (1 - prior))

    for agent, score in agent_scores.items():
        confidence = agent_confidences.get(agent, 0.5)

        # Skip unreliable or zero-information agents
        if confidence < 0.1 or score == 0.0:
            continue

        # Clamp score to avoid log(0) or log(inf)
        score = max(0.001, min(0.999, score))

        # Compute the likelihood ratio weighted by confidence
        likelihood_ratio = score / (1 - score)
        log_odds += np.log(likelihood_ratio) * confidence

    # Convert back to probability
    posterior = 1 / (1 + np.exp(-log_odds))
    return float(min(1.0, max(0.0, posterior)))


def compute_ensemble_risk(swarm_result: dict) -> dict:
    """
    Compute ensemble risk score using multiple fusion methods.

    Returns a dict with:
      - avg_score: simple average
      - max_score: max agent score
      - bayesian_score: Bayesian fusion
      - weighted_avg: confidence-weighted average
      - ensemble_score: final blended score
    """
    scores = swarm_result.get("scores", {})
    confidences = swarm_result.get("confidences", {})

    if not scores:
        return {
            "avg_score": 0.0,
            "max_score": 0.0,
            "bayesian_score": 0.0,
            "weighted_avg": 0.0,
            "ensemble_score": 0.0,
        }

    # Method 1: Simple average
    avg_score = sum(scores.values()) / max(len(scores), 1)

    # Method 2: Max score
    max_score = max(scores.values())

    # Method 3: Bayesian fusion
    bayesian_score = bayesian_fuse(scores, confidences, prior=0.1)

    # Method 4: Confidence-weighted average
    total_conf = sum(confidences.values())
    if total_conf > 0:
        weighted_avg = sum(
            scores[a] * confidences.get(a, 0.5) for a in scores
        ) / total_conf
    else:
        weighted_avg = avg_score

    # Final ensemble: blend of methods
    # Weight: Bayesian 40%, Weighted-Avg 30%, Max 20%, Avg 10%
    ensemble_score = (
        bayesian_score * 0.40 +
        weighted_avg * 0.30 +
        max_score * 0.20 +
        avg_score * 0.10
    )

    return {
        "avg_score": round(avg_score, 4),
        "max_score": round(max_score, 4),
        "bayesian_score": round(bayesian_score, 4),
        "weighted_avg": round(weighted_avg, 4),
        "ensemble_score": round(ensemble_score, 4),
    }
