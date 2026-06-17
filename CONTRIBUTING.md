# Contributing to the Epilepsy Phenotype Project

Thank you for your interest in contributing!

## Setup

```bash
git clone https://github.com/mmanthe37/epilepsy-phenotype-project.git
cd epilepsy-phenotype-project
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
pytest tests/ -v --cov=algorithm
```

## Code Standards

- Follow PEP 8; use type hints throughout
- Every public function must have a docstring with Args + Returns
- New algorithm components must include a unit test in `tests/unit/`

## Pull Request Process

1. Fork the repo and create a feature branch
2. Implement changes with tests
3. Run the full test suite — all tests must pass
4. Submit a pull request with a clear description of the change

## Clinical Content Contributions

Changes to clinical thresholds, tier weights, or ILAE mappings require
a supporting citation in the PR description.
