import newspaper
from nela_features.nela_features import NELAFeatureExtractor
import pickle

def get_article_text(url):
    return newspaper.article(url).text

def get_knn_class_text(text):
    with open('knnfakenews.pkl', 'rb') as f:
        knn = pickle.load(f)
    nela = NELAFeatureExtractor()
    feature_vector, feature_names = nela.extract_all(text)
    vector = [[feature_vector[i] for i in [24, 22, 4, 86]]]
    return True if knn.predict(vector) == [1] else False

def get_knn_class(url):
    text = get_article_text(url)
    return get_knn_class_text(text)