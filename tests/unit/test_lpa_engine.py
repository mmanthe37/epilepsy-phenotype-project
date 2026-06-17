"""Unit tests for LPAEngine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from algorithm.core.lpa_engine import LPAEngine, LPAConfig, IngestionRecord
from algorithm.core.evidence_ledger import DataRecordType, SourceTier
from datetime import datetime


def _make_record(content_text="Focal aware seizures. MRI: hippocampal sclerosis."):
    """Helper: build a valid IngestionRecord."""
    return IngestionRecord(
        timestamp=datetime(2024, 1, 1),
        record_type=DataRecordType.CLINICAL_NOTE,
        source_description="Epilepsy clinic specialist note",
        author_id="dr_test",
        content={"text": content_text},
        source_tier=SourceTier.SPECIALIST_EVALUATION,
        narrative=content_text,
    )


def test_engine_init():
    engine = LPAEngine(patient_id="UNIT-000")
    assert engine.patient_id == "UNIT-000"
    assert engine.config is not None
    assert engine.ledger is not None
    print("test_engine_init: PASSED")


def test_engine_ingest():
    engine = LPAEngine(patient_id="UNIT-001")
    engine.ingest(_make_record())
    assert engine.ledger.size == 1
    print("test_engine_ingest: PASSED")


def test_engine_resolve_csep():
    engine = LPAEngine(patient_id="UNIT-002")
    engine.ingest(_make_record("Focal impaired awareness seizures. Structural etiology."))
    report = engine.resolve_csep()
    assert report is not None
    assert report.patient_id == "UNIT-002"
    print("test_engine_resolve_csep: PASSED")


def test_engine_ledger_summary():
    engine = LPAEngine(patient_id="UNIT-003")
    engine.ingest(_make_record("Test record for ledger summary."))
    summary = engine.ledger_summary()
    assert isinstance(summary, dict)
    assert summary["patient_id"] == "UNIT-003"
    assert summary["total_entries"] == 1
    print("test_engine_ledger_summary: PASSED")


if __name__ == "__main__":
    test_engine_init()
    test_engine_ingest()
    test_engine_resolve_csep()
    test_engine_ledger_summary()
    print("ALL lpa_engine tests PASSED")
