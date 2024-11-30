import numpy as np
from get_dataset import get_and_preprocess_data
from nela_features.nela_features import NELAFeatureExtractor
from tqdm import tqdm
from google.cloud import language_v2

nela = NELAFeatureExtractor()
client = language_v2.LanguageServiceClient()

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

# Embedding vectors to test on
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

def apply_features(statements, glove_embeddings):
    features = []
    names = []
    for statement in tqdm(statements):
        nela_features, nela_names = find_nela_features(statement)
        embedding_features, embeddings_names = find_embedding_features(statement, glove_embeddings)
        sentiment = analyze_sentiment(statement)
        all_features = nela_features + embedding_features + [sentiment]
        features.append(all_features)
        names = nela_names + embeddings_names + ['sentiment']
    np_features = np.array(features)
    return np_features, names
