"""Column-wise PDF extraction scrambles a table; keep rows with headers and provenance."""
import re

flattened = "Coverage type Maximum amount Hospitalization Dental $100,000 $5,000"


def naive_amount_after(label, text):
    after = text.split(label, 1)[1]
    return re.search(r"\$[\d,]+", after).group()


table = {
    "table_id": "benefits-1", "page": 3,
    "columns": ["Coverage type", "Maximum amount"],
    "rows": [["Hospitalization", "$100,000"], ["Dental", "$5,000"]],
}


def row_chunks(t):
    for row in t["rows"]:
        fields = " | ".join(f"{c}: {v}" for c, v in zip(t["columns"], row))
        yield {"text": fields, "table_id": t["table_id"], "page": t["page"]}


chunks = list(row_chunks(table))
structured = next(c["text"] for c in chunks if c["text"].startswith("Coverage type: Dental"))
assert naive_amount_after("Dental", flattened) == "$100,000"
assert structured.endswith("$5,000")
print("naive", naive_amount_after("Dental", flattened), "structured", structured, chunks[1]["page"])
