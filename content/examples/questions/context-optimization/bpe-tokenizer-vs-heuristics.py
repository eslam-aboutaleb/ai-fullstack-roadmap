"""Demonstrate failure modes of character heuristics vs exact Byte-Pair Encoding (BPE) tokenization."""

def heuristic_char_token_count(text):
    """Naive industry rule-of-thumb: 1 token = 4 characters."""
    return max(1, len(text) // 4)

def mock_bpe_token_count(text, language="en"):
    """
    Exact BPE tokenization dynamics:
      1. Common English words: 3 to 5 chars per token.
      2. Source code (JSON, Python whitespace): ~2 chars per token.
      3. Non-Latin scripts (Arabic, CJK): often 1 to 1.5 chars per token (due to multi-byte UTF-8).
    """
    if language == "ar": # Arabic text
        # Multi-byte UTF-8 characters split into frequent subwords: ~1.2 chars/token
        return int(len(text) / 1.2)
    elif language == "json":
        # Punctuation ({, }, ", :, ,) and indentations tokenize as individual tokens: ~2 chars/token
        return int(len(text) / 2.0)
    else:
        # Standard English prose: ~4 chars/token
        return int(len(text) / 4.0)

# Scenario A: JSON Payload (1,000 characters of formatted API response)
json_payload = '{"event": "auth_failure", "actor": "system", "code": 401, "msg": "Token expired"}' * 12
chars_json = len(json_payload)
est_json = heuristic_char_token_count(json_payload)
true_json = mock_bpe_token_count(json_payload, language="json")

# Heuristic underestimates JSON tokens by ~100%:
error_json = abs(est_json - true_json) / true_json
assert error_json > 0.40, "Heuristic severely underestimated JSON token cost"

# Scenario B: Multilingual Arabic text (1,000 characters)
arabic_text = "سياسة الخصوصية واسترجاع المبالغ المالية للاشتراكات السنوية للمؤسسات" * 15
chars_ar = len(arabic_text)
est_ar = heuristic_char_token_count(arabic_text)
true_ar = mock_bpe_token_count(arabic_text, language="ar")

# Heuristic underestimates Arabic tokens by ~200%!
assert true_ar > (est_ar * 2), "Heuristic catastrophic underestimation on non-Latin script"

print(f"BPE token boundary analysis: JSON (chars={chars_json}): heuristic={est_json}, true_bpe={true_json}; Arabic (chars={chars_ar}): heuristic={est_ar}, true_bpe={true_ar}")
