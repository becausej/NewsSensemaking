import pandas as pd
import jellyfish
import tldextract
from flask import jsonify

def get_allsides(url):
    allsides = pd.read_csv('backend_logic/allsides.csv')
    parsed = tldextract.extract(url)
    website = parsed.domain
    allsides_vals = allsides.values
    sources = allsides_vals[:,0]
    rows = [row for row in allsides_vals if website.lower() in row[0].lower()]
    if rows == []:
        rows = [row for row in allsides_vals if website.lower()[:3] in row[0].lower() and website.lower()[:3] != 'the']
    if rows != []:
        rows.sort(key = lambda x: x[2],reverse=True)
        return rows[0]
    distances = [jellyfish.jaro_similarity(website.lower(), x.lower()) for x in sources]
    loc = distances.index(max(distances))
    row = allsides_vals[loc]
    dict = {'center':50,'left-center':25,'left':5,'right-center':75,'right':95}
    return jsonify({'allsides_rating': dict[row[1]], 'message': 'Success'})