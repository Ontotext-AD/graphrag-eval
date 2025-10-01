import jsonlines
from pathlib import Path

def read_responses(path: Path) -> dict:
    with jsonlines.open(path) as reader:
        return {obj["question_id"]: obj for obj in reader}
