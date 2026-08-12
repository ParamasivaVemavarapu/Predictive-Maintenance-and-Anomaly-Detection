import io
from pathlib import Path
import pandas as pd
from .analytics import analyze


class SensorStore:
    def __init__(self, path: str, contamination: float):
        self.contamination = contamination
        self._data = analyze(pd.read_csv(Path(path)), contamination)

    @property
    def data(self) -> pd.DataFrame:
        return self._data.copy()

    def replace(self, content: bytes) -> int:
        candidate = analyze(pd.read_csv(io.BytesIO(content)), self.contamination)
        self._data = candidate
        return len(candidate)
