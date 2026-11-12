# CSV Check

Validate a UTF-8 CSV file locally before importing it. Requires Python 3.10+ and has no third-party dependencies.

    python csv_check.py example.csv --required id --unique id --date date --number total --json

Repeat a rule to check multiple columns. Multiple unique columns form one composite key. Dates must use YYYY-MM-DD and numbers must be finite. Reports identify physical input lines. Exit codes are 0 for clean data, 1 for validation issues, and 2 for file or CSV parsing errors.

The sample intentionally contains errors. Remove or fix the second data row to see a clean result.

## Proposed maintenance plan

- Months 1–2: Document supported imports, collect reproducible sample files, and add regression tests for multiline records and malformed input.
- Months 3–4: Triage public issues and use Codex to review fixes and test changes.
- Months 5–6: Benchmark large inputs, document practical limits, and publish a release with a changelog.

## Reuse an import schema

    python csv_check.py example.csv --schema schema.json --json

Keep the schema with your import job to apply the same rules to every batch. CLI rules
extend schema rules. The JSON report can be redirected to a file by your shell.
Malformed CSV and invalid schema files exit with code 2 and write an error to stderr.
