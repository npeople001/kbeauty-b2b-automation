# Privacy Guard Baseline Test Matrix

## 1. Purpose

This document records the pre-enhancement Privacy Guard baseline before Task 014 code changes start.

It documents the current behavior of `tests/validate_privacy_guard.py`, the current PASS baseline, current scan scope, current false-positive protections, staged-only behavior, `.gitignore` behavior, and the regression matrix that future Privacy Guard enhancement steps must preserve.

This document is documentation only. It does not modify validator code, `.gitignore`, automation logic, source CSV files, generated output files, or business data.

## 2. Current Baseline Result

Latest baseline commands:

```powershell
python tests\validate_privacy_guard.py
python -m py_compile tests\validate_privacy_guard.py
git status --short
```

Observed result:

| Item | Current result |
| --- | --- |
| Privacy Guard command | `python tests\validate_privacy_guard.py` |
| PASS/WARNING/FAIL result | PASS |
| files_scanned | 84 |
| warnings | 0 |
| failures | 0 |
| py_compile result | PASS; no output |
| git status summary | Only Task 014 Step A document is untracked: `docs/privacy_guard_enhancement_implementation_plan.md` |

Baseline note:

- The `files_scanned` count increased from 83 to 84 after Task 014 Step A because `docs/privacy_guard_enhancement_implementation_plan.md` was added.
- This is expected and does not indicate a validator behavior change.

## 3. Current Privacy Guard Responsibilities

The current validator already checks:

- Repository privacy policy compliance.
- Sensitive filename and path patterns.
- Current `.gitignore` privacy protections.
- Sample/source files remain trackable.
- Sample contact placeholder safety.
- Non-placeholder email detection.
- Phone-like values that may require review.
- Proposal and quotation internal-review disclaimers.
- Approval-required brand context.
- Forbidden external collection and sending implementation patterns.
- Working-tree and staged-only scan modes.

The current output format is:

```text
PASS: privacy guard validation passed
files_scanned=<number>
warnings=<number>
failures=<number>
```

Warnings and failures are printed below the summary when present.

The validator uses local repository inspection only. It does not scrape, search, call APIs, automate browsers, enrich buyer data, run credit checks, send email/messages/quotations, or collect external data.

## 4. Current Protected Paths

Existing `.gitignore` and validator expectations protect these areas:

| Path or pattern | Current protection | Local existence |
| --- | --- | --- |
| `data/private/**` | Protected by `.gitignore` and required by Privacy Guard | `data/private` does not exist |
| `data/private/templates/**` | Covered by `data/private/**` | `data/private/templates` does not exist |
| `output/private/**` | Protected by `.gitignore`; `git check-ignore` currently reports `output/*` as the active matching rule | `output/private` does not exist |
| `output/final/**` | Protected by `.gitignore`; `git check-ignore` currently reports `output/*` as the active matching rule | `output/final` does not exist |
| `local_config/**` | Protected by `.gitignore` and required by Privacy Guard | not reviewed as an existing folder in Step B |
| `*_real.csv` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_private.csv` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_contacts.csv` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_prices.csv` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_stock.csv` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_expiry.csv` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_quotation_final.*` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_final_quotation.*` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_external_ready.*` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `*_send_ready.*` | Protected by `.gitignore` and sensitive filename checks | pattern only |
| `output/*` | Generated outputs ignored except `output/.gitkeep` | generated outputs may exist locally and remain ignored |

## 5. Current Scan Scope

Observed from source inspection:

| Area | Current behavior |
| --- | --- |
| `docs/` | Scanned when text-like and not skipped. Policy wording can currently be scanned, so false-positive handling matters. |
| `data/` | Scanned for text-like files such as CSV. Contact CSV checks apply to contact columns. |
| `tests/` | Scanned for Python code. Forbidden import and call checks apply, with some comment/docstring safety handling. |
| `automations/` | Scanned for Python code. Forbidden import and call checks apply. |
| `README.md` | Scanned as Markdown. |
| `AGENTS.md` | Scanned as Markdown. |
| `.gitignore` | Scanned as text-like file and also checked directly by `check_gitignore`. |
| `output/*` | Current `should_skip` skips `output/` files except `output/.gitkeep`, so generated output files generally do not break validation. |
| ignored output files | Not scanned when skipped by `should_skip`; future behavior may add warnings for ignored generated outputs if needed. |

Current text suffixes:

- `.md`
- `.csv`
- `.txt`
- `.py`
- `.json`
- `.yaml`
- `.yml`
- `.gitignore`

Current skipped directories:

- `.git`
- `.venv`
- `venv`
- `__pycache__`

Current skipped suffixes:

- `.xlsx`
- `.xls`
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`
- `.gif`
- `.webp`
- `.html`

## 6. Current Forbidden Patterns

Current sensitive path and filename categories include:

- Private paths:
  - `data/private/**`
  - `output/private/**`
  - `output/final/**`
  - `local_config/**`
- Real/private CSV patterns:
  - `*_real.csv`
  - `*_private.csv`
  - `*_production.csv`
  - `*_contacts.csv`
  - `*_buyers_real.csv`
  - `*_prices.csv`
  - `*_price_list.csv`
  - `*_stock.csv`
  - `*_inventory.csv`
  - `*_expiry.csv`
- Quotation and commercial patterns:
  - `*_quotation_final.*`
  - `*_final_quotation.*`
  - `*_supplier_terms.*`
  - `*_contract_terms.*`
  - `*_payment_terms.*`
  - `*_incoterms.*`
  - `*_external_ready.*`
  - `*_send_ready.*`
- Credential and local config patterns:
  - `.env`
  - `*.key`
  - `*_token*`
  - `*_credentials*`
  - `credentials.*`
  - `secrets.*`
  - `local_settings.*`
  - `local_config.*`

Current contact and real-data checks include:

- Email pattern detection, with `example.invalid` allowed.
- CSV contact column placeholder checks for:
  - `contact_email`
  - `contact_phone`
  - `wechat_id`
  - `whatsapp`
  - `contact_name`
- Phone-like value warning when contact-related terms are present.

Current external automation checks include forbidden imports and code patterns for:

- `requests`
- `httpx`
- `selenium`
- `playwright`
- `smtplib`
- `urllib.request`
- `SMTP(`
- `.sendmail(`
- `requests.get/post/put/delete/request`
- `httpx.get/post/put/delete/request`
- `webdriver.`

## 7. Current Allowlist and Safe-Context Behavior

Current false-positive protections include:

- Placeholder email domain:
  - `example.invalid`
- Placeholder phone:
  - `+00-0000-0000`
- Placeholder WeChat prefix:
  - `placeholder`
- Placeholder contact prefix:
  - `Sample Contact`
- Internal-review disclaimer checks for proposal and quotation sample outputs.
- Safe approval-required brand context terms such as:
  - `approval-required`
  - `approval_required`
  - `proposal_allowed=false`
  - `blocked`
  - `excluded`
  - `excluded_brands`
  - `approval_block`
  - `internal-review`
  - `not external`
  - `must not`
  - `validation`
- Python forbidden code check skips lines that are comments or contain `does not` or `do not`.
- `output/*` generated files are currently skipped except `output/.gitkeep`.

Current limitations:

- Documentation and validator deny-list handling is partly implicit, not fully formalized.
- File sensitivity categories such as STRICT, CODE, DOCS, and GENERATED_IGNORED are not yet explicit in code.
- Some forbidden terms in policy docs are safe today because of context and current skipped output behavior, but future stricter content checks need more intentional false-positive prevention.
- Generated ignored outputs are mostly skipped rather than classified with WARNING/INFO.

## 8. Baseline Regression Matrix

| Baseline area | Current expected result | Future enhancement risk | Required regression check | Command or inspection method |
| --- | --- | --- | --- | --- |
| Current sample data passes | PASS | Stricter contact/content checks may flag sample placeholders. | Confirm Privacy Guard PASS. | `python tests\validate_privacy_guard.py` |
| Current documentation passes | PASS | Policy wording may be misread as leaked sensitive data. | Confirm docs do not create false failures. | Privacy Guard plus docs sensitivity review |
| Current validators pass | PASS | Deny-list strings may be misread as forbidden implementation. | Confirm validator files do not false fail. | Privacy Guard and py_compile |
| Current automation scripts pass | PASS | External automation deny-list may overmatch safe text. | Confirm automation scripts still pass. | Privacy Guard |
| Current generated ignored outputs do not break validation | PASS | Future output scanning may flag ignored internal-review outputs. | Confirm output handling remains intentional. | Privacy Guard plus `git status --ignored` if needed |
| No `data/private` folder exists | PASS | Future tests may accidentally create folder. | Confirm folder does not exist. | `Test-Path data\private` |
| No `output/private` folder exists | PASS | Future tests may accidentally create folder. | Confirm folder does not exist. | `Test-Path output\private` |
| No `output/final` folder exists | PASS | Future tests may accidentally create folder. | Confirm folder does not exist. | `Test-Path output\final` |
| External automation deny-list strings in validators do not cause false positives | PASS | More aggressive string scanning may fail validator itself. | Keep code context and validator deny-list exception. | Privacy Guard and source inspection |
| Policy docs mentioning prohibited terms do not cause false positives | PASS | Content scanner may overmatch docs. | DOCS sensitivity model must allow policy language. | Privacy Guard |
| Operations Dashboard generated output does not cause false failure | PASS under current skip behavior | Future generated output scanning may flag dashboard wording. | Ensure ignored internal-review output is warning/allowed unless unsafe. | Privacy Guard and dashboard validator |
| Integrated Runner files do not cause false failure | PASS | Runner command strings may look operational. | Confirm runner remains local-only and passes Privacy Guard. | Privacy Guard and integrated runner validation |

## 9. Future Test Matrix

| Category | Expected severity | Real files needed? | Preferred test method | False positive risk | Mitigation |
| --- | --- | --- | --- | --- | --- |
| Private path staged/tracked | FAIL | No | Synthetic path classification or controlled Git inspection without real data | Low | Do not create private folders; test classification helpers. |
| Private path ignored local | WARNING | No | `git check-ignore` example paths; optional temp path outside repo | Medium | Avoid creating `data/private` or `output/private`. |
| Sensitive filename tracked | FAIL | No | Synthetic filename list | Low | Test patterns with strings rather than files. |
| Contact field in strict CSV | FAIL | No | Synthetic CSV string | Medium | Allow approved sample placeholders only. |
| Contact placeholder in docs | INFO | No | Synthetic Markdown string | Medium | DOCS sensitivity model and placeholder allowlist. |
| External automation import in automations | FAIL | No | Synthetic Python code string parsed with AST | Low | Detect imports/calls, not documentation text. |
| Forbidden pattern string in validator | INFO | No | Synthetic validator snippet or existing validator inspection | High | Allow deny-list/config context. |
| Final quotation wording in docs | INFO | No | Synthetic policy Markdown | High | Safe context phrase detection. |
| Final quotation wording in output | FAIL or WARNING | No | Synthetic output Markdown string | Medium | Require internal-review context; fail external-ready/final wording. |
| Generated ignored dashboard | WARNING or PASS | No | Existing ignored dashboard path inspection | Medium | Check ignored status and internal-review disclaimer. |
| Sample placeholder contact | INFO or PASS | No | Synthetic sample CSV string | Low | Allow `example.invalid`, `+00-0000-0000`, and placeholder prefixes. |
| `approval_block` policy docs | INFO | No | Synthetic policy Markdown | High | Safe context phrase detection and DOCS model. |

## 10. Staged-Only Mode Baseline

The current validator supports:

```powershell
python tests\validate_privacy_guard.py --mode staged-only
```

Current observed result:

```text
PASS: privacy guard validation passed
files_scanned=0
warnings=0
failures=0
```

Interpretation:

- No files were staged at the time of the baseline run.
- Staged-only mode can inspect staged files through `git diff --cached --name-only`.
- Future enhancements should preserve this mode and make private/final staged-path failures blocking.

## 11. git check-ignore Baseline

Commands run:

```powershell
git check-ignore -v data/private/example.csv
git check-ignore -v output/private/example.md
git check-ignore -v output/final/example.pdf
```

Observed results:

| Example path | Ignored? | Reported source rule | Future review needed? |
| --- | --- | --- | --- |
| `data/private/example.csv` | Yes | `.gitignore:22:data/private/**` | No immediate change needed. |
| `output/private/example.md` | Yes | `.gitignore:60:output/*` | No immediate change needed, but future reporting may prefer confirming specific `output/private/**` also exists. |
| `output/final/example.pdf` | Yes | `.gitignore:60:output/*` | No immediate change needed, but future reporting may prefer confirming specific `output/final/**` also exists. |

`.gitignore` should not be modified in Step B.

## 12. Implementation Readiness

Before Step C code changes, the following must be true:

- Baseline behavior is documented.
- Privacy Guard PASS is confirmed.
- `py_compile` PASS is confirmed.
- `git status --short` is understood.
- No real/private/final folders exist.
- No private data has been introduced.
- False-positive strategy is understood.
- `.gitignore` is not modified without explicit approval.

Current readiness:

- Baseline Privacy Guard PASS: yes.
- `py_compile` PASS: yes.
- Current git status: only Task 014 Step A document was untracked before Step B.
- Private/final folders: absent.

## 13. Step C Entry Criteria

Step C can start only if:

- `docs/privacy_guard_baseline_test_matrix.md` exists.
- Current Privacy Guard passes.
- `python -m py_compile tests\validate_privacy_guard.py` passes.
- `git status --short` is clean or contains only Task 014 documentation changes.
- No `data/private/`, `data/private/templates/`, `output/private/`, or `output/final/` folders exist.
- `.gitignore` is not modified without explicit approval.
- Step C instructions explicitly authorize modifying `tests/validate_privacy_guard.py`.

## 14. Completion Criteria

Step B passes when:

- `docs/privacy_guard_baseline_test_matrix.md` exists.
- Baseline behavior is documented.
- Baseline regression matrix exists.
- Future test matrix exists.
- No code was implemented.
- `tests/validate_privacy_guard.py` was not modified.
- `.gitignore` was not modified.
- Privacy Guard still passes.
- No real data files were created.
- No private/final folders were created.
- No CSV/XLSX templates were created.
- Existing automation logic was not modified.
