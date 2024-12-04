import asyncio
import numpy as np
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

async def process_statement(statement, glove_embeddings):
    nela_features, nela_names = find_nela_features(statement)
    embedding_features, embeddings_names = find_embedding_features(statement, glove_embeddings)
    sentiment = analyze_sentiment(statement)
    all_features = nela_features + embedding_features + [sentiment]
    names = nela_names + embeddings_names + ['sentiment']
    return all_features, names

async def apply_features(statements, glove_embeddings):
    tasks = [
        process_statement(statement, glove_embeddings)
        for statement in statements
    ]
    features = []
    names = []
    outputs = await asyncio.gather(*tasks)
    for o in outputs:
        features.append(o[0])
        names = o[1]
    np_features = np.array(features)
    return np_features, names

if __name__ == "__main__":
    ## New code here to load and test data ##
    ## This can be run independently of the above code ##
    import pandas as pd

    # load the data
    X_test = pd.read_csv('dataset/X_test.csv')
    y_test = pd.read_csv('dataset/y_test.csv')
    X_train = pd.read_csv('dataset/X_train.csv')
    y_train = pd.read_csv('dataset/y_train.csv')
    
    # # Drop bad columns from X
    # bad_columns = ['allpunc', 'word_count', 'allcaps', 'EX', 'IN', 'JJR',
    #                'LS', 'NN', 'NNPS', 'PDT', 'POS', 'PRP', 'exclaim',
    #                'RB', 'RBR', 'RBS', 'SYM', 'TO', 'UH', 'WP$', 'WRB', 'VBD', 'VBG',
    #                'VBN', 'VBZ', 'WDT', 'WP', '$', "''", '(', ')', ',', '--', '.', ':',
    #                '``', 'lix', 'factives', 'hedges', 'implicatives', 'report_verbs',
    #                'negative_opinion_words', 'vadneg', 'vadneu', 'vadpos', 'wneg', 'wpos',
    #                'sneg', 'spos', 'HarmVice', 'FairnessVirtue', 'FairnessVice',
    #                'IngroupVirtue', 'IngroupVice', 'AuthorityVirtue', 'AuthorityVice',
    #                'PurityVirtue', 'PurityVice', 'MoralityGeneral', 'num_locations', 'num_dates']
    
    # Drop all columns BUT test_embeddings and sentiment
    test_embeddings_names = [test_embedding['name'] for test_embedding in test_embeddings]
    test_embeddings_names.append('sentiment')
    test_embeddings_names.append('bias_words')
    _, tmp = nela.extract_style('test')
    not_tmp = ['quotes', 'exclaim', 'allpunc', 'allcaps', 'stops', 'WP$', '(', 'UH', 'SYM', 'RBR', '$', 'POS', ')', ',', "''", 'EX', '``', '--', 'LS', '.', ':', 'NNPS', 'FW', 'JJR', 'MD', 'RBS', 'VBG', 'PDT', 'RP', 'VBN', 'TO', 'PRP$', 'RB', 'PRP', 'VBZ', 'VBD', 'WDT', 'VB']
    tmp = [t for t in tmp if t not in not_tmp]
    test_embeddings_names += tmp
    bad_columns = [col for col in X_train.columns if col not in test_embeddings_names]
    X_test = X_test.drop(columns=bad_columns)
    X_train = X_train.drop(columns=bad_columns)
    X_train_copy = X_train.copy()
    
    # Run an xgboost model on the data, use grid search to find the best hyperparameters
    # Then after we find the best hyperparameters, we will use the best threshold to find the best probability threshold
    # Then lastly we will look at the feature importances
    import xgboost as xgb
    from sklearn.model_selection import GridSearchCV
    from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_curve, roc_auc_score, f1_score
    import matplotlib.pyplot as plt
    import numpy as np
    # normalize features using standard scaler
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = xgb.XGBClassifier()
    param_grid = {
        'max_depth': [5],
        'n_estimators': [200],
        'learning_rate': [0.1],
        'subsample': [0.9],
        'reg_alpha': [0.01],
        'reg_lambda': [3],
    }
    grid_search = GridSearchCV(model, param_grid, cv=5, n_jobs=-1)
    grid_search.fit(X_train, y_train)
    print("Best Parameters: ", grid_search.best_params_)
    model = grid_search.best_estimator_
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:,1]

    print("Accuracy: ", accuracy_score(y_test, y_pred))
    print("Training Accuracy: ", accuracy_score(y_train, model.predict(X_train)))
    print("Confusion Matrix: ", confusion_matrix(y_test, y_pred))
    print("Classification Report: ", classification_report(y_test, y_pred))

    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    print("AUC: ", roc_auc)

    plt.figure()
    plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

    f1_scores = []
    for threshold in thresholds:
        y_pred_threshold = y_pred_proba > threshold
        f1_scores.append(f1_score(y_test, y_pred_threshold))
        
    best_threshold = thresholds[np.argmax(f1_scores)]
    print("Best Threshold: ", best_threshold)

    # classifcation report and accuracy with best threshold
    y_pred_threshold = y_pred_proba > best_threshold
    print("Accuracy: ", accuracy_score(y_test, y_pred_threshold))
    print("Confusion Matrix: ", confusion_matrix(y_test, y_pred_threshold))
    print("Classification Report: ", classification_report(y_test, y_pred_threshold))

    # find the feature importances
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    plt.figure()
    plt.title("Feature importances")
    plt.bar(range(X_train.shape[1]), importances[indices], align="center")
    plt.xticks(range(X_train.shape[1]), X_train_copy.columns[indices], rotation=90)
    plt.xlim([-1, X_train.shape[1]])
    plt.show()
    
    # Save the model
    import pickle
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    # save scaler
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    