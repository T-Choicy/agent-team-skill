# Classic minimal trial: design v2 addendum

Author: /root/trial_classic_debater. This addendum references and supersedes clauses 1–3 and subclass test expectations in design-v1.md (Design ID 015d210da5b7ee08850a4c3696c778024f7058ecb40aa21310bb42bbbe8559f6). All other v1 requirements remain unchanged. Authorized source files remain status_counts.py and test_status_counts.py.

Design v2 addendum: require **exact built-in `list` and `str` types**. This explicitly narrows v1's subclass acceptance. Confidence: high.

The frozen failure establishes that v1's promise to accept string subclasses was broader than its implementation: a valid-looking string subclass can disable hashing and fail dictionary membership. Supporting arbitrary subclasses would also require a policy for overridden equality, hashing, iteration, and other behavior. This toy API does not need that flexibility.

Replace v1 API clauses 1–3 with:

1. `statuses` must have exact built-in type `list`. A list subclass or any other input type raises `TypeError`.
2. Every element must have exact built-in type `str`. String subclasses and all other element types raise `TypeError`, before dictionary membership or counting.
3. Accepted strings remain exactly `"pending"`, `"running"`, `"done"`, and `"failed"`. Other built-in strings raise `ValueError`.

All other v1 requirements remain unchanged, including four output keys, zero counts, validation order, fresh output, and preservation of caller input on success and failure. Keep implementation within `status_counts.py` and `test_status_counts.py`.

Regression requirements:

- A `str` subclass with `__hash__ = None`, instantiated with `"done"`, raises the explicitly required `TypeError`; its input list remains unchanged.
- An ordinary hashable `str` subclass containing `"done"` also raises `TypeError`, proving subclass rejection is intentional and consistent.
- A `list` subclass containing a valid built-in string raises `TypeError`.
- Built-in `["done"]` still returns all four keys with the correct counts.

The independent probe must assert these v2 outcomes explicitly. A raw dictionary-generated `TypeError` alone is insufficient evidence: independent inspection must verify that exact-type validation precedes membership, and the ordinary hashable-subclass regression must pass.

Preserve v1's design, snapshot, failed probe, and prior limited PASS records. After independent v2 design PASS, laborer may repair the two files in the already thawed state. Acceptance requires a new snapshot linked to the v2 Design ID and independent verification of that snapshot.

Author clarification: preserve all existing tests except the subclass-acceptance expectations. Revise those expectations to require explicit `TypeError` rejection of both list and string subclasses. Add the unhashable string-subclass regression and the built-in `["done"]` control. Preserve input-unchanged assertions. Keep the original v1 tests and results in historical evidence; working v2 tests reflect the documented contract change.

No source changes were performed by the designer. This deliberate compatibility change rejects subclasses that v1 promised to accept; ordinary built-in inputs retain their behavior.
