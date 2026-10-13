# Requirements log

| ID | Category | Requirement | Component/package | Priority | Dependencies | Status | Acceptance criterion | Evidence/test | Follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | security | Missing authorization scope is rejected | `app/security` | P0 | Domain contracts | Implemented | `None` raises a validation error | Unit test to add when route layer is integrated | Wire into request dependencies |
| R-002 | evaluation | Unanswerable examples are excluded from recall | `evaluation/metrics` | P1 | Evaluation schema | Implemented | Empty relevant set raises | `tests/unit/test_evaluation_metrics.py` | Add report persistence |
| R-003 | architecture | Python does not generate user-facing answers | Service boundary | P0 | Java integration | Deferred | No generation adapter exists | Architecture review | Add contract tests |
