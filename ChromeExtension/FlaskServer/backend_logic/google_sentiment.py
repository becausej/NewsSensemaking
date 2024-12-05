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

    if not sorted_sentiments:
        return jsonify({'message': 'Failed'})
    
    response = {}
    unique_sentences = set()
    keys = ['max_sentence', 'max_sentence_two', 'max_sentence_three']

    for sentence in sorted_sentiments:
        if len(unique_sentences) >= 3:
            break 
        if sentence.text.content not in unique_sentences:
            key_prefix = keys[len(unique_sentences)]
            response[key_prefix] = sentence.text.content
            response[f'{key_prefix}_score'] = sentence.sentiment.score
            unique_sentences.add(sentence.text.content)

    response['message'] = 'Success'

    return jsonify(response)

def get_sentiment_values(text):
    data = analyze_sentiment(text)
    category = classify_text(text)
    if category.startswith("/"):
        category = category[1:]
    category = category.replace("/", ",")
    return jsonify({'total_sentiment': data.document_sentiment.score,
                    'category': category,
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

# classifies text based on Google's predefined categories
def classify_text(text):
    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    document = {"content": text, "type_": type_}

    response = client.classify_text(
        request={
            "document": document,
            "classification_model_options": {
                "v2_model": {"content_categories_version": language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2}
            },
        }
    )
  
    sorted_categories = sorted(
        response.categories,
        key=lambda entity: abs(entity.confidence),
        reverse=True
    )
    if (len(sorted_categories) < 1):
        return ""
    return sorted_categories[0].name