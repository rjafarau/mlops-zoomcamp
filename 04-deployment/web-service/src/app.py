from flask import Flask, jsonify, request

from src.utils import predict, prepare_features

app = Flask("duration-prediction")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    prediction = predict(features)

    result = {"duration": prediction}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
