from typing import Any

import numpy as np
import pandas as pd


def obj_to_dataframe(list_objs: list[Any]) -> pd.DataFrame:
    """returns a dataframe representing the attributes of the object as rows of the dataframe
    Requires a "to_dict" method for each object.
    """
    df_store = pd.DataFrame()
    for obj in list_objs:
        df_row = pd.DataFrame(obj.to_dict(), index=[0])
        df_store = pd.concat([df_store, df_row], axis=0, ignore_index=True)
    df_store = df_store.fillna(value=np.nan)
    df_store = df_store.dropna(axis=1, how='all')
    return df_store
