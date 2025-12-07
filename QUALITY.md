# 📘 QUALITY.md — Code Quality & Security Standards

This document defines the code quality, formatting, testing, and security practices used in the **HomeDashboard** project.
All checks run automatically via **pre-commit hooks** and are validated continuously during development.

---

## 🔍 Overview
The goal of the quality pipeline is to ensure:
- Consistent, clean, auto-formatted code
- High test coverage and predictable behaviour
- Static analysis for catching logic and security issues early
- Automated enforcement before each commit

The tools used are:
- **Ruff** (linting + formatting)
- **Pytest** (+ Coverage)
- **Bandit** (security)
- **pre-commit** (automation)

---

## 🧹 Ruff — Linter & Auto-Formatter
**Purpose:** Enforces code style, import order, and detects common Python issues.

**Configuration:** `pyproject.toml`

**Rule sets enabled:**
- `E`, `F`, `I` — Standard PEP8 and import rules
- `B` — Bugbear (logic/bug detection)
- `UP` — Python upgrade rules
- `N` — Naming conventions

**Typical usage:**
```bash
ruff check .          # report issues
ruff check . --fix    # auto-fix
```

Ruff is executed automatically on commit.

---

## 🧪 Pytest — Unit Testing & Coverage
**Purpose:** Executes unit tests and validates behaviour of API, UI viewmodels, and utility layers.

**Configuration:** `pyproject.toml`

**Test folder:** `tests/`

**Coverage:** Generated with `pytest-cov` and reported in terminal.

Example:
```bash
pytest -v
pytest --cov=src --cov-report=term-missing
```

Test coverage in the project is typically **80–90%**, depending on feature set.

---

## 🛡️ Bandit — Security Scanning
**Purpose:** Performs static security analysis and flags high-risk patterns.

**Configuration:** `bandit.yaml`

**Expected exceptions:**
- `B110` — use of `try/except/pass` (allowed for controlled parsing logic)
- `B112` — use of `try/except/continue` (allowed for fallback data sources)

**Special handling:**
All `urllib.request.urlopen()` calls are explicitly validated, and cases requiring exceptions are annotated with:
```python
# nosec B310
```

Manual run:
```bash
bandit -r src -c bandit.yaml -f json
```

---

## ⚙️ Pre-commit — Automated Quality Pipeline
**Purpose:** Ensures that all code meets quality rules before commits are accepted.

**Configuration file:** `.pre-commit-config.yaml`

**Installed hooks:**
| Hook | Function |
|------|----------|
| `ruff` | Lint & import order |
| `ruff-format` | Formatting |
| `bandit` | Security scan |
| `end-of-file-fixer`, `trailing-whitespace` | Basic file hygiene |

Setup:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## 🧾 Relevant Files
| File | Purpose |
|------|---------|
| `pyproject.toml` | Central config for Ruff, Pytest, Coverage |
| `.pre-commit-config.yaml` | Defines hooks |
| `bandit.yaml` | Security rules & exceptions |
| `scripts/SetupQuality.ps1` | Windows setup script |
| `tests/` | Unit tests |

---

## ✅ Quality Pipeline Status
Current status:

| Tool | Status |
|-------|:------:|
| **Ruff** | ✅ |
| **Bandit** | ✅ |
| **Pytest** | ✅ |
| **Pre-commit** | ✅ |

The project passes all checks.

---

## 🧰 Developer Tips
- Run full pipeline after large refactors:
  ```bash
  pre-commit run --all-files
  ```
- To bypass checks temporarily:
  ```bash
  git commit --no-verify
  ```
- In CI/CD, replicate the same steps in `.github/workflows/test.yml`.

---
