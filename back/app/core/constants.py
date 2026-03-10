from __future__ import annotations

ROUND_SEQUENCE: list[int] = [1, 3, 2, 1, 3, 2]
TOTAL_ROUNDS: int = 6

NINE_CLASSES: list[str] = [
    "High Prime",
    "Average Prime",
    "Low Prime",
    "High Choice",
    "Average Choice",
    "Low Choice",
    "High Select",
    "Low Select",
    "High Standard",
]

FOUR_CLASSES: list[str] = ["Prime", "Choice", "Select", "Standard"]

# 9-class → 4-class marbling category
CLASS_TO_MARBLING: dict[str, str] = {
    "High Prime": "Prime",
    "Average Prime": "Prime",
    "Low Prime": "Prime",
    "High Choice": "Choice",
    "Average Choice": "Choice",
    "Low Choice": "Choice",
    "High Select": "Select",
    "Low Select": "Select",
    "High Standard": "Standard",
}

# 4-class → representative 9-class (used when only marbling_class is known)
MARBLING_TO_REPRESENTATIVE: dict[str, str] = {
    "Prime": "Average Prime",
    "Choice": "Average Choice",
    "Select": "High Select",
    "Standard": "High Standard",
}
