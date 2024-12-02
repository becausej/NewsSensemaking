import pandas as pd
import jellyfish
import tldextract

def get_allsides(url):
    allsides = pd.read_csv('dataset/allsides.csv')
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
    #distances = [jellyfish.levenshtein_distance(website.lower(), x.lower()) for x in sources]
    #loc = distances.index(min(distances))
    distances = [jellyfish.jaro_similarity(website.lower(), x.lower()) for x in sources]
    loc = distances.index(max(distances))
    #source_allsides_format = sources[loc]
    row = allsides_vals[loc]
    return row