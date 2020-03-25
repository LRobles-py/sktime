__all__ = [
    "check_y",
    "check_X",
    "check_y_X",
    "check_fh",
    "check_cv",
    "check_window_length",
    "check_step_length",
    "check_time_index",
    "check_consistent_time_index",
    "check_alpha",
    "check_is_fitted_in_transform"
]
__author__ = ["Markus Löning", "@big-o"]

import numpy as np
import pandas as pd

from sktime.utils.validation import check_is_fitted
from sktime.utils.validation import is_int


def check_y_X(y, X):
    """Validate input data.
    Parameters
    ----------
    y : pandas Series or numpy ndarray
    X : pandas DataFrame
    Returns
    -------
    None
    Raises
    ------
    ValueError
        If y is an invalid input
    """
    y = check_y(y)
    X = check_X(X)
    check_consistent_time_index(y, X)
    return y, X


def check_y(y, allow_empty=False, allow_constant=True):
    """Validate input data.
    Parameters
    ----------
    y : pd.Series
    allow_empty : bool, optional (default=False)
        If True, empty `y` does not raise an error.
    allow_constant : bool, optional (default=True)
        If True, constant `y` does not raise an error.

    Returns
    -------
    y : pd.Series

    Raises
    ------
    ValueError, TypeError
        If y is an invalid input
    """
    # Check if pandas series or numpy array
    if not isinstance(y, pd.Series):
        raise TypeError(f"`y` must be a pandas Series, but found type: {type(y)}")

    # check that series is not empty
    if not allow_empty:
        if len(y) < 1:
            raise ValueError(f"`y` must contain at least some observations, but found empty series: {y}")

    if not allow_constant:
        if np.all(y == y.iloc[0]):
            raise ValueError(f"All values of `y` are the same")

    # check time index
    check_time_index(y.index)
    return y


def check_cv(cv):
    """
    Check CV generators.

    Parameters
    ----------
    cv : CV generator

    Raises
    ------
    ValueError
        if cv does not have the required attributes.
    """
    from sktime.forecasting.model_selection._split import BaseTemporalCrossValidator
    allowed_base_class = BaseTemporalCrossValidator
    if not isinstance(cv, allowed_base_class):
        raise TypeError(f"`cv` is not an instance of {allowed_base_class}")
    return cv


def check_time_index(time_index):
    """Check time index.

    Parameters
    ----------
    time_index : pd.Index or np.array

    Returns
    -------
    time_index : pd.Index
    """
    if isinstance(time_index, np.ndarray):
        time_index = pd.Index(time_index)

    # period or datetime index are not support yet
    supported_index_types = (pd.RangeIndex, pd.Int64Index, pd.UInt64Index)
    if not isinstance(time_index, supported_index_types):
        raise NotImplementedError(f"{type(time_index)} is not supported, "
                                  f"please use one of {supported_index_types} instead.")

    if not time_index.is_monotonic:
        raise ValueError(f"Time index must be sorted (monotonically increasing), "
                         f"but found: {time_index}")

    return time_index


def check_X(X):
    """Validate input data.

    Parameters
    ----------
    X : pandas.DataFrame

    Returns
    -------
    X : pandas.DataFrame

    Raises
    ------
    ValueError
        If y is an invalid input
    """
    if not isinstance(X, pd.DataFrame):
        raise ValueError(f"`X` must a pandas DataFrame, but found: {type(X)}")
    if X.shape[0] > 1:
        raise ValueError(f"`X` must consist of a single row, but found: {X.shape[0]} rows")

    # Check if index is the same for all columns.

    # Get index from first row, can be either pd.Series or np.array.
    first_index = X.iloc[0, 0].index if hasattr(X.iloc[0, 0], 'index') else pd.RangeIndex(X.iloc[0, 0].shape[0])

    # Series must contain now least 2 observations, otherwise should be primitive.
    if len(first_index) < 1:
        raise ValueError(f'Time series must contain now least 2 observations, but found: '
                         f'{len(first_index)} observations in column: {X.columns[0]}')

    # Compare with remaining columns
    for c, col in enumerate(X.columns):
        index = X.iloc[0, c].index if hasattr(X.iloc[0, c], 'index') else pd.RangeIndex(X.iloc[0, 0].shape[0])
        if not np.array_equal(first_index, index):
            raise ValueError(f'Found time series with unequal index in column {col}. '
                             f'Input time-series must have the same index.')

    return X


def check_window_length(window_length):
    """Validate window length"""
    if window_length is not None:
        if not is_int(window_length) or window_length < 1:
            raise ValueError(f"`window_length_` must be a positive integer >= 1 or None, "
                             f"but found: {window_length}")
    return window_length


def check_step_length(step_length):
    """Validate window length"""
    if step_length is not None:
        if not is_int(step_length) or step_length < 1:
            raise ValueError(f"`step_length` must be a positive integer >= 1 or None, "
                             f"but found: {step_length}")
    return step_length


def check_sp(sp):
    """Validate seasonal periodicity.

    Parameters
    ----------
    sp : int
        Seasonal periodicity

    Returns
    -------
    sp : int
        Validated seasonal periodicity
    """
    if sp is not None:
        if not is_int(sp) or sp < 1:
            raise ValueError("`sp` must be a positive integer >= 1 or None")
    return sp


def check_fh(fh):
    """Validate forecasting horizon.

    Parameters
    ----------
    fh : int, list of int, array of int
        Forecasting horizon with steps ahead to predict.

    Returns
    -------
    fh : numpy array of int
        Sorted and validated forecasting horizon.
    """
    # check single integer
    if is_int(fh):
        fh = np.array([fh], dtype=np.int)

    # check array
    elif isinstance(fh, np.ndarray):
        if fh.ndim > 1:
            raise ValueError(f"`fh` must be a 1d array, but found shape: "
                             f"{fh.shape}")

        if not np.issubdtype(fh.dtype, np.integer):
            raise ValueError(f"If `fh` is passed as an array, it must "
                             f"be an array of integers, but found an "
                             f"array of type: {fh.dtype}")



    # check list
    elif isinstance(fh, list):
        if not np.all([is_int(h) for h in fh]):
            raise ValueError("If `fh` is passed as a list, "
                             "it has to be a list of integers.")
        fh = np.array(fh, dtype=np.int)

    else:
        raise ValueError(f"`fh` has to be either a numpy array or list of integers, "
                         f"or a single integer, but found: {type(fh)}")

    # check fh is not empty
    if len(fh) < 1:
        raise ValueError(f"`fh` cannot be empty, please specify now least one "
                         f"step to forecast.")

    # check fh does not contain duplicates
    if len(fh) != len(np.unique(fh)):
        raise ValueError(f"`fh` should not contain duplicates.")

    # sort fh
    fh.sort()
    return fh


def check_is_fitted_in_transform(estimator, attributes, msg=None, all_or_any=all):
    """Checks if the estimator is fitted during transform by verifying the presence of
    "all_or_any" of the passed attributes and raises a NotFittedError with the
    given message.

    Parameters
    ----------
    estimator : estimator instance.
        estimator instance for which the check is performed.
    attributes : attribute name(s) given as string or a list/tuple of strings
        Eg.:
            ``["coef_", "estimator_", ...], "coef_"``
    msg : string
        The default error message is, "This %(name)s instance is not fitted
        yet. Call 'fit' with appropriate arguments before using this method."
        For custom messages if "%(name)s" is present in the message string,
        it is substituted for the estimator name.
        Eg. : "Estimator, %(name)s, must be fitted before sparsifying".
    all_or_any : callable, {all, any}, default all
        Specify whether all or any of the given attributes must exist.
    Returns
    -------
    None

    Raises
    ------
    NotFittedError
        If the attributes are not found.    
    """
    if msg is None:
        msg = ("This %(name)s instance has not been fitted yet. Call 'transform' with "
               "appropriate arguments before using this method.")

    check_is_fitted(estimator, attributes=attributes, msg=msg, all_or_any=all_or_any)


def check_consistent_time_index(*ys, y_train=None):
    """Check that y_test and y_pred have consistent indices.
    Parameters
    ----------
    y_test : pd.Series
    y_pred : pd.Series
    y_train : pd.Series
    Raises
    ------
    ValueError
        If time indicies are not equal
    """

    # only validate indices if data is passed as pd.Series
    first_index = ys[0].index
    check_time_index(first_index)
    for y in ys[1:]:
        check_time_index(y.index)

        if not first_index.equals(y.index):
            raise ValueError(f"Found inconsistent time indices.")

    if y_train is not None:
        check_time_index(y_train.index)
        if y_train.index.max() >= first_index.min():
            raise ValueError(f"Found `y_train` with time index which is not "
                             f"before time index of `y_pred`")


def check_alpha(alpha):
    """Check that a confidence level alpha (or list of alphas) is valid.
    All alpha values must lie in the open interval (0, 1).
    Parameters
    ----------
    alpha : float, list of float
    Raises
    ------
    ValueError
        If alpha is outside the range (0, 1).
    """
    # check type
    if isinstance(alpha, list):
        if not all(isinstance(a, float) for a in alpha):
            raise ValueError("When `alpha` is passed as a list, "
                             "it must be a list of floats")

    elif isinstance(alpha, float):
        alpha = [alpha]  # make iterable

    # check range
    for a in alpha:
        if not 0 < a < 1:
            raise ValueError(f"`alpha` must lie in the open interval (0, 1), "
                             f"but found: {a}.")

    return alpha


def check_cutoffs(cutoffs):
    if not isinstance(cutoffs, np.ndarray):
        raise ValueError(f"`cutoffs` must be a np.array, but found: {type(cutoffs)}")

    if not all([is_int(cutoff) for cutoff in cutoffs]):
        raise ValueError("All cutoff points must be integers")

    if not cutoffs.ndim == 1:
        raise ValueError("`cutoffs must be 1-dimensional array")

    if not len(cutoffs) > 0:
        raise ValueError("Found empty `cutoff` array")

    return np.sort(cutoffs)


def check_scoring(scoring):
    from sktime.performance_metrics.forecasting._classes import MetricFunctionWrapper
    from sktime.performance_metrics.forecasting import sMAPE

    if scoring is None:
        return sMAPE()

    if not callable(scoring):
        raise TypeError("`scoring` must be a callable object")

    allowed_base_class = MetricFunctionWrapper
    if not isinstance(scoring, allowed_base_class):
        raise TypeError(f"`scoring` must inherit from `{allowed_base_class.__name__}`")

    return scoring
