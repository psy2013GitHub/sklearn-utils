
#-*- encoding: utf8 -*-

from __future__ import division

__author__ = 'flappy'

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import numpy as np
from scipy import optimize
from functools import partial
from sklearn.linear_model.logistic import LogisticRegression, _multinomial_loss, _logistic_loss, _logistic_loss_and_grad
from sklearn.utils.extmath import safe_sparse_dot, logsumexp

# 主要为了解决上溢，因为上溢 => phi(z) = 1/(1+exp(z)) == 0 => log(phi(z)) 无意义

class Sigmoid:

    @staticmethod
    def raw(z):
        '''
            实际上, exp(300)就已经上溢出了, 所以此种办法比较天真
        '''
        return 1.0 / (1.0 + np.exp(-z))

    @staticmethod
    def scipy_stable(z, out=None):
        '''
            来自sklearn，更快更稳定
        '''
        try:
            from scipy.special import expit     # SciPy >= 0.10
            with np.errstate(invalid='ignore', over='ignore'):
                if np.isnan(expit(1000)):       # SciPy < 0.14
                    raise ImportError("no stable expit in scipy.special")
            return expit(z, out=out)
        except ImportError:
            """Logistic sigmoid function, ``1 / (1 + exp(-x))``.

            See sklearn.utils.extmath.log_logistic for the log of this function.
            """
            if out is None:
                out = np.empty(np.atleast_1d(z).shape, dtype=np.float64)
            out[:] = z

            # 1 / (1 + exp(-x)) = (1 + tanh(x / 2)) / 2
            # This way of computing the logistic is both fast and stable.
            out *= .5
            np.tanh(out, out)
            out += 1
            out *= .5
            print 'out:', out
            return out.reshape(np.shape(z))

    @staticmethod
    def fabian_stable(z):
        '''
        sklearn 训练采用得办法, 避免上溢
        if z > 0, 1.0/(1.0 + exp(-z))
        if z < 0, exp(z)/(1.0 + exp(z))
        来自http://fa.bianp.net/blog/2013/numerical-optimizers-for-logistic-regression/，
        '''
        out = np.empty_like(z)
        idx = z > 0
        out[idx] = Sigmoid.raw(z[idx])
        out[~idx] = np.exp(z[~idx])/(1.0 + np.exp(z[~idx]))
        return out

    @staticmethod
    def call(method, z):
        func = getattr(Sigmoid, method, None)
        if not func:
            raise NotImplementedError('sigmoid: %s' % method)
        return func(z)

class LogSigmoid:
    '''
        log of sigmoid
    '''

    @staticmethod
    def raw(Z):
        return np.log(Sigmoid.call('raw', Z))

    @staticmethod
    def fabian_stable(z):
        '''
            if z > 0, -log(1.0 + exp(-z))
            if z < 0, log(exp(z)/(1.0 + exp(z))) = z - log(1.0 + exp(z))
        来自http://fa.bianp.net/blog/2013/numerical-optimizers-for-logistic-regression/，
        '''
        out = np.empty_like(z)
        idx = z > 0
        out[idx] = -np.log(1.0 + np.exp(-z[idx]))
        out[~idx] = z[~idx] - np.log(1.0 + np.exp(z[~idx]))
        return out

    @staticmethod
    def call(method, Z):
        func = getattr(LogSigmoid, method, None)
        if not func:
            raise NotImplementedError('logsigmoid: %s' % method)
        return func(Z)

class LogLogitSum:

    @staticmethod
    def raw(Z, weight):
        return np.sum(weight * LogSigmoid.call('raw', Z))

    @staticmethod
    def fabian_stable(Z, weight):
        return np.sum(weight * LogSigmoid.call('fabian_stable', Z))

    @staticmethod
    def call(method, Z, weight):
        func = getattr(LogLogitSum, method, None)
        if not func:
            raise NotImplementedError('logsum: %s' % method)
        return func(Z, weight)

class NaiveLR:

    '''
        可以选择不考虑数值稳定性版本 --
        !!! 注意：
                目前只实现了L2 cost版本，好像只有了liblinear实现了L1.
                目前只实现了二分类版本.
    '''
    def __init__(self, sigmoid_method='raw', logsum_method='raw'):
        self.sigmoid_method = sigmoid_method
        self.logsum_method = logsum_method

    def check_y(self, Y):
        labels = np.unique(Y)
        assert len(labels)==2 and -1 in labels and 1 in labels, 'invalid y: %s' % labels

    def fit(self, X, Y, alpha=0, sample_weight=None,
            solver='SLSQP', constraints=(), options={}):

        self.check_y(Y)

        theta = np.zeros(X.shape[1] + 1) # !!! don't forget intercept, random init
        print 'init theta:', ','.join([str(_) for _ in theta])

        if sample_weight is not None:
            self.sample_weight = np.array(sample_weight, dtype=np.float64, order='C')
        else:
            self.sample_weight = np.ones(X.shape[0])

        args = (X, Y, alpha)
        func = self._logistic_loss
        grad = self._logistic_grad
        if solver=='lbfgs':
            func = lambda *args: (NaiveLR._logistic_loss(*args), NaiveLR._logistic_grad(*args))
            w0, loss, info = optimize.fmin_l_bfgs_b(
                    func, theta, fprime=None,
                    args=(X, Y, alpha),
                    iprint=options['disp'])
            self.coef_, self.intercept_ = w0[:-1], w0[-1]
        else:
            res = optimize.minimize(func, theta, jac=grad, args=args, method=solver, constraints=constraints, options=options)
            self.coef_, self.intercept_ = res.x[:-1], res.x[-1]

        self.is_fit = True
        return self.coef_

    def _logistic_loss(self, theta, X, Y, alpha=0):
        w, b = theta[:-1], theta[-1]
        dot = safe_sparse_dot(X, w)
        Z = Y * (dot + b)
        llh = LogLogitSum.call(self.logsum_method, Z, self.sample_weight) # loglikelyhood
        return -llh + alpha * w.dot(w)

    def _logistic_grad(self, theta, X, Y, alpha=0):
        w, b = theta[:-1], theta[-1]
        grad, n_features = np.empty_like(theta), len(w)
        dot = safe_sparse_dot(X, w)
        Z = Y * (dot + b)
        P = Sigmoid.call(self.sigmoid_method, Z)
        grad[:n_features] = X.T.dot(Y * (P - 1) * self.sample_weight) + 0.5 * alpha * w
        grad[-1] = np.sum(Y * (P - 1) * self.sample_weight)
        return grad

    def predict_proba(self, X, sigmoid_method='raw'):
        Z = safe_sparse_dot(X, self.coef_) + self.intercept_
        P = Sigmoid.call(sigmoid_method, Z)
        return P

    def predict(self, X, sigmoid_method='raw'):
        P = self.predict_proba(X, sigmoid_method=sigmoid_method)
        P[P<0.5] = -1
        P[P>=0.5] = 1
        return P

    def _predict_proba_lr(self, X):
        """
        从sklearn拷贝而来，便于对比
        """
        Z = safe_sparse_dot(X, self.coef_) + self.intercept_
        Z *= -1
        np.exp(Z, Z)
        Z += 1
        np.reciprocal(Z, Z)
        return Z

class LR(LogisticRegression):

    # !!! suppose y in {-1, 1}

    def __init__(self):
        super(LogisticRegression, self).__init__()
        self.is_fit = False
        self.eps = np.finfo(np.float64).eps
        print 'eps:', self.eps

    def fit(self, X, Y, alpha=0, sample_weight=None,
            sigmoid_method='fabian_stable',
            solver='SLSQP', constraints=(), options={'maxiter': 1, 'disp': True}
        ):
        '''
            如果solver为None，默认使用sklearn
        '''

        if solver is None: # 直接代理调用sklearn，然后copy代理
            proxy = LogisticRegression(solver='sag', max_iter=options['maxiter'])
            proxy.fit(X, Y) # fixme for C
            for k in dir(proxy):
                try:
                    setattr(self, k, getattr(proxy, k))
                except Exception, e:
                    pass
            return

        self.is_fit = False
        self.classes_ = np.unique(Y)
        theta = np.random.random(X.shape[1] + 1) # !!! don't forget intercept, random init
        theta = np.zeros(X.shape[1] + 1) # !!! don't forget intercept, random init
        print 'init theta:', ','.join([str(_) for _ in theta])

        if sample_weight is not None:
            sample_weight = np.array(sample_weight, dtype=np.float64, order='C')
        else:
            sample_weight = np.ones(X.shape[0])

        args = (X, Y, alpha, sample_weight)
        func = _logistic_loss
        grad = lambda x, *args: _logistic_loss_and_grad(x, *args)[1]
        print 'solver:', solver
        res = optimize.minimize(func, theta, jac=grad, args=args, method=solver, constraints=constraints, options=options)

        self.coef_, self.intercept_ = res.x[:-1], res.x[-1]
        self.coef_.shape = 1, self.coef_.shape[0]
        self.is_fit = True
        return res

if __name__ == '__main__':
    pass