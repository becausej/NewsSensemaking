from flask import jsonify
from google.cloud import language_v2

def analyze_sentiment(text) -> None:
    client = language_v2.LanguageServiceClient()
    document = {"content": text, "type_": language_v2.Document.Type.PLAIN_TEXT}
    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    sorted_sentiments = sorted(
        response.sentences,
        key=lambda sentence: abs(sentence.sentiment.score), #maybe pick out top positive and top negative?
        reverse=True
    )

    return sentiment_json(response.document_sentiment.score, 
                          sorted_sentiments[0].text.content, 
                          sorted_sentiments[0].sentiment.score)

def sentiment_json(doc_sentiment, sentence, sentence_score):
  return jsonify({'total_sentiment': doc_sentiment, 
                  'max_sentence': sentence,
                  'max_sentence_score': sentence_score,
                  'message': 'Success'})