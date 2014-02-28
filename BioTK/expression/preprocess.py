import pandas as pd
import numpy as np

def quantile_normalize(X):
    """
    Quantile normalize a DataFrame, where samples are columns and probes/genes
    are rows.
    """
    X_n = X.copy().as_matrix()
    mu = X.T.mean()
    mu.sort()
    for j in range(X.shape[1]):
        ix = np.array(X.iloc[:,j].argsort())
        X_n[ix,j] = mu
    return pd.DataFrame(X_n, index=X.index, 
            columns=X.columns)
