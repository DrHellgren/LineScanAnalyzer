#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 09:29:01 2022
@author: kim
"""
import scipy
import numpy as np


def model_func(t, a, tau, offset):
    
    """A function of exponential decay that is used when estimating decay tau of calcium sparks
        Parameters
        ----------
        t : float
            time point at which the function is evaluated
        a : float
            a parameter controlling the function's maximum (not exclusively though, offset is also used)
        tau : float
            the exponential decay time constant
        offset : float
            the offset of the whole exponential decay over 0

        Returns
        -------
        : float
            the value of the exponential decay function at point t.
        """
    return a * np.exp(-t/tau) + offset


def fit_exp_nonlinear(t, y):
    """A function for fitting an exponential decay curve to data (usually the downstroke of a Ca spark).
       The equation of the decay used is a * np.exp(-t/tau) + offset.

        Parameters
        ----------
        t : numpy array
            time vector for the data
        y : numpy array
            a parameter controlling the function's maximum (not exclusively though, offset is also used)

        Returns
        -------
        a, tau, offset: float, float, float
            parameters of exponential decay function (a * np.exp(-t/tau) + offset) fit to the input data. When fitting fails (or there isn't enough data points), nans are returned.
        """
    try:
        opt_params, parm_cov = scipy.optimize.curve_fit(model_func, t, y, maxfev=10000)
        a, tau, offset = opt_params
        return a, tau, offset
    except ValueError:
        return np.nan, np.nan, np.nan
    except RuntimeError:
        return np.nan, np.nan, np.nan