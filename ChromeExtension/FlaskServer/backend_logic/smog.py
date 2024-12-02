from nela_features.nela_features import NELAFeatureExtractor
import newspaper
from flask import jsonify

def get_article_text(url):
    return newspaper.article(url).text

def smog_to_text(smog):
    if smog >= 17:
        return "Graduate"
    if smog >= 13:
        return "Undergraduate"
    if smog >= 9:
        return "High School"
    if smog >= 5:
        return "Middle School"
    else:
        return "Elementary School"


def get_nela_smog_text(text):
    nela = NELAFeatureExtractor()
    complexity_vector, complexity_names = nela.extract_complexity(text)
    return smog_to_text(complexity_vector[4])


def get_nela_smog(url):
    text = get_article_text(url)
    return jsonify({'smog_score': get_nela_smog_text(text), 'message': "smog not doomed"})