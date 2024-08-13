from typing import Any

import numpy as np
import pandas as pd


def obj_to_dataframe(list_objs: list[Any]) -> pd.DataFrame:
    """Returns a dataframe representing the attributes of the object as rows of the dataframe.

    Requires a "to_dict" method for each object.
    """
    df_store = pd.DataFrame([x.to_dict(add_iso_date=True) for x in list_objs])
    df_store = df_store.fillna(value=np.nan)
    df_store = df_store.dropna(axis=1, how='all')
    return df_store
