Design proposal: `tally_statuses(statuses: list[str]) -> dict[str, int]`, implemented only in `status_counts.py`, with standard-library `unittest` coverage only in `test_status_counts.py`. Confidence: high.

Premises and evidence

- The sentry report supplied by root states that the designated workspace is empty, both proposed source files are absent, and Python 3.14.7 is available.
- There are no existing callers, fixtures, exports, or configuration to update.
- Authorized scope is the two named files. This design introduces no dependencies, command-line interface, persistence, or changes to the skill.

API contract

1. `statuses` must be a Python list; list subclasses are accepted. Other container types and arbitrary iterables are rejected with `TypeError`.
2. Every list element must be a string; string subclasses are accepted. A non-string element raises `TypeError`.
3. Valid strings are exactly `"pending"`, `"running"`, `"done"`, and `"failed"`, with case and whitespace significant. Any other string raises `ValueError`.
4. The return value is a newly allocated plain dictionary containing these four keys in this order: `"pending"`, `"running"`, `"done"`, `"failed"`. Each value is the nonnegative integer count of that status. Zero counts remain present.
5. Empty input returns all four keys with zero values.
6. Entries are checked in input order. The first invalid entry determines the exception. Exception messages should identify the offending index and the allowed status values or expected element type as applicable; exact message wording is not a public contract.
7. The function never modifies the supplied list, including when it raises. It does not retain the list or reuse a return dictionary across calls.
8. Type annotations document the interface; runtime validation enforces it.

Implementation recommendation

Use one function with a fresh four-key count dictionary, explicit container validation, and one pass over the list. For each element, validate its type, validate membership among the four statuses, and increment its count. Return the dictionary after the pass. No helper class, generic counting abstraction, exception wrapper, normalization, or additional public function is needed.

Meaningful unittest plan

- Empty list: assert exact equality with the four-key zero dictionary and verify key order.
- Mixed valid input: use repeated statuses with different counts, such as two pending, one running, three done, and one failed; assert the entire returned dictionary.
- Missing statuses: count repeated instances of one valid status and assert that the other three keys remain zero.
- Invalid strings: exercise an unknown name, the empty string, different case, and surrounding whitespace; each raises `ValueError`.
- Invalid element types: exercise `None`, an integer, a boolean, a list, and a dictionary as elements; each raises `TypeError`. The unhashable examples check that explicit validation handles them correctly.
- Invalid outer types: exercise `None`, a string, a tuple, a dictionary, and an iterator; each raises `TypeError`.
- Error precedence: a valid prefix followed by an unknown string and then a non-string must raise `ValueError`; reversing the invalid entries must raise `TypeError`.
- Input preservation: snapshot a valid list and invalid lists containing a valid prefix, invoke the function, and assert equal contents afterward, including after either exception type.
- Result independence: mutate one returned dictionary, call the function again, and verify the new result remains correct and is a distinct dictionary.

Standard-library `subTest` may group parallel invalid cases. Tests must assert expected results directly and must not derive expectations using the same counting loop as the implementation.

Independent verification strategy

1. Root records this exact design and computes its SHA256 Design ID.
2. An independent sentry reviews the design. Implementation starts only after that review reports PASS.
3. Laborer implements the two authorized files and runs `python -B -m unittest -v test_status_counts`; root retains the actual command, exit code, and output.
4. Independent sentry inspects the delivered source and tests, confirms the two-file scope, and runs the same unittest command plus a separate read-only `python -B -c` assertion probe covering a mixed result, zero keys, invalid input, and input preservation.
5. Root freezes the reviewed files using the evidence helper and the real Design ID. Independent sentry verifies the frozen file hashes and repeats the checks against those exact files. Root records raw logs, exit codes, hashes, and review results.
6. Final acceptance requires frozen verification PASS and no detected drift. Any subsequent source change requires a new freeze and independent verification.

Alternatives and unresolved matters

Accepting every iterable would require decisions about consumption, generators, and failures during iteration. Restricting the container to a list keeps this trial's contract small and makes preservation straightforward. Returning only observed keys would save initialization but would violate the required four-key output.

There are no unresolved design questions under the stated list-only contract. Root may submit this proposal directly for independent design review.

No files were changed or implementation checked. Tuple and generator inputs are intentionally rejected; callers must supply a list.
