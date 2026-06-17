"""Unit tests for PhenotypeStateVector."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from algorithm.core.phenotype_vector import (
    PhenotypeTrajectory, SeizureType, EtiologyClass,
    TreatmentResponseState
)


def test_seizure_type_enum():
    assert SeizureType.FOCAL_AWARE is not None
    assert SeizureType.GENERALIZED_TONIC_CLONIC is not None
    print("test_seizure_type_enum: PASSED")


def test_etiology_enum():
    assert EtiologyClass.STRUCTURAL is not None
    assert EtiologyClass.GENETIC is not None
    print("test_etiology_enum: PASSED")


def test_trajectory_empty():
    traj = PhenotypeTrajectory(patient_id="P001")
    assert traj.patient_id == "P001"
    assert traj.current is None
    assert traj.baseline is None
    print("test_trajectory_empty: PASSED")


def test_treatment_response_enum():
    assert TreatmentResponseState.DRUG_RESPONSIVE is not None
    assert TreatmentResponseState.PHARMACORESISTANT is not None
    print("test_treatment_response_enum: PASSED")


if __name__ == "__main__":
    test_seizure_type_enum()
    test_etiology_enum()
    test_trajectory_empty()
    test_treatment_response_enum()
    print("ALL phenotype_vector tests PASSED")
