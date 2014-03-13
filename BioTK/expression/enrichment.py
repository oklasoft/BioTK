"""
Analysis of gene/transcript sets.

Includes, (or could include), methods such as (GO or other ontology)
enrichment analysis, GSEA, rotation gene set analysis, etc.
"""

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

import BioTK.expression

def roast_lite(X, C, p_grp, n_perm=100):
    """
    Like limma roast, except computes p-value by permuting samples
    instead of rotation set analysis (more sensitive, TODO).

    X : :class:`pandas.DataFrame`
        Expression matrix - transcripts (rows) vs samples (columns)
    C : :class:`pandas.DataFrame`
        Coefficient matrix - transcripts (rows) vs terms (columns)
    """
    # FIXME: use a contrast vector instead of p_grp
    p_grp = p_grp.copy()
    X, C = X.align(C, axis=0, join="inner")
    Xm = X.as_matrix()

    n = C.apply(lambda x: np.abs(x).sum())

    def t_stat(p_grp):
        ix = p_grp.as_matrix()
        t = ttest_ind(Xm[:,ix], Xm[:,~ix], axis=1)[0]
        t = pd.Series(t, index=X.index)
        return (C.T * t).sum(axis=1) / n

    y_true = t_stat(p_grp)
    y_perm = []
    for i in range(n_perm):
        np.random.shuffle(p_grp)
        y_perm.append(t_stat(p_grp))
    y_perm = pd.DataFrame(y_perm)

    p_up = (y_true >= y_perm).mean()
    p_down = (y_true <= y_perm).mean()
    return pd.DataFrame({
        "n": (C != 0).sum(axis=0),
        "t": y_true,
        "p Up" : p_up,
        "p Down" : p_down,
    }).ix[:,["n","t","p Up","p Down"]].sort("t")
