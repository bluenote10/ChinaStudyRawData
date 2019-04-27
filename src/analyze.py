from __future__ import division, print_function

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn import linear_model
import statsmodels.api as sm

from convert import get_data_path, ColNames


def plot(df, x, y):
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.plot(df[x], df[y], "o")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.show()


def check_correlations(df, target_col):
    column_names, column_descs = parse_column_names_descriptions()

    cols = [
        (col_name, column_descs[col_code]) for col_code, col_name in sorted(column_names.items())
        if col_name != target_col and not col_code.startswith("M")
    ]

    names = []
    descs = []
    corrs = []

    null_mask_target = df[target_col].isnull()

    for col_name, col_desc in cols:
        if col_name not in df:
            print("Warning: skipping column '{}', not available.".format(col_name))
            continue

        corr = df[[target_col, col_name]].corr().iloc[0, 1]
        print("{:<20s}{:12.3f}".format(col_name, corr))

        # count nulls
        null_mask_column = df[col_name].isnull()
        print("N = {}   N_missing_target = {}    N_missing_column = {}    N_missing_either = {}".format(
            len(df),
            null_mask_target.sum(),
            null_mask_column.sum(),
            (null_mask_target | null_mask_column).sum(),
        ))

        if not math.isnan(corr):
            names.append(col_name)
            descs.append(col_desc)
            corrs.append(corr)

    df = pd.DataFrame({
        "variable": names,
        "description": descs,
        "correlation": corrs,
    })
    df = df[["variable", "description", "correlation"]]
    df["correlation_abs"] = df["correlation"].abs()
    df.sort_values("correlation_abs", ascending=False, inplace=True)
    print(df)


def calc_rmse(target_col, predict_col):
    return math.sqrt(((predict_col - target_col) ** 2).mean())


def fit_model(df, target_col, colname_filter):
    col_names = ColNames()

    cols = [
        col_name for col_name in col_names.get_nice_names()
        if col_name != target_col and colname_filter(col_name) and col_name in df.columns
    ]

    df = df[cols + [target_col]]

    null_mask = df[target_col].isnull()
    print("N = {}   N_missing_target = {}".format(
        len(df),
        null_mask.sum(),
    ))

    for col_name in cols:
        # count nulls
        null_mask_column = df[col_name].isnull()
        print("N = {}   N_missing_column = {}".format(
            len(df),
            null_mask_column.sum(),
        ))
        if null_mask_column.sum() > 10:
            del df[col_name]
        else:
            null_mask |= null_mask_column

    print("N = {}   N_missing_total = {}".format(
        len(df),
        null_mask.sum(),
    ))

    df = df.loc[~null_mask, :].reset_index(drop=True)

    cols = df.columns[:-1]

    base_rmse = calc_rmse(df[target_col], pd.Series([df[target_col].mean()] * len(df)))
    print("Base RMSE: {:12.3f}".format(base_rmse))

    data = {
        "col": [],
        "rmse": [],
        "rmse_reduction": [],
        "corr": [],
        "corr_std_err": [],
    }

    for col in cols:
        reg = linear_model.LinearRegression()
        reg.fit(df[[col]], df[target_col])

        X = df[[col]].copy()
        X["const"] = 1
        y = df[target_col]
        results = sm.OLS(y, X).fit()
        print(results.summary())
        std_err = np.sqrt(results.cov_params().iloc[0, 0])
        corr_std_err = std_err * df[col].std() / df[target_col].std()

        corr = df[[target_col, col]].corr().iloc[0, 1]
        corr_est = reg.coef_[0] * df[col].std() / df[target_col].std()

        predict = reg.predict(df[[col]])
        rmse = calc_rmse(df[target_col], predict)
        print("{:<30s} RMSE: {:12.3f}    RMSE reduction: {:12.3f}    corr: {:12.3f}    corr_est: {:12.3f}".format(
            col, rmse, rmse - base_rmse, corr, corr_est
        ))
        data["col"].append(col)
        data["rmse"].append(rmse)
        data["rmse_reduction"].append(rmse - base_rmse)
        data["corr"].append(corr_est)
        data["corr_std_err"].append(corr_std_err)
        #import IPython; IPython.embed()

    res = pd.DataFrame(data, columns=["col", "rmse", "rmse_reduction", "corr", "corr_std_err"])
    res = res.sort_values("corr").reset_index(drop=True)
    print(res)

    import IPython; IPython.embed()
    reg = linear_model.LinearRegression()
    reg.fit(df.iloc[:, :-1], df[target_col])

    for i in range(len(df.columns) - 1):
        print("{:<30s} {:12.3f}".format(df.columns[i], reg.coef_[i]))
        #reg.coef_


def load_data(filename):
    df = pd.read_csv(get_data_path("data", filename))

    mask_totals = (df["Sex"] == "T") & (df["Xiang"] == 3)
    df = df.loc[mask_totals, :].reset_index(drop=True)

    #check_correlations(df, "M_MEDICALc")
    #check_correlations(df, "ALLCAc")
    #check_correlations(df, "ALLVASCc")

    # M_MEDICALc M_ALLCAc DIABETESc BLOODc MENTALc M_ALLVASCc M_STOMCAc

    #fit_model(df, "M_MEDICALc", lambda col_name: col_name.startswith("P"))
    fit_model(df, "P_TOTCHOL", lambda col_name: col_name.startswith("M"))

    #plot(df, "KCAL", "MEDICALc")
    plot(df, "dSMOKE", "LUNGCAfc")
    plot(df, "VOLURmn", "ALLCAc")
    plot(df, "dSMOKFOOD", "ALLCAc")
    import IPython; IPython.embed()


if __name__ == "__main__":
    load_data("89.csv")
