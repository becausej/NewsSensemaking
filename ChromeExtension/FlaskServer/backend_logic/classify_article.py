import newspaper
from nela_features.nela_features import NELAFeatureExtractor
import pickle
from flask import jsonify
import numpy as np

def find_embedding_features(inp, glove_embeddings):
    test_embeddings = [
        # Socioeconomic status
        {'name': 'rich/poor', 'dir1': ["rich", "wealthy", "affluent"], "dir2": ["poor", "impoverished", "destitute"]},

        # Age bias
        {'name': 'young/old', 'dir1': ["young", "youthful", "vibrant"], "dir2": ["old", "elderly", "aged"]},

        # Gender stereotypes (roles)
        {'name': 'male/female stereotypes', 'dir1': ["leader", "strong", "assertive"],
         "dir2": ["nurturing", "caring", "supportive"]},

        # Rural vs. Urban bias
        {'name': 'rural/urban', 'dir1': ["urban", "city"], "dir2": ["rural", "countryside"]},

        # Employment bias (white-collar vs. blue-collar)
        {'name': 'white-collar/blue-collar', 'dir1': ["professional", "educated", "executive"],
         "dir2": ["manual", "laborer", "working-class"]},

        # Intelligence perception
        {'name': 'smart/dumb', 'dir1': ["smart", "intelligent"], 'dir2': ["dumb", "stupid"]},
    ]
    # Find the average embedding of the sentence
    words = inp.split()
    embedding = np.zeros(len(glove_embeddings['the']))

    for word in words:
        if word.lower() in glove_embeddings:
            embedding += glove_embeddings[word.lower()]
    embedding /= len(words)

    # Now find all cosine similarities to the difference between dir1 and dir2
    embedding_features = []
    embedding_names = []
    for test_embedding in test_embeddings:
        net_dir = np.zeros(len(glove_embeddings['the']))
        for word in test_embedding['dir1']:
            net_dir += glove_embeddings[word]
        for word in test_embedding['dir2']:
            net_dir -= glove_embeddings[word]
        net_dir /= len(test_embedding['dir1']) + len(test_embedding['dir2'])

        # Find the cosine similarity
        cos_sim = np.dot(embedding, net_dir) / (np.linalg.norm(embedding) * np.linalg.norm(net_dir))

        embedding_features.append(cos_sim)
        embedding_names.append(test_embedding['name'])

    return embedding_features, embedding_names

def embedding_vector(text, glove_embeddings):
    embedding_features, embedding_names = find_embedding_features(text, glove_embeddings)
    return embedding_features

def get_article_text(url):
    return newspaper.article(url).text

def get_knn_class_text(text,glove_embeddings):
    with open('backend_logic/knnfakenews.pkl', 'rb') as f:
        knn = pickle.load(f)
    nela = NELAFeatureExtractor()
    feature_vector, feature_names = nela.extract_all(text)
    feature_vector = feature_vector + embedding_vector(text,glove_embeddings)
    vector = [[feature_vector[i] for i in [89, 92, 4, 59, 24]]]
    return jsonify({'class':"Reliable" if knn.predict(vector) == [1] else "Unreliable",'message':'Success'})

def get_knn_class(url,glove_embeddings):
    text = get_article_text(url)
    return get_knn_class_text(text,glove_embeddings)
