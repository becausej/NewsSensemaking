from flask import Blueprint, request, jsonify
import newspaper
import numpy as np
from backend_logic.google_sentiment import get_max_sentence, get_sentiment_values
from backend_logic.analyze_sentence import predict_sentence
from backend_logic.classify_article import get_knn_class_text
from backend_logic.smog import get_nela_smog_text
from backend_logic.allsides import get_allsides
bp = Blueprint('routes', __name__)

# Load glove embeddings
glove_embeddings = {}
print("Loading glove embeddings")
with open('backend_logic/glove.6B.100d.txt', 'r', encoding='utf8') as f:
    for line in f:
        values = line.split(' ')
        word = values[0]
        vector = np.asarray(values[1:], "float32")
        glove_embeddings[word] = vector
print("Glove embeddings loaded")

@bp.route('/get_max_sentence', methods=['POST'])
def max_sentence():
    data = request.json
    text = getTextFromUrl(data.get('url', ''))
    return get_max_sentence(text)

@bp.route('/get_analysis', methods=['POST'])
def sentiment():
    data = request.json
    text = getTextFromUrl(data.get('url', ''))
    return get_sentiment_values(text)

@bp.route('/classify_sentence', methods=['POST'])
def classify():
    data = request.get_json()
    sentence = data.get('sentence', '')
    if sentence.strip() == '' or sentence is None:
        return 0
    return jsonify({'score': predict_sentence(sentence, glove_embeddings),
                  'message': 'Success'})

@bp.route('/bias_indicator', methods=['POST'])
def bias_indicator():
    data = request.json
    text = getTextFromUrl(data.get('url', ''))
    # split text into sentences
    sentences = text.split('.')
    total = 0
    for sentence in sentences:
        total += predict_sentence(sentence, glove_embeddings)
    if len(sentences) == 0:
        return jsonify({'score': 0,
                  'message': 'Success'})
    return jsonify({'score': total / len(sentences) * 100,
                  'message': 'Success'})

@bp.route('/classify_full_text', methods=['POST'])
def classify_text():
    data = request.get_json()
    text = data.get('text', '')
    return get_knn_class_text(text,glove_embeddings)

@bp.route('/smog_full_text', methods=['POST'])
def smog_text():
    data = request.get_json()
    text = data.get('text', '')
    return get_nela_smog_text(text)

@bp.route('/allsides_rating', methods=['POST'])
def allsides_text():
    data = request.get_json()
    url = data.get('url', '')
    return get_allsides(url)

def sentiment_json(doc_sentiment, sentence, sentence_score):
    return jsonify({'total_sentiment': doc_sentiment, 
                  'max_sentence': sentence,
                  'max_sentence_score': sentence_score,
                  'message': 'Success'})

def getTextFromUrl(url):
    article = newspaper.article(url)
    return article.text