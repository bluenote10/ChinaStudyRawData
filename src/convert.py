#!/usr/bin/env python

from __future__ import division, print_function

import pandas as pd
import os
import glob

from functools import reduce

DATASETS = [
    "83",
    "89",
    "93",
    "TAI",
]


def get_data_path(*subpaths):
    return os.path.normpath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", *subpaths)
    )


def parse_column_names_descriptions():
    # This file format is silly...
    column_names = dict()
    column_descs = dict()

    col_names_file = os.path.join(get_data_path("original_data"), "CHNAME.TXT")
    lines = open(col_names_file).readlines()
    lines_odd = lines[::2]
    lines_even = lines[1::2]

    lines = [
        (line_even + line_odd[4:].strip()).replace("\n", "")
        for line_even, line_odd in zip(lines_odd, lines_even)
    ]

    for line in lines:
        fields = line.split()
        if len(fields) > 1:
            column_code = fields[0]
            column_name = fields[1]
            column_desc = " ".join(fields[2:])
            column_names[column_code] = column_name
            column_descs[column_code] = column_desc

    return column_names, column_descs


def convert_column(series):
    nan = float("nan")
    return series.str.strip().replace(".", nan)\
                             .replace("", nan)\
                             .astype(float)


def extract_dataset(dataset):
    columns_names, columns_descs = parse_column_names_descriptions()

    glob_path = os.path.join(get_data_path("original_data"), "CH{}*.CSV".format(dataset))

    dfs = []

    for f in sorted(glob.glob(glob_path)):
        print("Reading file: '{}'".format(f))

        df = pd.read_csv(f)

        # There seems to be a final dummy column => remove it
        if df.columns[-1].strip() == "":
            del df[df.columns[-1]]

        # Strip whitespace from column names
        df.columns = [c.strip() for c in df.columns]

        # Verify schema / convert types
        data_columns = set(columns_names.keys())
        allowed_columns = {"County", "Sex", "Xiang"} | data_columns
        for c in df.columns:
            if c not in allowed_columns:
                raise ValueError("Unexpected column name '{}'".format(c))
            elif c in data_columns:
                df[c] = convert_column(df[c])
                df.rename(columns={c: columns_names[c]}, inplace=True)

        print("Shape: {}".format(df.shape))
        dfs.append(df)

    print("Merging data frames...")
    df_merged = reduce(lambda left, right: pd.merge(left, right, on=["County", "Sex", "Xiang"]), dfs)
    print("Shape: {}".format(df_merged.shape))

    return df_merged


def main():
    for dataset in DATASETS:
        df = extract_dataset(dataset)

        output_file = get_data_path("data", "{}.csv".format(dataset))
        df.to_csv(output_file)


if __name__ == "__main__":
    main()
