"""
ILAE Nosological Versioning Framework

Maintains compatibility across ILAE classification versions (2010, 2017, 2022, 2025).
Enables phenotype records to be retrospectively re-classified when framework
versions are updated.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ILAEVersion(str, Enum):
    V2010 = "2010"
    V2017 = "2017"
    V2022 = "2022"
    V2025 = "2025"


@dataclass
class NosologicalMapping:
    """Mapping of a phenotype concept between ILAE versions."""
    source_version: ILAEVersion
    target_version: ILAEVersion
    source_term: str
    target_term: str
    notes: Optional[str] = None


# Key inter-version mappings
VERSION_MAPPINGS: list[NosologicalMapping] = [
    NosologicalMapping(ILAEVersion.V2010, ILAEVersion.V2017, "complex partial seizure", "focal impaired awareness seizure",
                       "Terminology standardized in 2017 revision"),
    NosologicalMapping(ILAEVersion.V2010, ILAEVersion.V2017, "simple partial seizure", "focal aware seizure"),
    NosologicalMapping(ILAEVersion.V2010, ILAEVersion.V2017, "secondarily generalized", "focal to bilateral tonic-clonic"),
    NosologicalMapping(ILAEVersion.V2017, ILAEVersion.V2022, "focal epilepsy", "focal epilepsy",
                       "Structural/functional etiological subclassification added"),
    NosologicalMapping(ILAEVersion.V2022, ILAEVersion.V2025, "ILAE 2022 syndrome", "ILAE 2025 syndrome",
                       "Additional molecular subtypes recognized"),
]


class NosologicalFramework:
    """Manager for cross-version phenotype concept alignment."""

    def __init__(self, current_version: ILAEVersion = ILAEVersion.V2025):
        self.current_version = current_version

    def translate(self, term: str, from_version: ILAEVersion) -> str:
        """Translate a term from a historical version to current version."""
        # Chain mappings across versions
        current_term = term
        versions = [v for v in ILAEVersion]
        from_idx = versions.index(from_version)
        target_idx = versions.index(self.current_version)

        for i in range(from_idx, target_idx):
            src = versions[i]
            tgt = versions[i+1]
            for mapping in VERSION_MAPPINGS:
                if (mapping.source_version == src and
                    mapping.target_version == tgt and
                    mapping.source_term.lower() == current_term.lower()):
                    current_term = mapping.target_term
                    break
        return current_term
