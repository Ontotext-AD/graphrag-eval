def compute_f1(recall: float | str | None, precision: float | str | None) -> float | None:
    if recall is None or precision is None:
        return None
    recall = float(recall)
    precision = float(precision)
    if recall == 0.0 and precision == 0.0:
        return 0.0
    return 2 * (recall * precision) / (recall + precision)


def get_f1_dict(
    input_dict: dict,
    prefix: str
) -> dict:
    recall = input_dict.get(f"{prefix}_recall")
    precision = input_dict.get(f"{prefix}_precision")
    f1 = compute_f1(recall, precision)
    if f1 is None:
        return {}
    return {f"{prefix}_f1": f1}
