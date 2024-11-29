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

# Analyzes sentiment by document+sentence
def analyze_sentiment(text) -> None:
    client = language_v2.LanguageServiceClient()
    document = {"content": text, "type_": language_v2.Document.Type.PLAIN_TEXT}
    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    print(f"Document sentiment score: {response.document_sentiment.score}\n")
    
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

# identiifes relevant entities, still not sure it's useful
def find_entities(text) -> None:
    client = language_v2.LanguageServiceClient()
    document = {"content": text, "type_": language_v2.Document.Type.PLAIN_TEXT}
    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_entities(
        request={"document": document, "encoding_type": encoding_type}
    )

    for entity in response.entities:
        print(f"Representative name for the entity: {entity.name}")

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

# simplify same name entities #TODO consider cross-referencing with just entity analysis to filter out regular words
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

# sensitive topics
def analyze_sensitivity(text) -> None:
    client = language_v2.LanguageServiceClient()
    document = {"content": text, "type_": language_v2.Document.Type.PLAIN_TEXT}
    encoding_type = language_v2.EncodingType.UTF8

    response = client.moderate_text(
        request={"document": document}
    )

    sorted_categories = sorted(
        response.moderation_categories, 
        key=lambda x: x.confidence, 
        reverse=True
    )
    extreme_categories = sorted_categories[:5]

    print(extreme_categories)
    
# url = "https://www.nytimes.com/2024/11/03/us/politics/harris-trump-times-siena-poll.html"
# url = "https://www.infowars.com/posts/roger-stone-the-democrats-are-playing-possum-planning-to-strike-back"
# url = "https://www.infowars.com/posts/your-kids-are-already-communist-and-college-will-make-it-worse"
# url = "https://abcnews.go.com/Politics/trump-gets-warm-house-republicans-1st-stop-back/story?id=115810334"

url = "https://www.foxnews.com/media/feminists-argue-trad-wife-influencers-social-media-may-have-helped-trump-win-over-womens-vote"
#url = "https://www.newyorker.com/magazine/dispatches/what-does-it-mean-that-donald-trump-is-a-fascist"
url = "https://www.reuters.com/technology/australia-passes-social-media-ban-children-under-16-2024-11-28/"
url = "https://www.nbcsportsboston.com/nfl/new-england-patriots/fix-offense-tee-higgins-free-agency-nfl-draft/670127/"

article = newspaper.article(url)
text = article.text

print("CLASSIFY ARTICLE CONTENT")
classify_text(text)
print("\nHIGHEST SENTIMENT SENTENCES")
analyze_sentiment(text)
print("\nENTITY-SENTIMENT")
analyze_entity_sentiment(text)
print("\nSENSITIVE TOPICS")
analyze_sensitivity(text)
find_entities(text)

# import gdelt

# # Version 1 queries
# gd1 = gdelt.gdelt(version=1)

# # pull single day, gkg table
# results= gd1.Search('2016 Nov 01',table='gkg')
# print(len(results))

# # pull events table, range, output to json format
# results = gd1.Search(['2016 Oct 31','2016 Nov 2'],coverage=True,table='events')
# print(len(results))
