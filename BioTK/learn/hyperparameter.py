"""
Smarter ways to find (an approximation to) optimal hyperparameters than grid
search. Intended for use with scikits-learn.
"""

# See also: scipy.optimize (minimize, anneal, basinhopping)
# I tried them without much success for this task

import numpy as np

from sklearn import metrics, cross_validation

class HyperparameterSearch(object):
    _bounds = {
            # SVM
            "nu": [-5, 0],
            "gamma": [-5, 0],
            "C": [-5, 2.5],
            # Linear model
            "alpha": [-5, 0],
            "l1_ratio": [-5, 0]
    }

    def __init__(self, model, params, scorer=metrics.mean_squared_error, cv=10, max_iter=100):
        self._model = model
        self._cv = cv
        self._max_iter = max_iter
        self._scorer = scorer
        self._params = params

    def fit(self, X, y):
        n = len(self._params)
        lower = np.array([self._bounds[k][0] for k in self._params])
        upper = np.array([self._bounds[k][1] for k in self._params])

        def within_bounds(x):
            return not ((x <= lower).any() or (x >= upper).any())

        def F(P):
            if not within_bounds(P):
                return 1e100
            P = 10 ** P
            param = dict(zip(self._params, P))
            try:
                model = self._model.set_params(**param)
                cv = []
                for i in range(3):
                    kf = cross_validation.KFold(X.shape[0], 
                            n_folds=self._cv, shuffle=True)
                    j = cross_validation.cross_val_score(self._model, 
                        X, y, scoring=self._scorer, cv=kf)
                    if np.any(np.isnan(j)):
                        return 1e100
                    cv.extend(j)
            except RuntimeError:
                return 1e100
            J = np.array(cv).mean()
            print("%0.3f @ %s" % (1 - J * 2, np.log10(P)))
            return J

        jmin, xmin = scatter_search(F, lower, upper)
        return jmin, 10 ** xmin

def scatter_search(F, lower, upper):
    """
    An approximation of the scatter search algorithm.
    """
    lower = np.array(lower)
    upper = np.array(upper)
    xs = np.zeros((0,len(lower)))
    js = np.zeros(0)

    for i in range(50):
        x = np.random.uniform(lower, upper)
        if len(lower) == 1:
            x = [x]
        xs = np.append(xs, [x], axis=0)
        js = np.append(js, F(xs[-1,:]))

    n = 10
    ix = js.argsort()[:n]
    js, xs = js[ix], xs[ix,:]

    k = 1.25
    b = 3

    print("** Starting local search ...")
    for i in range(25):
        ix = set()
        while len(ix) < b:
            ix.add(int(np.floor((1 - np.random.power(k)) * n)))
        ix = np.array(list(ix))
       
        worst = js.argsort()[-1]
        x = xs[ix,:].mean(axis=0)
        j = F(x)
        if j < js[worst]:
            js[worst] = j
            xs[worst] = x

        ix = js.argsort()
        js, xs = js[ix], xs[ix,:]

    best = js.argsort()[0]
    return js[best], xs[best]

def test():
    def F(x):
        return np.prod(x)

    scatter_search(F, [0, 1], [0, 10])
