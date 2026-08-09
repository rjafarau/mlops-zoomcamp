import pickle

with open("bin/lin_reg.bin", "rb") as f_in:
    (dv, model) = pickle.load(f_in)


def prepare_features(ride):
    return {
        "PU_DO": f"{ride['PULocationID']}_{ride['DOLocationID']}",
        "trip_distance": ride["trip_distance"],
    }


def predict(features):
    X = dv.transform(features)
    return model.predict(X).item()
