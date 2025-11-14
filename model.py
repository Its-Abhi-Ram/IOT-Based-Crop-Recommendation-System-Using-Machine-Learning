import pickle

def load_model():
    return pickle.load(open("model_edited.pkl", "rb"))
