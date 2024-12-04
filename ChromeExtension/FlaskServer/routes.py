from flask import Blueprint, request, jsonify
import newspaper
import numpy as np
from backend_logic.google_sentiment import get_max_sentence, get_sentiment_values
from backend_logic.analyze_sentence import predict_sentence
from backend_logic.classify_article import get_knn_class_text
from backend_logic.smog import get_nela_smog_text
from backend_logic.allsides import get_allsides
bp = Blueprint('routes', __name__)
# cached calls contains:
# key: url, value: {'query': query, 'response': response}
cached_calls = {}

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
    url = data.get('url', '')
    if url in cached_calls and 'get_max_sentence' in cached_calls[url]:
        return cached_calls[url]['cached_calls']
    text = getTextFromUrl(url)
    response = get_max_sentence(text)
    cached_calls[url] = {'get_max_sentence': response}
    return response

@bp.route('/get_analysis', methods=['POST'])
def sentiment():
    data = request.json
    url = data.get('url', '')
    if url in cached_calls and 'get_analysis' in cached_calls[url]:
        return cached_calls[url]['get_analysis']
    text = getTextFromUrl(url)
    response = get_sentiment_values(text)
    cached_calls[url] = {'get_analysis': response}
    return response

@bp.route('/classify_sentence', methods=['POST'])
def classify():
    data = request.get_json()
    sentence = data.get('sentence', '')
    url = data.get('url', '')
    if url in cached_calls and 'classify_sentence' + sentence in cached_calls[url]:
        return cached_calls[url]['classify_sentence' + sentence]
    if len(sentence.strip().split(' ')) < 5 or sentence is None:
        return jsonify({'score': 0,
                  'message': 'Success'})
    score = predict_sentence(sentence, glove_embeddings, threshold=0.8)
    response = jsonify({'score': score, 'message': 'Success'})
    cached_calls[url] = {'classify_sentence' + sentence: response}
    return response

@bp.route('/bias_indicator', methods=['POST'])
def bias_indicator():
    data = request.json
    url = data.get('url', '')
    if url in cached_calls and 'bias_indicator' in cached_calls[url]:
        return cached_calls[url]['bias_indicator']
    text = getTextFromUrl(url)
    # split text into sentences
    sentences = text.split('.')
    total = 0
    print("Starting bias indicator")
    tot_words = 0
    for sentence in sentences:
        total += predict_sentence(sentence, glove_embeddings, threshold=0.5) * len(sentence.split(' '))
        tot_words += len(sentence.split(' '))
    output = total / tot_words * 100
    if len(sentences) == 0:
        response = jsonify({'score': 0,
                  'message': 'Success'})
        cached_calls[url] = {'bias_indicator': response}
        return response
    response = jsonify({'score': output,
                    'message': 'Success'})
    cached_calls[url] = {'bias_indicator': response}
    return response

@bp.route('/classify_full_text', methods=['POST'])
def classify_text():
    data = request.get_json()
    url = data.get('url', '')
    if url in cached_calls and 'classify_full_text' in cached_calls[url]:
        return cached_calls[url]['classify_full_text']
    text = data.get('text', '')
    response = get_knn_class_text(text,glove_embeddings)
    cached_calls[url] = {'classify_full_text': response}
    return response

@bp.route('/smog_full_text', methods=['POST'])
def smog_text():
    data = request.get_json()
    url = data.get('url', '')
    if url in cached_calls and 'smog_full_text' in cached_calls[url]:
        return cached_calls[url]['smog_full_text']
    text = data.get('text', '')
    response = get_nela_smog_text(text)
    cached_calls[url] = {'smog_full_text': response}
    return response

@bp.route('/allsides_rating', methods=['POST'])
def allsides_text():
    data = request.get_json()
    url = data.get('url', '')
    if url in cached_calls and 'allsides_rating' in cached_calls[url]:
        return cached_calls[url]['allsides_rating']
    response = get_allsides(url)
    cached_calls[url] = {'allsides_rating': response}
    return response

def sentiment_json(doc_sentiment, sentence, sentence_score):
    return jsonify({'total_sentiment': doc_sentiment, 
                  'max_sentence': sentence,
                  'max_sentence_score': sentence_score,
                  'message': 'Success'})

def getTextFromUrl(url):
    article = newspaper.article(url)
    return article.text