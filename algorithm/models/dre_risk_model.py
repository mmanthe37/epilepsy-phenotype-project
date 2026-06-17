"""
Drug-Resistant Epilepsy (DRE) Risk Model

Binary classifier for identifying patients at high risk of developing
pharmacoresistance (drug-resistant epilepsy, DRE).

DRE is defined per ILAE 2010 consensus: failure of adequate trials of ≥2
tolerated and appropriately chosen ASM schedules to achieve sustained
seizure freedom.

This model integrates with the LPA engine to flag patients at intake
or early follow-up for proactive surgical evaluation referral.
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class DRERiskProfile:
    patient_id: str
    risk_score: float               # 0–1
    risk_category: str              # "low", "moderate", "high"
    top_risk_factors: list[str]
    surgical_referral_recommended: bool
    monitoring_interval_months: int  # Suggested follow-up interval


# Evidence-based DRE risk factors and their log-odds contributions
# Derived from Mohanraj & Brodie (2006), Brodie et al. (2012), Xue-Ping et al. (2019)
DRE_RISK_FACTORS = {
    "focal_seizures": 0.62,
    "structural_etiology": 1.08,
    "mri_lesion": 0.89,
    "early_seizure_onset_under_1yr": 0.95,
    "high_seizure_frequency_at_onset": 0.71,
    "failed_first_asm": 0.84,
    "history_of_febrile_status": 0.55,
    "abnormal_neurological_exam": 0.67,
    "intellectual_disability": 0.58,
    "eeg_multifocal": 0.72,
    "genetic_epilepsy_high_risk": 0.88,     # SCN1A, CDKL5, STXBP1
    "psychiatric_comorbidity": 0.38,
}


class DRERiskModel:
    """
    Logistic regression-based DRE risk classifier.
    """

    def __init__(self, threshold: float = 0.4):
        self.threshold = threshold
        self.intercept = -1.5  # Prior ~18% base rate

    def predict(self, features: dict[str, float]) -> DRERiskProfile:
        patient_id = features.get("patient_id", "unknown")
        log_odds = self.intercept
        active_factors = []

        for factor, coef in DRE_RISK_FACTORS.items():
            val = features.get(factor, 0.0)
            if val > 0:
                log_odds += coef * val
                active_factors.append((factor, coef * val))

        prob = 1 / (1 + np.exp(-log_odds))
        risk_cat = "high" if prob > 0.6 else ("moderate" if prob > self.threshold else "low")

        # Top 3 risk factors by contribution
        top3 = sorted(active_factors, key=lambda x: x[1], reverse=True)[:3]

        return DRERiskProfile(
            patient_id=str(patient_id),
            risk_score=float(prob),
            risk_category=risk_cat,
            top_risk_factors=[f for f, _ in top3],
            surgical_referral_recommended=(risk_cat == "high"),
            monitoring_interval_months=3 if risk_cat == "high" else (6 if risk_cat == "moderate" else 12),
        )
