from google.cloud import language_v2
from google.cloud import language_v1
import newspaper
from collections import defaultdict

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
  highest_categories = sorted_categories[:2]

  for category in highest_categories:
        print(f"Category name: {category.name}")
        print(f"Confidence: {round(category.confidence, 3)}")

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
    extreme_sentences = sorted_sentiments[:5]

    for sentence in extreme_sentences:
        print(f"Entity: {sentence.text.content}")
        print(f"Sentiment score: {round(sentence.sentiment.score, 5)}")
        print(f"Sentiment magnitude: {round(sentence.sentiment.magnitude, 5)}\n")

def analyze_entity_sentiment(text):
    client = language_v1.LanguageServiceClient()
    type_ = language_v1.types.Document.Type.PLAIN_TEXT

    document = {"content": text, "type_": type_}
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

def help_combine_entities(all_entities):
    combined_entities = defaultdict(lambda: {
        'sentiment_score': 0,
        'sentiment_magnitude': 0,
        'metadata': [],
        'count': 0
    })

    for entity in all_entities:
        key = entity.name.lower()
        combined_entities[key]['sentiment_score'] += entity.sentiment.score
        combined_entities[key]['sentiment_magnitude'] += entity.sentiment.magnitude
        combined_entities[key]['count'] += 1
        combined_entities[key]['metadata'] += entity.metadata

    entity_averages = {}
    entity_averages = {}
    for key, value in combined_entities.items():
        entity_averages[key] = {
            'sentiment_score': value['sentiment_score'] / value['count'],
            'sentiment_magnitude': value['sentiment_magnitude'] / value['count'],
            'metadata': value['metadata']  
    }
    return entity_averages

# url = "https://www.nytimes.com/2024/11/03/us/politics/harris-trump-times-siena-poll.html"
# url = "https://www.infowars.com/posts/roger-stone-the-democrats-are-playing-possum-planning-to-strike-back"
# url = "https://www.infowars.com/posts/your-kids-are-already-communist-and-college-will-make-it-worse"
# url = "https://abcnews.go.com/Politics/trump-gets-warm-house-republicans-1st-stop-back/story?id=115810334"

# url = "https://www.foxnews.com/media/feminists-argue-trad-wife-influencers-social-media-may-have-helped-trump-win-over-womens-vote"
url = "https://www.newyorker.com/magazine/dispatches/what-does-it-mean-that-donald-trump-is-a-fascist"

article = newspaper.article(url)
text = article.text

classify_text(text)
analyze_sentiment(text)
analyze_entity_sentiment(text)