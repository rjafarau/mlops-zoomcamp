import os

import mlflow
import pydantic

RUN_ID = os.environ["RUN_ID"]
MODEL_ID = os.environ["MODEL_ID"]

# logged_model = f"runs:/{RUN_ID}/model"
# logged_model = f"models:/{MODEL_ID}"
# logged_model = f"mlflow-artifacts:/3/models/{MODEL_ID}/artifacts"
logged_model = f"s3://mlflow/3/models/{MODEL_ID}/artifacts"

model = mlflow.pyfunc.load_model(logged_model)


class Ride(pydantic.BaseModel):
    PULocationID: int
    DOLocationID: int
    trip_distance: float


def prepare_features(ride: Ride):
    return {
        "PU_DO": f"{ride.PULocationID}_{ride.DOLocationID}",
        "trip_distance": ride.trip_distance,
    }


def predict(features):
    return model.predict(features).item()
