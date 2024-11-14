import numpy as np
from get_dataset import get_and_preprocess_data
from nela_features.nela_features import NELAFeatureExtractor
from tqdm import tqdm

nela = NELAFeatureExtractor()

# Apply nela to a single sentence
def find_nela_features(inp):
    feature_vector, _ = nela.extract_all(inp)
    return feature_vector

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
    return embedding_features

def apply_features(statements, glove_embeddings):
    features = []
    for statement in tqdm(statements):
        nela_features = find_nela_features(statement)
        embedding_features = find_embedding_features(statement, glove_embeddings)
        all_features = nela_features + embedding_features
        features.append(all_features)
    np_features = np.array(features)
    return np_features

def transform():
    train_statement, train_label, test_statement, test_label, validation_statement, validation_label = get_and_preprocess_data()
    
    # only use the first 1000 samples for train and 300 for test and validation
    train_statement = train_statement[:1000]
    train_label = train_label[:1000]
    test_statement = test_statement[:300]
    test_label = test_label[:300]
    validation_statement = validation_statement[:300]
    validation_label = validation_label[:300]
    
    # Load glove embeddings
    glove_embeddings = {}
    print("Loading glove embeddings")
    with open('glove.6B.100d.txt', 'r') as f:
        for line in tqdm(f):
            values = line.split(' ')
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            glove_embeddings[word] = vector

    print("Transforming train dataset")
    train_features = apply_features(train_statement, glove_embeddings)
    print("Transforming test dataset")
    test_features = apply_features(test_statement, glove_embeddings)
    print("Transforming validation dataset")
    validation_features = apply_features(validation_statement, glove_embeddings)

    # now save the features + labels to a folder dataset/
    np.save('dataset/train_features.npy', train_features)
    np.save('dataset/train_label.npy', train_label)
    np.save('dataset/test_features.npy', test_features)
    np.save('dataset/test_label.npy', test_label)
    np.save('dataset/validation_features.npy', validation_features)
    np.save('dataset/validation_label.npy', validation_label)
    
    print('Transformed dataset with features and saved to dataset/ folder')



if __name__ == '__main__':
    transform()