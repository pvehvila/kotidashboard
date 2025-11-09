📘 QUALITY.md

Code Quality & Security Configuration – HomeDashboard

🔍 Overview

This document describes the code quality, formatting, testing and security configuration used in the HomeDashboard project.
All quality checks are automated and executed through pre-commit hooks before each Git commit.

🧹 Ruff — Linter & Formatter

    Purpose: checks code style, import order, and common logic issues.
    Config: defined in pyproject.toml
    Rules: based on PEP8 + common plugin sets (E, F, I, B, UP, N)
    Fix: automatically formats and corrects minor issues
    
    Usage:
    
    ruff check .        # find issues
    ruff check . --fix  # auto-fix
    
    Run in pre-commit automatically.

🧪 Pytest — Unit Testing

    Purpose: executes functional and unit tests, with coverage reporting.
    Config: pyproject.toml
    Test folder: /tests
    Coverage: automatically measured (pytest-cov)
    Usage:
    
    pytest -v
    pytest --cov=src --cov-report=term-missing
    
    Example Output:
    
    Name                     Stmts   Miss  Cover
    --------------------------------------------
    src/api/weather.py          80      2    97%

🛡️ Bandit — Security Scanning

    Purpose: static code analysis for common security risks.
    Config file: bandit.yaml
    Disabled checks:
        B110 – try/except/pass (accepted for data parsing loops)
        B112 – try/except/continue (accepted for data source fallbacks)

    Special note:
    urllib.request.urlopen() calls are explicitly validated for allowed schemes and marked with # nosec B310.

    Run manually:

    bandit -r src -c bandit.yaml -f json

⚙️ Pre-commit — Automation

    Purpose: automatically runs all quality checks before commits.
    Configuration: .pre-commit-config.yaml
    Installed hooks:
        Hook	                                Function
        ruff	                                Lint & fix imports
        ruff-format	                            Auto-format code
        bandit	                                Security scan
        end-of-file-fixer, trailing-whitespace	Basic hygiene

    Setup command:

        pip install pre-commit
        pre-commit install
        pre-commit run --all-files

🧾 Files Summary

    | File | Description |
    |:----|:------------|
    |pyproject.toml	| Central config for Ruff, Pytest, Coverage |
    |.pre-commit-config.yaml | Defines active hooks |
    |bandit.yaml | Security rules |
    |scripts/SetupQuality.ps1 |	Automates setup on Windows |
    |tests/	| Contains all unit tests |

✅ Quality Pipeline Status

    All hooks currently pass:
    
    Tool	Status
    Ruff	✅
    Bandit	✅
    Pytest	✅
    Pre-commit	✅

🧰 Developer Tips

    Run pre-commit run --all-files after large refactors.
    
    To temporarily skip checks: git commit --no-verify.

For CI/CD, replicate the same steps in .github/workflows/test.yml.
