import pytest
import pandas as pd
import numpy as np


@pytest.fixture(scope="session")
def data():
    np.random.seed(512)
    return pd.concat(
        [
            pd.DataFrame(
                {
                    "A": np.random.normal(0, 1, 100),
                    "B": np.random.normal(0, 1, 100),
                    "C": np.random.normal(0, 1, 100),
                    "group": ["X"] * 100,
                    "binary": np.random.choice([0, 1], 100, p=[0.7, 0.3]),
                }
            ),
            pd.DataFrame(
                {
                    "A": np.random.normal(0, 1, 100),
                    "B": np.random.normal(5, 2, 100),
                    "C": np.random.normal(1, 1, 100),
                    "group": ["Y"] * 100,
                    "binary": np.random.choice([0, 1], 100, p=[0.3, 0.7]),
                }
            ),
            pd.DataFrame(
                {
                    "A": np.random.normal(0, 1, 100),
                    "B": np.random.normal(0, 1, 100),
                    "C": np.random.normal(1, 1, 100),
                    "group": ["Z"] * 100,
                    "binary": np.random.choice([0, 1], 100, p=[0.5, 0.5]),
                }
            ),
        ]
    )
