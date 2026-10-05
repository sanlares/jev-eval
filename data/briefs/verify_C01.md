# Annotation brief: task C01

You are an expert human-quality annotator. For each text in `data/blind/C01.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: customer support tickets sent to a SaaS company
- Question: "Which team should handle this customer support ticket?"
- Options:
- `account_access`: Login problems, password resets, two-factor authentication, locked or suspended accounts, single sign-on issues
- `billing`: Charges, invoices, refunds, payment methods, receipts, plan prices
- `bug_report`: Something in the product is broken, throws errors, or behaves incorrectly
- `feature_request`: Asks for new functionality or an improvement to how the product works
- `cancellation`: Wants to cancel, close the account, stop auto-renewal, or leave the service

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C01.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C01` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).
