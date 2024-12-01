import pickle
from nela_features.nela_features import NELAFeatureExtractor
from google.cloud import language_v2
import numpy as np
import pandas as pd
from flask import jsonify

nela = NELAFeatureExtractor()
client = language_v2.LanguageServiceClient()
model = pickle.load(open('backend_logic/model.pkl', 'rb'))
opt_threshold = 0.4494572

test_embeddings = [
    # Socioeconomic status
    {'name': 'rich/poor', 'dir1': ["rich", "wealthy", "affluent"], "dir2": ["poor", "impoverished", "destitute"]},
    
    # Age bias
    {'name': 'young/old', 'dir1': ["young", "youthful", "vibrant"], "dir2": ["old", "elderly", "aged"]},
    
    # Gender stereotypes (roles)
    {'name': 'male/female stereotypes', 'dir1': ["leader", "strong", "assertive"], "dir2": ["nurturing", "caring", "supportive"]},
    
    # Rural vs. Urban bias
    {'name': 'rural/urban', 'dir1': ["urban", "city"], "dir2": ["rural", "countryside"]},
    
    # Employment bias (white-collar vs. blue-collar)
    {'name': 'white-collar/blue-collar', 'dir1': ["professional", "educated", "executive"], "dir2": ["manual", "laborer", "working-class"]},
    
    # Intelligence perception
    {'name': 'smart/dumb', 'dir1': ["smart", "intelligent"], 'dir2': ["dumb", "stupid"]},
]


def find_embedding_features(inp, glove_embeddings):
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


# Get sentiment from Google
def analyze_sentiment(text):
    document = {"content": text, "type_": language_v2.Document.Type.PLAIN_TEXT, "language_code": "en"}
    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )
    return response.document_sentiment.score

# Apply nela to a single sentence
def find_nela_features(inp):
    feature_vector, feature_names = nela.extract_all(str(inp))
    return feature_vector, feature_names

def get_features(text, glove_embeddings):
    nela_features, nela_names = find_nela_features(text)
    sentiment_feature, sentiment_name = [analyze_sentiment(text)], ['sentiment']
    embedding_features, embeddings_names = find_embedding_features(text, glove_embeddings)
    all_features = nela_features + embedding_features + sentiment_feature
    names = nela_names + embeddings_names + sentiment_name
    df = pd.DataFrame([all_features], columns=names)
    dropped_features = {'sneu', 'FairnessVirtue', 'report_verbs', 'num_dates', 'NNS', 'AuthorityVirtue', 'JJS', 'vadneu', 'VB', '``', '--', 'WP$', 'LS', '(', 'factives', 'IngroupVice', 'AuthorityVice', 'lix', 'wneu', 'FairnessVice', 'wpos', 'positive_opinion_words', 'RB', 'FW', 'VBP', 'avg_wordlen', 'PurityVice', 'HarmVirtue', 'EX', 'SYM', '$', 'PDT', 'allpunc', 'vadneg', 'implicatives', 'UH', 'WRB', 'white-collar/blue-collar', 'assertatives', 'JJR', 'RP', ',', 'RBR', 'vadpos', 'MD', 'IngroupVirtue', '.', 'num_locations', 'male/female stereotypes', ':', 'VBD', "''", ')', 'POS', 'WDT', 'HarmVice', 'hedges', 'PRP', 'VBN', 'PurityVirtue', 'RBS', 'VBG', 'MoralityGeneral', 'sneg'}
    df = df.drop(list(dropped_features), axis=1)
    return df

def predict_sentence(text, glove_embeddings):
    feature_vector = get_features(text, glove_embeddings)
    y = model.predict_proba(feature_vector)
    y = y[0][1]
    # Do some transform on y using optimal threshold
    # Anything that is 1 should be reliable
    # Anything else is a range of unrealiability from 1 (unreliable) to 0 (reliable)
    y = max(0, y - opt_threshold) / (1 - opt_threshold)
    return jsonify({'score': y,
                  'message': 'Success'})
    
if __name__ == '__main__':
    glove_embeddings = {}
    print("Loading glove embeddings")
    with open('backend_logic/glove.6B.100d.txt', 'r') as f:
        for line in f:
            values = line.split(' ')
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            glove_embeddings[word] = vector
    print("Glove embeddings loaded")
    
    test_1 = "Jackie Mason: Hollywood Would Love Trump if He Bombed North Korea over Lack of Trans Bathrooms (Exclusive Video) - Breitbart"
    # test_2 is test_1 but lowercased
    test_2 = test_1.lower()
    # run feature extraction on both then combine the tables and add a column for the sentence
    features_1 = get_features(test_1, glove_embeddings)
    features_2 = get_features(test_2, glove_embeddings)
    combined_features = pd.concat([features_1, features_2], axis=0)
    combined_features['sentence'] = [test_1, test_2]
    # save csv to look at
    combined_features.to_csv('combined_features.csv')
    
    print("Testing sentence 1", test_1, predict_sentence(test_1, glove_embeddings))
    print("Testing sentence 2", test_2, predict_sentence(test_2, glove_embeddings))