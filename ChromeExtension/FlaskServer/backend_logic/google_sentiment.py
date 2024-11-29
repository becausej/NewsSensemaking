from flask import jsonify
from google.cloud import language_v2
from google.cloud import language_v1
from collections import defaultdict

def analyze_sentiment(text):
    client = language_v2.LanguageServiceClient()
    document = {"content": text, "type_": language_v2.Document.Type.PLAIN_TEXT}
    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )
    return response

def get_max_sentence(text):
    data = analyze_sentiment(text)

    sorted_sentiments = sorted(
        data.sentences,
        key=lambda sentence: abs(sentence.sentiment.score), #maybe pick out top positive and top negative?
        reverse=True
    )
    max_sentence = sorted_sentiments[0]

    return jsonify({'max_sentence': max_sentence.text.content,
                  'max_sentence_score': max_sentence.sentiment.score,
                  'message': 'Success'})

def get_sentiment_values(text):
    data = analyze_sentiment(text)

    return jsonify({'total_sentiment': data.document_sentiment.score,
                  'message': 'Success'})

# Analyze sentiment for each entity
def analyze_entity_sentiment(text):
    client = language_v1.LanguageServiceClient()
    document = {"content": text, "type_": language_v1.types.Document.Type.PLAIN_TEXT}
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entity_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    combined_entities = help_combine_entities(response.entities)

    high_magnitude_entities = sorted(
        combined_entities.items(),
        key=lambda x: x[1]['sentiment_magnitude'],
        reverse=True
    )
    top_magnitude_entities = high_magnitude_entities[:5]
    print("\nHighest Magnitude Sentiment")
    print(top_magnitude_entities)

    high_sentiment_entities = sorted(
        combined_entities.items(),
        key=lambda x: abs(x[1]['sentiment_score']),
        reverse=True
    )
    top_sentiment_entities = high_sentiment_entities[:5]
    print("\nMost Extreme Sentiments")
    print(top_sentiment_entities)

# simplify same name entities
def help_combine_entities(all_entities):
    count = 'count'
    sentiment_score = 'sentiment_score'
    sentiment_magnitude = 'sentiment_magnitude'
    metadata ='metadata'

    combined_entities = defaultdict(lambda: {
        sentiment_score: 0,
        sentiment_magnitude: 0,
        metadata: [],
        count: 0
    })

    for entity in all_entities:
        key = entity.name.lower()
        combined_entities[key][sentiment_score] += entity.sentiment.score
        combined_entities[key][sentiment_magnitude] += entity.sentiment.magnitude
        combined_entities[key][count] += 1
        combined_entities[key][metadata] += entity.metadata

    entity_averages = {}
    for key, value in combined_entities.items():
        entity_averages[key] = {
            sentiment_score: value[sentiment_score] / value[count],
            sentiment_magnitude: value[sentiment_magnitude] / value[count],
            metadata: value[metadata]  
    }
    return entity_averages