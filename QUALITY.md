# 📘 QUALITY.md
### Code Quality & Security Configuration – *HomeDashboard*

---

## 🔍 Overview
This document describes the code quality, formatting, testing, and security configuration used in the **HomeDashboard** project.
All quality checks are automated and executed through **pre-commit hooks** before each Git commit.

---

## 🧹 Ruff — Linter & Formatter
**Purpose:** checks code style, import order, and common logic issues.
**Config:** defined in `pyproject.toml`
**Rules:** based on *PEP8* + plugin sets *(E, F, I, B, UP, N)*
**Fix:** automatically formats and corrects minor issues

**Usage:**
```bash
ruff check .        # find issues
ruff check . --fix  # auto-fix
```

Ruff runs automatically via *pre-commit* hooks.

---

## 🧪 Pytest — Unit Testing
**Purpose:** executes functional and unit tests with coverage reporting.
**Config:** `pyproject.toml`
**Test folder:** `/tests`
**Coverage:** automatically measured with `pytest-cov`

**Usage:**
```bash
pytest -v
pytest --cov=src --cov-report=term-missing
```

**Example output:**
```
Name                     Stmts   Miss  Cover
--------------------------------------------
src/api/weather.py          80      2    97%
```

---

## 🛡️ Bandit — Security Scanning
**Purpose:** static code analysis for common security issues.
**Config file:** `bandit.yaml`
**Disabled checks:**
- **B110** – `try/except/pass` (accepted for data parsing loops)
- **B112** – `try/except/continue` (accepted for data source fallbacks)

**Special note:**
`urllib.request.urlopen()` calls are explicitly validated for allowed schemes and marked with `# nosec B310`.

**Manual run:**
```bash
bandit -r src -c bandit.yaml -f json
```

---

## ⚙️ Pre-commit — Automation
**Purpose:** automatically runs all quality checks before commits.
**Config file:** `.pre-commit-config.yaml`

**Installed hooks:**

| Hook                                   | Function              |
|---------------------------------------|------------------------|
| `ruff`                                | Lint & fix imports     |
| `ruff-format`                         | Auto-format code       |
| `bandit`                              | Security scan          |
| `end-of-file-fixer`, `trailing-whitespace` | Basic hygiene       |

**Setup:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## 🧾 Files Summary

| File | Description |
|:----------------------------|:----------------------------------------------|
| `pyproject.toml`            | Central config for Ruff, Pytest, and Coverage |
| `.pre-commit-config.yaml`   | Defines active pre-commit hooks               |
| `bandit.yaml`               | Security rules and exceptions                 |
| `scripts/SetupQuality.ps1`  | Automates setup on Windows                    |
| `tests/`                    | Contains all unit tests                       |

---

## ✅ Quality Pipeline Status
All hooks currently pass successfully:

| Tool        | Status |
|--------------|:-------:|
| **Ruff**     | ✅ |
| **Bandit**   | ✅ |
| **Pytest**   | ✅ |
| **Pre-commit** | ✅ |

---

## 🧰 Developer Tips

- Run `pre-commit run --all-files` after large refactors.
- To temporarily skip checks:
  ```bash
  git commit --no-verify
  ```
- In CI/CD, replicate these steps in `.github/workflows/test.yml`.

---
