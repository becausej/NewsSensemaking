from flask import Blueprint, request, jsonify
import newspaper
from backend_logic.google_sentiment import get_max_sentence, get_sentiment_values

bp = Blueprint('routes', __name__)

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

def sentiment_json(doc_sentiment, sentence, sentence_score):
    return jsonify({'total_sentiment': doc_sentiment, 
                  'max_sentence': sentence,
                  'max_sentence_score': sentence_score,
                  'message': 'Success'})

def getTextFromUrl(url):
    article = newspaper.article(url)
    return article.text