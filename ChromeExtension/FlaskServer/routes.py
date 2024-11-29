from flask import Blueprint, request
import newspaper
from backend_logic.google_sentiment import analyze_sentiment

bp = Blueprint('routes', __name__)

@bp.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    url = data.get('url', '')

    article = newspaper.article(url)
    text = article.text

    return analyze_sentiment(text)
