import argparse
import csv
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


def validate(source, required, dates, numbers, unique):
    reader = csv.reader(source, strict=True)
    header = next(reader, [])
    if not header or any(not name.strip() for name in header):
        return [{"line": 1, "error": "Missing or blank column header"}]
    if len(header) != len(set(header)):
        return [{"line": 1, "error": "Duplicate column headers"}]
    missing = sorted(set(required + dates + numbers + unique) - set(header))
    if missing:
        return [{"line": 1, "error": "Missing columns", "columns": missing}]

    issues = []
    seen = set()
    previous_line = reader.line_num
    for row in reader:
        line = previous_line + 1
        previous_line = reader.line_num
        if len(row) != len(header):
            issues.append({"line": line, "error": "Wrong number of fields"})
            continue
        values = dict(zip(header, row))
        for name in required:
            if not values[name].strip():
                issues.append({"line": line, "column": name, "error": "Required value is blank"})
        for name in dates:
            value = values[name].strip()
            try:
                if date.fromisoformat(value).isoformat() != value:
                    raise ValueError
            except ValueError:
                issues.append({"line": line, "column": name, "error": "Expected YYYY-MM-DD"})
        for name in numbers:
            try:
                if not Decimal(values[name].strip()).is_finite():
                    raise InvalidOperation
            except InvalidOperation:
                issues.append({"line": line, "column": name, "error": "Expected a finite number"})
        if unique:
            key = tuple(values[name] for name in unique)
            if key in seen:
                issues.append({"line": line, "columns": unique, "error": "Duplicate key"})
            seen.add(key)
    return issues


def read_schema(path):
    schema = json.loads(path.read_text(encoding="utf-8-sig"))
    rules = {"required", "date", "number", "unique"}
    if not isinstance(schema, dict) or schema.keys() - rules:
        raise ValueError("Schema must be an object with required, date, number, or unique rules.")
    for rule, columns in schema.items():
        if not isinstance(columns, list) or any(
            not isinstance(column, str) or not column.strip() for column in columns
        ):
            raise ValueError(f"Schema rule {rule} must be a list of nonblank column names.")
    return schema


def main():
    parser = argparse.ArgumentParser(description="Check CSV data before importing it.")
    parser.add_argument("file")
    parser.add_argument("--required", action="append", default=[])
    parser.add_argument("--date", action="append", default=[], metavar="COLUMN")
    parser.add_argument("--number", action="append", default=[], metavar="COLUMN")
    parser.add_argument("--unique", action="append", default=[], metavar="COLUMN")
    parser.add_argument("--schema", type=Path, help="Read reusable rules from a JSON file.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        schema = read_schema(args.schema) if args.schema else {}
        rules = [
            list(dict.fromkeys(schema.get(rule, []) + getattr(args, rule)))
            for rule in ("required", "date", "number", "unique")
        ]
        with open(args.file, encoding="utf-8-sig", newline="") as source:
            issues = validate(source, *rules)
    except (OSError, ValueError, csv.Error) as error:
        print(error, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        for issue in issues:
            fields = [issue["column"]] if "column" in issue else issue.get("columns", [])
            details = f" ({', '.join(fields)})" if fields else ""
            print(f"Line {issue['line']}: {issue['error']}{details}")
        if not issues:
            print("No issues found.")
    return int(bool(issues))


if __name__ == "__main__":
    sys.exit(main())

