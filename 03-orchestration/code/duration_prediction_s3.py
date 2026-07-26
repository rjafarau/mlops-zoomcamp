#!/usr/bin/env python
# coding: utf-8

import argparse
import datetime
import pathlib
import pickle

import mlflow
import pandas as pd
import xgboost as xgb
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact
from prefect_aws import S3Bucket
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error

mlflow.set_experiment("nyc-taxi-experiment")

models_folder = pathlib.Path("models")
models_folder.mkdir(exist_ok=True)

data_folder = pathlib.Path("data")
data_folder.mkdir(exist_ok=True)

MARKDOWN_TEMPLATE = """
# RMSE Report

## Summary

Duration Prediction

## RMSE XGBoost Model

| Region    | RMSE |
|:----------|-------:|
| {timestamp} | {error:.2f} |
"""


@task(retries=3, retry_delay_seconds=2)
def read_dataframe(year, month):
    file_name = f"green_tripdata_{year}-{month:02d}.parquet"
    s3_bucket_block = S3Bucket.load("s3-bucket-example")
    s3_bucket_block.download_object_to_path(
        from_path=file_name,
        to_path=data_folder / file_name,
    )
    df = pd.read_parquet(data_folder / file_name)

    df["duration"] = df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]
    df["duration"] = df["duration"].dt.total_seconds() / 60

    df = df[(df["duration"] >= 1) & (df["duration"] <= 60)]

    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].astype(str)

    df["PU_DO"] = df["PULocationID"] + "_" + df["DOLocationID"]

    return df


@task
def create_X(df, dv=None):
    categorical = ["PU_DO"]
    numerical = ["trip_distance"]
    dicts = df[categorical + numerical].to_dict(orient="records")

    if dv is None:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)

    return X, dv


@task(log_prints=True)
def train_model(X_train, y_train, X_val, y_val, dv):
    mlflow.xgboost.autolog(disable=True)
    with mlflow.start_run() as run:
        train = xgb.DMatrix(X_train, label=y_train)
        valid = xgb.DMatrix(X_val, label=y_val)

        best_params = {
            "max_depth": 44,
            "learning_rate": 0.1719747846289316,
            "reg_alpha": 4.896614873911946e-05,
            "reg_lambda": 0.019446810721081013,
            "min_child_weight": 1.785047439733004,
            "objective": "reg:squarederror",
            "random_state": 42,
        }

        mlflow.log_params(best_params)

        booster = xgb.train(
            params=best_params,
            dtrain=train,
            num_boost_round=1000,
            evals=[(valid, "validation")],
            early_stopping_rounds=50,
        )

        y_pred = booster.predict(
            data=valid, iteration_range=(0, booster.best_iteration + 1)
        )
        error = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("error", error)

        (models_folder / "preprocessor.pkl").write_bytes(pickle.dumps(dv))
        mlflow.log_artifact(
            local_path=models_folder / "preprocessor.pkl",
            artifact_path="preprocessor",
        )

        mlflow.xgboost.log_model(booster, name="models_mlflow")

        create_markdown_artifact(
            key="duration-model-report",
            markdown=MARKDOWN_TEMPLATE.format(
                timestamp=datetime.datetime.now(),
                error=error,
            ),
        )

        return run.info.run_id


@flow
def run(year, month):
    df_train = read_dataframe(year=year, month=month)

    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    df_val = read_dataframe(year=next_year, month=next_month)

    X_train, dv = create_X(df_train)
    X_val, _ = create_X(df_val, dv)

    target = "duration"
    y_train = df_train[target].values
    y_val = df_val[target].values

    run_id = train_model(X_train, y_train, X_val, y_val, dv)
    print(f"MLflow run_id: {run_id}")
    return run_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train a model to predict taxi trip duration."
    )
    parser.add_argument(
        "--year", type=int, required=True, help="Year of the data to train on"
    )
    parser.add_argument(
        "--month", type=int, required=True, help="Month of the data to train on"
    )
    args = parser.parse_args()

    run_id = run(year=args.year, month=args.month)

    pathlib.Path("run_id.txt").write_text(run_id)
