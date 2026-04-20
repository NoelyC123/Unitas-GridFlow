import pandas as pd


def _is_missing_value(series: pd.Series) -> pd.Series:
    if series.dtype == "object":
        return series.isnull() | (series.astype(str).str.strip() == "")
    return series.isnull()


def run_qa_checks(df, rules):
    issues = []

    for rule in rules:
        check = rule.get("check")
        field = rule.get("field")

        if field not in df.columns:
            issues.append({"Issue": f"Missing column: {field}", "Row": {}})
            continue

        if check == "unique":
            duplicate_mask = df[field].duplicated(keep="first")
            duplicates = df.loc[duplicate_mask, field].tolist()

            for dup in duplicates:
                rows = df[df[field] == dup].to_dict(orient="records")
                for row in rows:
                    issues.append({"Issue": f"Duplicate value in '{field}': {dup}", "Row": row})

        elif check == "range":
            min_val = rule.get("min", float("-inf"))
            max_val = rule.get("max", float("inf"))

            numeric_series = pd.to_numeric(df[field], errors="coerce")
            out_of_range = df[
                numeric_series.notna() & ((numeric_series < min_val) | (numeric_series > max_val))
            ]

            for _, row in out_of_range.iterrows():
                issues.append(
                    {
                        "Issue": f"{field} out of range ({min_val}-{max_val})",
                        "Row": row.to_dict(),
                    }
                )

        elif check == "required":
            missing = df[_is_missing_value(df[field])]

            for _, row in missing.iterrows():
                issues.append({"Issue": f"Missing required field: {field}", "Row": row.to_dict()})

        elif check == "allowed_values":
            allowed = rule.get("values", [])

            invalid = df[~_is_missing_value(df[field]) & ~df[field].isin(allowed)]

            for _, row in invalid.iterrows():
                issues.append(
                    {
                        "Issue": f"Invalid value for '{field}': {row[field]}",
                        "Row": row.to_dict(),
                    }
                )

        else:
            issues.append({"Issue": f"Unknown check type: {check}", "Row": {}})

    return pd.DataFrame(issues)
