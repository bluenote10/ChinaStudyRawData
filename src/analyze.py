from __future__ import division, print_function

import math
import pandas as pd
import matplotlib.pyplot as plt

from convert import get_data_path, parse_column_names_descriptions


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

    for col_name, col_desc in cols:
        if col_name not in df:
            print("Warning: skipping column '{}', not available.".format(col_name))
            continue
        corr = df[[target_col, col_name]].corr().iloc[0, 1]
        print("{:<20s}{:12.3f}".format(col_name, corr))

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


def load_data(filename):
    df = pd.read_csv(get_data_path("data", filename))

    mask_totals = (df["Sex"] == "T") & (df["Xiang"] == 3)
    df = df.loc[mask_totals, :]

    #check_correlations(df, "MEDICALc")
    #check_correlations(df, "ALLCAc")
    check_correlations(df, "ALLVASCc")

    #plot(df, "KCAL", "MEDICALc")


if __name__ == "__main__":
    load_data("89.csv")
