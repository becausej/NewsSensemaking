from nela_features.nela_features import NELAFeatureExtractor
from flask import jsonify

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
    return jsonify({'smog_score': smog_to_text(complexity_vector[4]) + " Reading Level", 'message': 'Success'})