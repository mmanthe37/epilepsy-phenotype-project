"""Unit tests for EvidenceLedger."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from datetime import datetime
from algorithm.core.evidence_ledger import (
    EvidenceLedger, LedgerEntry, DataRecordType, SourceTier, TIER_WEIGHTS
)


def test_tier_weights():
    for tier, weight in TIER_WEIGHTS.items():
        assert 0.0 <= weight <= 1.0
    print("test_tier_weights: PASSED")


def test_ledger_creation():
    ledger = EvidenceLedger("PT-001")
    assert ledger.patient_id == "PT-001"
    assert len(ledger) == 0
    print("test_ledger_creation: PASSED")


def test_ledger_verify_integrity():
    ledger = EvidenceLedger("PT-002")
    result = ledger.verify_integrity()
    assert result is True  # empty ledger is valid
    print("test_ledger_verify_integrity: PASSED")


def test_ledger_query_empty():
    ledger = EvidenceLedger("PT-003")
    results = ledger.all()
    assert results == []
    print("test_ledger_query_empty: PASSED")


def test_ledger_size():
    ledger = EvidenceLedger("PT-004")
    assert ledger.size == 0
    print("test_ledger_size: PASSED")


if __name__ == "__main__":
    test_tier_weights()
    test_ledger_creation()
    test_ledger_verify_integrity()
    test_ledger_query_empty()
    test_ledger_size()
    print("ALL evidence_ledger tests PASSED")
