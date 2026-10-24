"""Voice Agent Evaluation Matrix & Quality Benchmark.

Multi-dimensional evaluation harness benchmarking voice agents across five critical
dimensions: Word Error Rate (WER), Intent Recognition Accuracy, Time to First Audio
Frame (TTFA), Barge-in Interruption Latency, and Obsolete Audio Leak Prevention.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class ConversationEvaluationRun:
    run_id: str
    ground_truth_text: str
    transcribed_text: str
    ground_truth_intent: str
    extracted_intent: str
    time_to_first_audio_ms: float
    barge_in_mute_latency_ms: float
    obsolete_audio_leak_detected: bool


class VoiceEvaluationHarness:
    """Evaluates conversational voice quality against operational thresholds."""

    def __init__(
        self,
        max_wer_threshold: float = 0.15,
        max_ttfa_ms: float = 1200.0,
        max_barge_in_latency_ms: float = 100.0,
    ) -> None:
        self.max_wer_threshold = max_wer_threshold
        self.max_ttfa_ms = max_ttfa_ms
        self.max_barge_in_latency_ms = max_barge_in_latency_ms

    @staticmethod
    def calculate_word_error_rate(reference: str, hypothesis: str) -> float:
        """Simplified Levenshtein word error rate."""
        ref_words = [w.strip(".,?!") for w in reference.lower().split() if w.strip(".,?!")]
        hyp_words = [w.strip(".,?!") for w in hypothesis.lower().split() if w.strip(".,?!")]
        if not ref_words:
            return 0.0 if not hyp_words else 1.0

        # Dynamic programming Levenshtein distance on words
        d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
        for i in range(len(ref_words) + 1):
            d[i][0] = i
        for j in range(len(hyp_words) + 1):
            d[0][j] = j

        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                if ref_words[i - 1] == hyp_words[j - 1]:
                    d[i][j] = d[i - 1][j - 1]
                else:
                    d[i][j] = min(
                        d[i - 1][j] + 1,  # deletion
                        d[i][j - 1] + 1,  # insertion
                        d[i - 1][j - 1] + 1,  # substitution
                    )
        return d[len(ref_words)][len(hyp_words)] / len(ref_words)

    def evaluate_run(self, run: ConversationEvaluationRun) -> Dict[str, Any]:
        wer = self.calculate_word_error_rate(run.ground_truth_text, run.transcribed_text)
        intent_match = run.ground_truth_intent == run.extracted_intent
        ttfa_ok = run.time_to_first_audio_ms <= self.max_ttfa_ms
        barge_in_ok = run.barge_in_mute_latency_ms <= self.max_barge_in_latency_ms
        no_leaks = not run.obsolete_audio_leak_detected

        passed_all = (
            wer <= self.max_wer_threshold
            and intent_match
            and ttfa_ok
            and barge_in_ok
            and no_leaks
        )

        return {
            "run_id": run.run_id,
            "passed_all": passed_all,
            "wer": round(wer, 3),
            "intent_match": intent_match,
            "ttfa_ok": ttfa_ok,
            "barge_in_ok": barge_in_ok,
            "no_leaks": no_leaks,
        }


def test_voice_evaluation() -> None:
    harness = VoiceEvaluationHarness(
        max_wer_threshold=0.15,
        max_ttfa_ms=1200.0,
        max_barge_in_latency_ms=100.0,
    )

    # Run 1: High quality conversational turn
    good_run = ConversationEvaluationRun(
        run_id="run_01_success",
        ground_truth_text="What are your hours on Saturday?",
        transcribed_text="what are your hours on saturday",
        ground_truth_intent="query_store_hours",
        extracted_intent="query_store_hours",
        time_to_first_audio_ms=850.0,
        barge_in_mute_latency_ms=45.0,
        obsolete_audio_leak_detected=False,
    )
    res_good = harness.evaluate_run(good_run)
    assert res_good["passed_all"] is True
    assert res_good["wer"] == 0.0

    # Run 2: Accurate transcript and intent, but defective barge-in and audio leak!
    bad_run = ConversationEvaluationRun(
        run_id="run_02_leak_failure",
        ground_truth_text="Cancel my appointment tomorrow",
        transcribed_text="cancel my appointment tomorrow",
        ground_truth_intent="cancel_appointment",
        extracted_intent="cancel_appointment",
        time_to_first_audio_ms=900.0,
        barge_in_mute_latency_ms=350.0,  # Failed: >100ms mute lag!
        obsolete_audio_leak_detected=True,  # Failed: Leaked old speech!
    )
    res_bad = harness.evaluate_run(bad_run)
    assert res_bad["passed_all"] is False
    assert res_bad["barge_in_ok"] is False
    assert res_bad["no_leaks"] is False

    print(
        f"Voice evaluation matrix verified: benchmark_passed={res_good['passed_all']}, "
        f"leak_failure_detected={not res_bad['passed_all']}"
    )


if __name__ == "__main__":
    test_voice_evaluation()
