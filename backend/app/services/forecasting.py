"""Lightweight demand forecasting.

Deliberately simple and transparent: an ensemble of linear-trend regression,
moving average and exponential smoothing, averaged, with an uncertainty band
derived from in-sample residuals. Forecasts are estimates, never guarantees —
the UI must present them with the confidence interval.
"""

from __future__ import annotations

import numpy as np


def _linear_trend(y: np.ndarray, horizon: int) -> np.ndarray:
    x = np.arange(len(y))
    if len(y) < 2:
        return np.repeat(y[-1] if len(y) else 0.0, horizon)
    a, b = np.polyfit(x, y, 1)
    fx = np.arange(len(y), len(y) + horizon)
    return a * fx + b


def _moving_average(y: np.ndarray, horizon: int, window: int = 3) -> np.ndarray:
    if len(y) == 0:
        return np.zeros(horizon)
    w = min(window, len(y))
    return np.repeat(y[-w:].mean(), horizon)


def _exp_smoothing(y: np.ndarray, horizon: int, alpha: float = 0.5) -> np.ndarray:
    if len(y) == 0:
        return np.zeros(horizon)
    level = y[0]
    for val in y[1:]:
        level = alpha * val + (1 - alpha) * level
    return np.repeat(level, horizon)


def forecast(series: list[float], horizon: int = 12) -> dict:
    """Forecast `horizon` future months from a monthly `series`.

    Returns point forecasts, a +/- band, and the key milestone months (3/6/12).
    """
    y = np.asarray(series, dtype=float)
    if y.size == 0:
        zeros = [0.0] * horizon
        return {"points": zeros, "lower": zeros, "upper": zeros,
                "milestones": {}, "method": "insufficient-data"}

    members = np.vstack([
        _linear_trend(y, horizon),
        _moving_average(y, horizon),
        _exp_smoothing(y, horizon),
    ])
    point = members.mean(axis=0)
    point = np.clip(point, 0.0, None)

    # Uncertainty: residual std of the linear fit against history, widening with
    # the forecast horizon (further ahead = less certain).
    resid_std = float(np.std(y - _linear_fit_insample(y))) if y.size >= 2 else float(np.std(y))
    widen = 1.0 + np.arange(horizon) * 0.08
    band = 1.5 * resid_std * widen

    lower = np.clip(point - band, 0.0, None)
    upper = point + band

    def at(m: int) -> dict | None:
        if horizon >= m:
            return {"point": round(float(point[m - 1]), 1),
                    "lower": round(float(lower[m - 1]), 1),
                    "upper": round(float(upper[m - 1]), 1)}
        return None

    return {
        "points": [round(float(v), 1) for v in point],
        "lower": [round(float(v), 1) for v in lower],
        "upper": [round(float(v), 1) for v in upper],
        "milestones": {"3m": at(3), "6m": at(6), "12m": at(12)},
        "method": "ensemble(linear+ma+ewma)",
    }


def _linear_fit_insample(y: np.ndarray) -> np.ndarray:
    x = np.arange(len(y))
    a, b = np.polyfit(x, y, 1)
    return a * x + b
