"""
Differential expression algorithms.
"""

from collections import namedtuple

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm

from scipy.optimize import minimize
from scipy.interpolate import interp1d
from scipy.stats import ttest_ind
from statsmodels.sandbox.stats.multicomp import multipletests

DifferentialExpressionResult = namedtuple("DifferentialExpressionResult",
        "coef,summary")

def AOV(X, P, formula):
    # FIXME: ensure alignment of X and P
    design = patsy.dmatrix(formula, P)
    coef = []
    summary = []

    genes = X.index[:3]
    for gene in genes:
        model = sm.OLS(X.ix[gene,:], design)
        fit = model.fit()
        coef.append(tuple(fit.params.tolist()))
        summary.append((fit.f_pvalue,))

    coef = pd.DataFrame.from_records(coef,
            index = genes,
            columns = design.design_info.column_names)
    summary = pd.DataFrame.from_records(summary,
            index = genes,
            columns = ["P-Value"])

    return DifferentialExpressionResult(coef, summary)

def fold_change(X, group, log=2):
    """
    Find the fold change between two groups in an expression matrix.
    """
    # FIXME: check for negative numbers in X
    fc = (X.ix[:,group].mean(axis=1) / 
            X.ix[:,(~group)].mean(axis=1)).fillna(0)
    if not log:
        return fc
    return np.log(fc) / np.log(log)
 
def t_test(X, group):
    """
    Simple two-group comparison with (unpaired) t-test. 
    """
    R = pd.DataFrame.from_records([], index=X.index)
    R["logFC"] = fold_change(X, group, log=2)
    R["logFC"] = R["logFC"].fillna(0)
    Xm = X.as_matrix()
    ix = group.as_matrix()
    t, p = ttest_ind(Xm[:,ix], Xm[:,~ix], axis=1)
    R["t"] = t
    R["p"] = p
    R["FDR"] = multipletests(R["p"], method="fdr_bh")[1]
    return R

def SAM(X, group, fdr_cutoff=0.1):
    """
    Significance Analysis of Microarrays.

    X: an expression matrix with genes as rows and samples as columns
    group: a boolean pandas Series, the same length as X has columns,
        indicating which of two groups each sample falls into.
    """
    assert group.dtype == bool
    assert len(group) == X.shape[1]
    # FIXME: detect situations where an entire row could be zero
    X = X.copy() - X.min()

    def D(s0, X, group):
        n = group.value_counts()
        n1,n2 = n[True], n[False]
        mu = X.T.groupby(group).mean().T
        s = ((X.ix[:,group].T.var() + X.ix[:,~group].T.var()) * \
            ((1/n1 + 1/n2) / (n1 + n2 - 2))) ** 0.5
        d = (mu[True] - mu[False]) / (s + s0)
        return d

    def F(s0, X, group):
        d = D(s0, X, group)
        # Should this be abs?
        return abs(d.std() / d.mean())

    # Choose the s0 minimizing the coefficient of variation of d
    res = minimize(F, 0, (X, group,))
    s0 = res.x[0]

    # Permute the labels to estimate FDR

    # This is the lazy way out; instead of choosing
    # "balanced" label permutations only, we just do a lot
    # of permutations and let the law of large numbers handle it
    # Probably this will make the test slightly less powerful
    n_perm = 100
    d_perm = np.zeros((X.shape[0], n_perm))
    ix = group.copy()
    for i in range(n_perm):
        np.random.shuffle(ix)
        d_p = D(s0, X, ix)
        d_p.sort()
        d_perm[:,i] = d_p.as_matrix()
    d_exp = d_perm.mean(axis=1)
    
    def FDR(delta):
        return (np.abs(d_perm.T - d_exp) >= delta).T.mean()

    # Find delta matching the chosen FDR using binary search
    deltas, fdrs = [0,1000], [1,0]
    delta = 100
    dx = delta / 2
    eps = 0.01
    fdr = FDR(delta)
    while abs(fdr_cutoff - fdr) > eps and (dx > 0.001):
        fdrs.append(fdr)
        deltas.append(delta)
        fdr = FDR(delta)
        delta += dx * (1 if fdr > fdr_cutoff else -1)
        dx /= 2
    while fdr > fdr_cutoff:
        fdrs.append(fdr)
        deltas.append(delta)
        delta -= dx
        fdr = FDR(delta)
    deltas, fdrs = np.array(deltas), np.array(fdrs)
    ix = deltas.argsort()
    delta_to_fdr = interp1d(deltas[ix], fdrs[ix])#, kind="cubic")

    # Return significant genes 
    result = pd.DataFrame.from_records([],index=X.index)
    result["logFC"] = fold_change(X, group, log=2)
    result["CV"] = X.std(axis=1) / X.mean(axis=1)
    d = D(s0, X, group)
    d.sort()
    result["delta"] = (d - d_exp).ix[result.index]
    result["q"] = delta_to_fdr(np.abs(result["delta"]))
    sig = result["q"] < fdr_cutoff
    result["change"] = "Unchanged"
    result["change"][sig & (result["logFC"] > 0)] = "Up"
    result["change"][sig & (result["logFC"] < 0)] = "Down"
    return result.sort("delta")

def differential_expression_simple(X, group, method="t_test", 
        correction="BH", annotation=None):
    """
    A simple two-group differential expression comparison.
    """
    # annotation will either be a DataFrame or a GEO accession string 
    assert isinstance(annotation, pd.DataFrame)

#def differential_expression( ... X, model & contrast matrices ...
