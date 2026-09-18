import argparse
import pathlib
import uuid

import mlflow
import pandas as pd

from prefect import flow, get_run_logger, task


@task
def get_paths(taxi_type, year, month, model_id):
    input_file = (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/"
        f"{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet"
    )

    output_dir = (
        pathlib.Path("output")
        / f"taxi_type={taxi_type}"
        / f"year={year:04d}"
        / f"month={month:02d}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{model_id}.parquet"

    return input_file, output_file


def generate_uuids(n: int):
    return [str(uuid.uuid4()) for _ in range(n)]


@task
def read_dataframe(filename: str):
    df = pd.read_parquet(filename)

    df["duration"] = df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]
    df["duration"] = df["duration"].dt.total_seconds() / 60
    df = df[(df["duration"] >= 1) & (df["duration"] <= 60)]

    df["ride_id"] = generate_uuids(len(df))

    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].astype(str)

    df["PU_DO"] = df["PULocationID"] + "_" + df["DOLocationID"]

    return df


@task
def prepare_features(df: pd.DataFrame):
    categorical = ["PU_DO"]
    numerical = ["trip_distance"]
    dicts = df[categorical + numerical].to_dict(orient="records")
    return dicts


@task
def load_model(model_id: str):
    # logged_model = f"runs:/{run_id}/model"
    logged_model = f"models:/{model_id}"
    # logged_model = f"mlflow-artifacts:/3/models/{model_id}/artifacts"
    # logged_model = f"s3://mlflow/3/models/{model_id}/artifacts"
    model = mlflow.pyfunc.load_model(logged_model)
    return model


@task
def predict(model, features):
    return model.predict(features)


@task
def save_results(df, y_pred, model_id, output_file):
    df_result = df[
        ["ride_id", "lpep_pickup_datetime", "PULocationID", "DOLocationID"]
    ].copy()
    df_result["actual_duration"] = df["duration"]
    df_result["predicted_duration"] = y_pred
    df_result["diff"] = df_result["actual_duration"] - df_result["predicted_duration"]
    df_result["model_version"] = model_id

    df_result.to_parquet(output_file, index=False)


@flow
def run(taxi_type: str, year: int, month: int, model_id: str):
    logger = get_run_logger()

    # logging.basicConfig(level=logging.INFO)
    # logger = logging.getLogger()

    logger.info("generating input/output paths...")
    input_file, output_file = get_paths(
        taxi_type=taxi_type,
        year=year,
        month=month,
        model_id=model_id,
    )

    logger.info(f"reading the data from {input_file}...")
    df = read_dataframe(input_file)

    logger.info("preparing features...")
    features = prepare_features(df)

    logger.info(f"loading the model with model_id={model_id}...")
    model = load_model(model_id)

    logger.info("applying the model...")
    y_pred = predict(model, features)

    logger.info(f"saving the result to {output_file}...")
    save_results(df, y_pred, model_id, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Score batch of rides using model to predict taxi trip duration."
    )
    parser.add_argument(
        "--taxi-type", type=str, required=True, help="Taxi type data to score"
    )
    parser.add_argument(
        "--year", type=int, required=True, help="Year of the data to score"
    )
    parser.add_argument(
        "--month", type=int, required=True, help="Month of the data to score"
    )
    parser.add_argument(
        "--model-id", type=str, required=True, help="Model ID of the model to be used"
    )
    args = parser.parse_args()

    run(
        taxi_type=args.taxi_type,
        year=args.year,
        month=args.month,
        model_id=args.model_id,
    )
