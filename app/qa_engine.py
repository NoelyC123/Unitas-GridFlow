import pandas as pd

def run_qa_checks(df, rules):
    issues = []

    for rule in rules:
        check = rule.get("check")
        field = rule.get("field")

        if field not in df.columns:
            issues.append({"Issue": f"Missing column: {field}", "Row": {}})
            continue

        if check == "unique":
            duplicates = df[df[field].duplicated()][field].tolist()
            for dup in duplicates:
                rows = df[df[field] == dup].to_dict(orient="records")
                for row in rows:
                    issues.append({"Issue": f"Duplicate value in '{field}': {dup}", "Row": row})

        elif check == "range":
            min_val = rule.get("min", float("-inf"))
            max_val = rule.get("max", float("inf"))
            out_of_range = df[(df[field] < min_val) | (df[field] > max_val)]
            for _, row in out_of_range.iterrows():
                issues.append({"Issue": f"{field} out of range ({min_val}-{max_val})", "Row": row.to_dict()})

        elif check == "required":
            missing = df[df[field].isnull() | (df[field] == "")]
            for _, row in missing.iterrows():
                issues.append({"Issue": f"Missing required field: {field}", "Row": row.to_dict()})

        else:
            issues.append({"Issue": f"Unknown check type: {check}", "Row": {}})

    return pd.DataFrame(issues)