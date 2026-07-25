# app/domain/value_objects/alert_policy.py
from dataclasses import dataclass


@dataclass(frozen=True)
class AlertPolicySettings:
    notify_unknown_person: bool = True
    escalate_repeated_detection: bool = True
    ignore_animals: bool = False
    loitering_seconds: int = 600
    repeated_detection_window_seconds: int = 900
    repeated_detection_count: int = 3