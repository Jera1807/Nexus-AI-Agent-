from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CalibrationReport:
    total: int
    false_escalations: int
    false_passes: int
    current_low_conf_threshold: float
    recommended_low_conf_threshold: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "false_escalations": self.false_escalations,
            "false_passes": self.false_passes,
            "current_low_conf_threshold": self.current_low_conf_threshold,
            "recommended_low_conf_threshold": self.recommended_low_conf_threshold,
        }


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return bool(value)


def analyze_decisions(records: list[dict[str, Any]], current_low_conf_threshold: float = 0.35) -> CalibrationReport:
    false_escalations = 0
    false_passes = 0

    for row in records:
        expected = row.get("expected_intent")
        predicted = row.get("predicted_intent")
        escalated = _safe_bool(row.get("escalated", False))
        confidence = float(row.get("confidence", 0.0))

        wrong_prediction = expected is not None and predicted is not None and expected != predicted

        # escalated even though model looked confident and matched expected intent
        if escalated and not wrong_prediction and confidence >= current_low_conf_threshold:
            false_escalations += 1

        # not escalated even though prediction wrong and low confidence
        if (not escalated) and wrong_prediction and confidence < current_low_conf_threshold:
            false_passes += 1

    # simple heuristic: adjust by error imbalance
    delta = (false_passes - false_escalations) * 0.01
    recommended = max(0.1, min(0.9, current_low_conf_threshold + delta))

    return CalibrationReport(
        total=len(records),
        false_escalations=false_escalations,
        false_passes=false_passes,
        current_low_conf_threshold=current_low_conf_threshold,
        recommended_low_conf_threshold=round(recommended, 3),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate confidence threshold from decision logs")
    parser.add_argument("--input", required=True, help="Path to JSON file containing decision records")
    parser.add_argument("--output", default="calibration_report.json")
    parser.add_argument("--current-threshold", type=float, default=0.35)
    args = parser.parse_args()

    records = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Input JSON must be a list of decision log rows")

    report = analyze_decisions(records, current_low_conf_threshold=args.current_threshold)
    out_path = Path(args.output)
    out_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Calibration report written to {out_path}")
    print(
        f"False escalations: {report.false_escalations}, false passes: {report.false_passes}, "
        f"recommended threshold: {report.recommended_low_conf_threshold}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
