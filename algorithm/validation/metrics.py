"""
Validation Metrics for the VLEP/LPA System

Implements validation metrics aligned with survival analysis and
longitudinal prediction evaluation:

- td-AUROC: Time-dependent Area Under ROC Curve
- C-index: Harrell's concordance index
- Brier score: Probabilistic calibration metric
- Integrated Brier Score (IBS)
- Sensitivity / Specificity at threshold
"""

from __future__ import annotations
import math
from typing import Optional, Sequence
import numpy as np


def concordance_index(
    event_times: np.ndarray,
    predicted_scores: np.ndarray,
    event_occurred: np.ndarray,
) -> float:
    """
    Harrell's C-index for survival predictions.

    C = P(risk_score(i) > risk_score(j) | T(i) < T(j), event(i)=1)

    Range: [0.5, 1.0]. 0.5 = random, 1.0 = perfect discrimination.

    Args:
        event_times:      Observed event/censoring times
        predicted_scores: Risk scores (higher = higher risk)
        event_occurred:   Binary: 1 if event occurred, 0 if censored

    Returns:
        C-index ∈ [0, 1]
    """
    n = len(event_times)
    concordant = 0
    discordant = 0
    tied = 0

    for i in range(n):
        if not event_occurred[i]:
            continue
        for j in range(n):
            if event_times[i] >= event_times[j]:
                continue
            # i had earlier event
            if predicted_scores[i] > predicted_scores[j]:
                concordant += 1
            elif predicted_scores[i] < predicted_scores[j]:
                discordant += 1
            else:
                tied += 1

    comparable = concordant + discordant + tied
    if comparable == 0:
        return float("nan")
    return (concordant + 0.5 * tied) / comparable


def brier_score(
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> float:
    """
    Brier score for binary classification / survival calibration.

    BS = (1/N) Σᵢ (yᵢ − p̂ᵢ)²

    Range: [0, 1]. 0 = perfect, 0.25 = uninformative (constant 0.5).

    Args:
        y_true: True binary labels (0/1)
        y_prob: Predicted probabilities ∈ [0, 1]

    Returns:
        Brier score ∈ [0, 1]
    """
    return float(np.mean((y_true - y_prob) ** 2))


def td_auroc(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_thresholds: int = 100,
) -> float:
    """
    Time-dependent AUROC (simplified version for binary outcomes).

    Computes AUC via trapezoidal integration of the ROC curve.
    For time-dependent version, call with outcome at a specific horizon t*.

    Args:
        y_true:  True binary labels at time horizon t*
        y_score: Predicted probabilities at time horizon t*

    Returns:
        AUROC ∈ [0.5, 1.0]
    """
    thresholds = np.linspace(0, 1, n_thresholds)[::-1]
    tpr_list = []
    fpr_list = []

    pos = y_true.sum()
    neg = len(y_true) - pos

    if pos == 0 or neg == 0:
        return float("nan")

    for thresh in thresholds:
        pred = (y_score >= thresh).astype(int)
        tp = np.sum((pred == 1) & (y_true == 1))
        fp = np.sum((pred == 1) & (y_true == 0))
        tpr_list.append(tp / pos)
        fpr_list.append(fp / neg)

    # Trapezoidal AUC
    tpr = np.array(tpr_list)
    fpr = np.array(fpr_list)
    return float(np.trapz(tpr, fpr))


def integrated_brier_score(
    brier_scores: Sequence[float],
    time_points: Sequence[float],
) -> float:
    """
    Integrated Brier Score (IBS) over time points.

    IBS = (1/τ) ∫₀ᵗ BS(t) dt ≈ trapezoidal integral

    Args:
        brier_scores: Brier score at each time point
        time_points:  Corresponding time values (sorted ascending)

    Returns:
        IBS ∈ [0, 1]
    """
    t = np.array(time_points)
    bs = np.array(brier_scores)
    total_time = t[-1] - t[0]
    if total_time == 0:
        return float("nan")
    return float(np.trapz(bs, t) / total_time)


def classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, float]:
    """
    Standard classification metrics at threshold 0.5.

    Returns sensitivity, specificity, PPV, NPV, F1, accuracy.
    """
    y_pred_bin = (y_pred >= 0.5).astype(int)

    tp = float(np.sum((y_pred_bin == 1) & (y_true == 1)))
    fp = float(np.sum((y_pred_bin == 1) & (y_true == 0)))
    tn = float(np.sum((y_pred_bin == 0) & (y_true == 0)))
    fn = float(np.sum((y_pred_bin == 0) & (y_true == 1)))

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
    specificity = tn / (tn + fp) if (tn + fp) > 0 else float("nan")
    ppv = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
    npv = tn / (tn + fn) if (tn + fn) > 0 else float("nan")
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else float("nan")
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else float("nan")

    return {
        "sensitivity": sensitivity,
        "specificity": specificity,
        "ppv": ppv,
        "npv": npv,
        "f1": f1,
        "accuracy": accuracy,
    }
