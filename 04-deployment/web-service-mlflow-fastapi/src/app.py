import uvicorn
from fastapi import FastAPI
from src.utils import Ride, predict, prepare_features

app = FastAPI(title="duration-prediction")


@app.post("/predict")
def predict_endpoint(ride: Ride):
    features = prepare_features(ride)
    prediction = predict(features)
    return {"duration": prediction}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
