# Classic finite workflow acceptance: PASS

Run b1c46ce1e70740dc8afbf29b294e168c.
Design 2e33e2bad7e95f44181c71a66e49f54144d6c05aecfa9b58c72b48a1095813e9.
Snapshot b58c8cc496e6a466d10360c9b6d244e1677721986c5514a57580c5f71422d39f.

Coordinator /root closes the finite v2 trial on independent sentry delivery/frozen PASS and designer recommendation. This is not designer self-review. Actual model choices for all three roles were individually confirmed gpt-6.1-sol / medium.

- sentry /root/trial_classic_sentry: facts, independent design/delivery/frozen reviews.
- debater /root/trial_classic_debater: v1 design and v2 contract revision, advisory closure recommendation.
- laborer /root/trial_classic_laborer: sole source/test writer and actual selftests.

Source files: status_counts.py and test_status_counts.py. Source SHA256 values are recorded in the snapshot and each command record. Scope is exact builtin list/str input, four zero-inclusive status keys, validation errors/order, independent return values and input preservation.

Actual order: configuration -> facts -> v1 design and independent approval -> implementation and 9 tests -> independent delivery -> v1 freeze -> ordinary frozen checks PASS -> additional unhashable-string-subclass probe FAIL -> thaw -> v2 design and independent approval -> repair and 10 tests -> independent delivery -> new freeze -> independent final 10 tests/probe PASS -> coordinator final check -> scoped closure. All old designs, frozen copies and actual failures remain.

The v1 accepted-subclass case failed and never became a passing v1 case. V2 deliberately narrows the API to builtin list/str, rejects ordinary and unhashable subclasses explicitly, and keeps normal builtin behavior. This is a documented toy-interface revision rather than a hidden change to expected results.

Evidence index:
- design-v1.md / design-v2.md, design-hash-command.json / design-v2-hash-command.json
- design-review-v1.json / design-review-v2.json
- self-test/ and self-test-v2/: laborer evidence.json plus raw stdout.log/stderr.log
- delivery-unit.json / delivery-probe.json and delivery-v2-unit.json / delivery-v2-probe.json: independent actual command outputs
- frozen-v1-unit.json / frozen-v1-probe.json: successful limited v1 checks
- frozen-v1-subclass-failure.json and frozen-review-v1-correction.json: actual exit1 failure and corrected review
- frozen-v2-unit.json / frozen-v2-probe.json and frozen-review-v2-final.json: new exact-snapshot independent validation
- snapshots/: immutable v1/v2 scopes, manifests and source copies
- final-check-command.json: coordinator helper check exit0 (does not replace independent review)
- events.jsonl / run.json: dependency/state history and actual native collaboration task paths

Readonly sentry cannot write files: it executed readonly_capture.py and returned complete JSON stdout. Coordinator transcribed those actual outputs; source/copy hashes and command output fields are retained. Local records are not server authentication or an OS write lock. Before/after hashes do not rule out temporary restored changes. No claim of all workflow branches, arbitrary tasks or production readiness.
