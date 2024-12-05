import pickle
from nela_features.nela_features import NELAFeatureExtractor
from google.cloud import language_v2
import numpy as np
import pandas as pd
from flask import jsonify

nela = NELAFeatureExtractor()
client = language_v2.LanguageServiceClient()
model = pickle.load(open('backend_logic/model.pkl', 'rb'))
scaler = pickle.load(open('backend_logic/scaler.pkl', 'rb'))

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
    style_vector, style_names = nela.extract_style(str(inp))
    bias_vector, bias_names = nela.extract_bias(str(inp))
    feature_vector = style_vector + bias_vector
    feature_names = style_names + bias_names
    return feature_vector, feature_names

def get_features(text, glove_embeddings):
    text = text.lower()
    nela_features, nela_names = find_nela_features(text)
    sentiment_feature, sentiment_name = [analyze_sentiment(text)], ['sentiment']
    embedding_features, embeddings_names = find_embedding_features(text, glove_embeddings)
    all_features = nela_features + embedding_features + sentiment_feature
    names = nela_names + embeddings_names + sentiment_name
    df = pd.DataFrame([all_features], columns=names)
    
    good_cols = [test_embedding['name'] for test_embedding in test_embeddings]
    good_cols.append('sentiment')
    good_cols.append('bias_words')
    _, tmp = nela.extract_style('test')
    not_tmp = ['quotes', 'exclaim', 'allpunc', 'allcaps', 'stops', 'WP$', '(', 'UH', 'SYM', 'RBR', '$', 'POS', ')', ',', "''", 'EX', '``', '--', 'LS', '.', ':', 'NNPS', 'FW', 'JJR', 'MD', 'RBS', 'VBG', 'PDT', 'RP', 'VBN', 'TO', 'PRP$', 'RB', 'PRP', 'VBZ', 'VBD', 'WDT', 'VB']
    tmp = [t for t in tmp if t not in not_tmp]
    good_cols += tmp
    bad_columns = [col for col in df.columns if col not in good_cols]
    
    df = df.drop(list(bad_columns), axis=1)
    return df

def predict_sentence(text, glove_embeddings, threshold=0.5, single=False):
    try:
        feature_vector = get_features(text, glove_embeddings)
        feature_vector = scaler.transform(feature_vector)
        y = model.predict_proba(feature_vector)
        y = y[0][1]
        # Do some transform on y using a threshold
        # Anything that is 1 should be reliable
        # Anything else is a range of unrealiability from 1 (unreliable) to 0 (reliable)
        if single:
            y = (max(0, y - threshold) / (1 - threshold)) / 1.5
            if y != 0:
                y += 0.2
        else:
            y = max(0, y - threshold) / (1 - threshold)
        return y
    except Exception as e:
        # print(e)
        return 0

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
    
    test_1 = "The quick brown fox jumps over the lazy dog."
    print("Testing sentence 1", test_1, predict_sentence(test_1, glove_embeddings))