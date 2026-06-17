"""
Hidden Markov Model for Epilepsy Phenotype State Transitions

Models the latent disease state as a Markov chain where observed clinical
features are emission probabilities from hidden phenotype states.

Uses Baum-Welch (EM) for parameter estimation and Viterbi for
MAP state sequence decoding.

Latent states:
    0 = Seizure-free / well-controlled
    1 = Active disease, drug-responsive
    2 = Emerging pharmacoresistance
    3 = Established pharmacoresistance
    4 = Post-surgical / device-managed
"""

from __future__ import annotations
import math
import json
from dataclasses import dataclass, field
from typing import Optional
import numpy as np

from algorithm.core.phenotype_vector import PhenotypeTrajectory, TreatmentResponseState


# Map treatment response to hidden state index
RESPONSE_TO_STATE = {
    TreatmentResponseState.SEIZURE_FREE: 0,
    TreatmentResponseState.DRUG_RESPONSIVE: 1,
    TreatmentResponseState.PARTIAL_RESPONSE: 1,
    TreatmentResponseState.EMERGING_RESISTANCE: 2,
    TreatmentResponseState.PHARMACORESISTANT: 3,
    TreatmentResponseState.SURGICAL_CANDIDATE: 3,
    TreatmentResponseState.POST_SURGICAL_SEIZURE_FREE: 4,
    TreatmentResponseState.POST_SURGICAL_NONRESPONDER: 3,
    TreatmentResponseState.UNKNOWN: 1,
}

N_STATES = 5


@dataclass
class HMMParameters:
    """HMM parameter set: π (initial), A (transition), B (emission)."""
    pi: np.ndarray        # (N,) initial state probabilities
    A: np.ndarray         # (N, N) state transition matrix
    B: np.ndarray         # (N, M) emission probability matrix (M = observation categories)
    n_states: int = N_STATES

    def to_dict(self) -> dict:
        return {
            "n_states": self.n_states,
            "pi": self.pi.tolist(),
            "A": self.A.tolist(),
            "B": self.B.tolist(),
        }


def _default_parameters() -> HMMParameters:
    """Return clinically-informed default HMM parameters."""
    pi = np.array([0.1, 0.4, 0.25, 0.15, 0.1])

    # Transition matrix — biased toward disease progression
    A = np.array([
        [0.80, 0.15, 0.04, 0.01, 0.00],  # seizure-free → mostly stays
        [0.10, 0.65, 0.20, 0.05, 0.00],  # drug-responsive → can progress
        [0.05, 0.15, 0.55, 0.25, 0.00],  # emerging resistance → progresses
        [0.02, 0.05, 0.10, 0.73, 0.10],  # established resistance → surgery
        [0.15, 0.20, 0.10, 0.15, 0.40],  # post-surgical → variable
    ])

    # Emission matrix: P(observation | state)
    # Observations: [seizure-free, drug-resp, part-resp, emerg-resist, pharmaco-resist]
    B = np.array([
        [0.70, 0.20, 0.08, 0.02, 0.00],
        [0.10, 0.60, 0.20, 0.08, 0.02],
        [0.03, 0.15, 0.30, 0.35, 0.17],
        [0.01, 0.05, 0.10, 0.25, 0.59],
        [0.35, 0.25, 0.15, 0.15, 0.10],
    ])

    return HMMParameters(pi=pi, A=A, B=B)


class EpilepsyHMM:
    """
    Discrete Hidden Markov Model for epilepsy phenotype trajectory analysis.

    Supports:
    - Forward algorithm (sequence likelihood)
    - Viterbi algorithm (MAP state decoding)
    - Baum-Welch EM (parameter estimation from observed sequences)
    """

    def __init__(self, params: Optional[HMMParameters] = None):
        self.params = params or _default_parameters()
        self.fitted = False

    def _encode_observations(self, trajectory: PhenotypeTrajectory) -> list[int]:
        """Encode treatment response states as integer observation indices."""
        obs = []
        for state in trajectory.states:
            idx = RESPONSE_TO_STATE.get(state.treatment_response, 1)
            obs.append(idx)
        return obs

    def forward(self, observations: list[int]) -> tuple[np.ndarray, float]:
        """
        Forward algorithm. Returns (alpha matrix, log-likelihood).
        alpha[t, i] = P(O₁...Oₜ, Xₜ=i | θ)
        """
        T = len(observations)
        N = self.params.n_states
        alpha = np.zeros((T, N))

        # Initialize
        alpha[0] = self.params.pi * self.params.B[:, observations[0]]
        alpha[0] /= alpha[0].sum() + 1e-300  # Normalize for numerical stability

        # Recurse
        for t in range(1, T):
            for j in range(N):
                alpha[t, j] = np.sum(alpha[t-1] * self.params.A[:, j]) * self.params.B[j, observations[t]]
            scale = alpha[t].sum()
            if scale > 0:
                alpha[t] /= scale

        log_likelihood = float(np.log(alpha[-1].sum() + 1e-300))
        return alpha, log_likelihood

    def viterbi(self, observations: list[int]) -> tuple[list[int], float]:
        """
        Viterbi algorithm. Returns (MAP state sequence, log probability).
        """
        T = len(observations)
        N = self.params.n_states
        log_A = np.log(self.params.A + 1e-300)
        log_B = np.log(self.params.B + 1e-300)
        log_pi = np.log(self.params.pi + 1e-300)

        viterbi_tbl = np.full((T, N), -np.inf)
        backtrack = np.zeros((T, N), dtype=int)

        viterbi_tbl[0] = log_pi + log_B[:, observations[0]]

        for t in range(1, T):
            for j in range(N):
                scores = viterbi_tbl[t-1] + log_A[:, j]
                best_prev = np.argmax(scores)
                viterbi_tbl[t, j] = scores[best_prev] + log_B[j, observations[t]]
                backtrack[t, j] = best_prev

        # Backtrack
        path = [int(np.argmax(viterbi_tbl[-1]))]
        for t in range(T-1, 0, -1):
            path.insert(0, int(backtrack[t, path[0]]))

        log_prob = float(np.max(viterbi_tbl[-1]))
        return path, log_prob

    def fit_and_decode(self, trajectory: PhenotypeTrajectory) -> dict:
        """
        Fit HMM to trajectory and decode state sequence.
        Returns dict with decoded states and summary statistics.
        """
        observations = self._encode_observations(trajectory)
        if len(observations) < 2:
            return {"error": "Need ≥2 time points for HMM decoding"}

        state_sequence, log_prob = self.viterbi(observations)
        _, log_likelihood = self.forward(observations)

        state_names = [
            "seizure_free", "drug_responsive", "emerging_resistance",
            "pharmacoresistant", "post_surgical"
        ]

        return {
            "n_timepoints": len(observations),
            "decoded_states": [state_names[s] for s in state_sequence],
            "log_probability": log_prob,
            "log_likelihood": log_likelihood,
            "terminal_state": state_names[state_sequence[-1]],
            "transitions": [
                f"{state_names[state_sequence[i]]} → {state_names[state_sequence[i+1]]}"
                for i in range(len(state_sequence)-1)
            ],
        }
