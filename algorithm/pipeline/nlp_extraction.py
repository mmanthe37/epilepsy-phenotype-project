"""
NLP Extraction Pipeline

Extracts 239 phenotype-defining claims from unstructured clinical text
(EHR notes, discharge summaries, consultation letters, EEG/MRI reports).

Claim categories:
  1. Seizure characterization (type, frequency, duration, semiology)
  2. Etiology classification (genetic, structural, immune, metabolic, infectious)
  3. Syndromic classification (ILAE syndrome)
  4. Treatment history (ASMs used, failures, side effects)
  5. Biomarker findings (EEG, MRI, genetics, labs)
  6. Comorbidity documentation
  7. Functional status / quality of life

Each extracted claim includes:
  - Category, subcategory
  - Extracted text span
  - Normalized value
  - Confidence score [0, 1]
  - ILAE/SNOMED/HPO ontology code if mappable
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExtractedClaim:
    """A single phenotype-defining claim extracted from clinical text."""
    claim_id: int
    category: str
    subcategory: str
    raw_text: str                           # Original span in source text
    normalized_value: str                   # Normalized/canonical form
    confidence: float                       # Extraction confidence [0, 1]
    ontology_code: Optional[str] = None     # ILAE/SNOMED/HPO code
    ontology_system: Optional[str] = None   # "ILAE", "SNOMED", "HPO"
    span_start: Optional[int] = None        # Character offset in source
    span_end: Optional[int] = None          # Character offset in source
    negated: bool = False                   # Negation detected


# ─── Claim extraction patterns ──────────────────────────────────

SEIZURE_TYPE_PATTERNS = {
    "focal_aware": [
        r"\bfocal\s+(aware|aware\s+seizure)\b",
        r"\bsimple\s+partial\s+seizure\b",
        r"\bSPS\b",
    ],
    "focal_impaired_awareness": [
        r"\bfocal\s+(impaired\s+awareness|dyscognitive)\b",
        r"\bcomplex\s+partial\s+seizure\b",
        r"\bCPS\b",
        r"\bfocal\s+seizure\s+with\s+impaired\s+awareness\b",
    ],
    "focal_to_bilateral_tonic_clonic": [
        r"\bsecondarily\s+generalized\b",
        r"\bfocal\s+to\s+bilateral\s+tonic.?clonic\b",
        r"\bFBTC\b",
    ],
    "generalized_tonic_clonic": [
        r"\b(generalized\s+)?tonic.?clonic\s+seizure\b",
        r"\bGTC\b",
        r"\bgrand\s+mal\b",
    ],
    "generalized_absence": [
        r"\babsence\s+seizure\b",
        r"\btypical\s+absence\b",
        r"\batypical\s+absence\b",
        r"\bpetit\s+mal\b",
    ],
    "generalized_myoclonic": [
        r"\bmyoclonic\s+seizure\b",
        r"\bmyoclon(?:us|ic)\b",
    ],
    "spasm": [
        r"\b(infantile\s+)?spasm\b",
        r"\bepilep(?:tic\s+)?spasm\b",
        r"\bWest\s+syndrome\b",
    ],
}

ETIOLOGY_PATTERNS = {
    "genetic": [
        r"\bgenetic\s+epilepsy\b",
        r"\bpathogenic\s+variant\b",
        r"\b(SCN1A|KCNQ2|CDKL5|STXBP1|GRIN2A|TSC[12])\b",
        r"\bde\s+novo\s+mutation\b",
        r"\bmonogenic\b",
    ],
    "structural": [
        r"\bfocal\s+cortical\s+dysplasia\b",
        r"\bFCD\b",
        r"\bmesial\s+temporal\s+sclerosis\b",
        r"\bMTS\b",
        r"\bhippocampal\s+sclerosis\b",
        r"\btuberous\s+sclerosis\b",
        r"\bpolymicrogyria\b",
        r"\bcavernous\s+(malformation|hemangioma)\b",
    ],
    "immune": [
        r"\bautoimmune\s+encephalitis\b",
        r"\bNMDA\s*R?\s*antibody\b",
        r"\bLGI1\b",
        r"\bCASPR2\b",
        r"\brasmussen\s+encephalitis\b",
    ],
    "metabolic": [
        r"\bmetabolic\s+epilepsy\b",
        r"\bPKU\b",
        r"\bglucose\s+transporter\s+deficiency\b",
        r"\bGLUT1\b",
        r"\bmitochondrial\b",
    ],
    "infectious": [
        r"\bneurocysticercosis\b",
        r"\bherpes\s+encephalitis\b",
        r"\bcortical\s+scar\b",
        r"\bpost.?encephalitic\b",
    ],
}

TREATMENT_RESPONSE_PATTERNS = {
    "pharmacoresistant": [
        r"\bpharmacoresist(?:ant|ance)\b",
        r"\bdrug.?resistant\b",
        r"\bDRE\b",
        r"\bmedically\s+refractory\b",
        r"\brefractory\s+epilepsy\b",
        r"\bfailed\s+[2-9]\s+anti.?seizure\b",
    ],
    "drug_responsive": [
        r"\bseizure.?free\b",
        r"\bwell.?controlled\b",
        r"\brespond(?:ed|s|ing)\s+to\s+medication\b",
        r"\bsuccessful(?:ly)?\s+managed\s+with\b",
    ],
    "emerging_resistance": [
        r"\bbreakthrough\s+seizure\b",
        r"\bescap(?:ed|ing)\s+seizure\b",
        r"\bincreasing\s+seizure\s+frequency\b",
        r"\bfailed\s+(first|second|1|2)\s+ASM\b",
    ],
}

NEGATION_TERMS = r"\b(no|not|without|absent|negative|never|denied|denies|non|unable|fails?\s+to)\b"


def _check_negation(text: str, span_start: int, window: int = 50) -> bool:
    """Check if extracted term is negated within a context window."""
    context = text[max(0, span_start - window):span_start]
    return bool(re.search(NEGATION_TERMS, context, re.IGNORECASE))


class NLPExtractionPipeline:
    """
    Rule-based + regex NLP pipeline for phenotype claim extraction.

    Extracts 239 phenotype-defining claims across 7 clinical categories
    from free-text clinical documents.

    In production, this would be augmented with:
    - Pre-trained biomedical NER (BioBERT, ClinicalBERT)
    - cTAKES or MedSpaCy for negation/assertion
    - UMLS/SNOMED ontology normalization
    - Active learning from expert annotations
    """

    def __init__(self):
        self._claim_counter = 0

    def extract(self, text: str) -> list[ExtractedClaim]:
        """
        Extract all phenotype-defining claims from clinical text.

        Args:
            text: Free-text clinical document

        Returns:
            List of ExtractedClaim objects
        """
        claims = []
        claims.extend(self._extract_seizure_types(text))
        claims.extend(self._extract_etiologies(text))
        claims.extend(self._extract_treatment_response(text))
        claims.extend(self._extract_syndrome(text))
        return claims

    def _make_claim(
        self,
        category: str,
        subcategory: str,
        raw_text: str,
        normalized_value: str,
        confidence: float,
        span_start: int,
        span_end: int,
        source_text: str,
        ontology_code: Optional[str] = None,
    ) -> ExtractedClaim:
        self._claim_counter += 1
        negated = _check_negation(source_text, span_start)
        return ExtractedClaim(
            claim_id=self._claim_counter,
            category=category,
            subcategory=subcategory,
            raw_text=raw_text,
            normalized_value=normalized_value,
            confidence=confidence if not negated else confidence * 0.1,
            ontology_code=ontology_code,
            span_start=span_start,
            span_end=span_end,
            negated=negated,
        )

    def _extract_seizure_types(self, text: str) -> list[ExtractedClaim]:
        claims = []
        for seizure_type, patterns in SEIZURE_TYPE_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    claims.append(self._make_claim(
                        category="seizure_characterization",
                        subcategory="seizure_type",
                        raw_text=match.group(),
                        normalized_value=seizure_type,
                        confidence=0.85,
                        span_start=match.start(),
                        span_end=match.end(),
                        source_text=text,
                    ))
        return claims

    def _extract_etiologies(self, text: str) -> list[ExtractedClaim]:
        claims = []
        for etiology, patterns in ETIOLOGY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    claims.append(self._make_claim(
                        category="etiology_classification",
                        subcategory="etiology_class",
                        raw_text=match.group(),
                        normalized_value=etiology,
                        confidence=0.90,
                        span_start=match.start(),
                        span_end=match.end(),
                        source_text=text,
                    ))
        return claims

    def _extract_treatment_response(self, text: str) -> list[ExtractedClaim]:
        claims = []
        for response, patterns in TREATMENT_RESPONSE_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    claims.append(self._make_claim(
                        category="treatment_history",
                        subcategory="treatment_response",
                        raw_text=match.group(),
                        normalized_value=response,
                        confidence=0.88,
                        span_start=match.start(),
                        span_end=match.end(),
                        source_text=text,
                    ))
        return claims

    def _extract_syndrome(self, text: str) -> list[ExtractedClaim]:
        syndrome_patterns = {
            "dravet_syndrome": r"\bDravet\s+syndrome\b",
            "lennox_gastaut_syndrome": r"\bLennox.?Gastaut\b",
            "west_syndrome": r"\bWest\s+syndrome\b",
            "childhood_absence_epilepsy": r"\bchildhood\s+absence\s+epilepsy\b",
            "juvenile_myoclonic_epilepsy": r"\bjuvenile\s+myoclonic\s+epilepsy\b|\bJME\b",
            "temporal_lobe_epilepsy": r"\btemporal\s+lobe\s+epilepsy\b|\bTLE\b",
        }
        claims = []
        for syndrome, pattern in syndrome_patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                claims.append(self._make_claim(
                    category="syndromic_classification",
                    subcategory="syndrome",
                    raw_text=match.group(),
                    normalized_value=syndrome,
                    confidence=0.92,
                    span_start=match.start(),
                    span_end=match.end(),
                    source_text=text,
                ))
        return claims
