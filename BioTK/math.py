import pandas as pd
import numpy as np

def dot(X, Y):
    """
    Dot product between two :class:`pandas.DataFrame` objects.

    First, aligns them properly, if necessary.
    """
    # TODO: make this properly handle various combinations
    # of DataFrames, Series, and arrays instead of just two dfs

    assert(isinstance(X, pd.DataFrame))
    assert(isinstance(Y, pd.DataFrame))

    Y, X = Y.align(X.T, axis=0, join="inner")
    X = X.T
    assert(X.shape[1] == Y.shape[0])
    return pd.DataFrame(np.dot(X.as_matrix(), Y.as_matrix()), 
            index=X.index, columns=Y.columns)
