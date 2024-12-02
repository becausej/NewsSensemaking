from google.cloud import language_v2
import newspaper
# Run the below once

# nltk.download('punkt_tab')
# nltk.download('punkt')

def sample_analyze_sentiment(text_content) -> None:
    client = language_v2.LanguageServiceClient()

    language_code = "en"
    document = {
        "content": text_content,
        "type_": language_v2.Document.Type.PLAIN_TEXT,
        "language_code": language_code,
    }

    encoding_type = language_v2.EncodingType.UTF8

    # SENTIMENT
    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )
    print(f"Document sentiment score: {response.document_sentiment.score}")
    print(f"Document sentiment magnitude: {response.document_sentiment.magnitude}")
    for sentence in response.sentences:
        print(f"Sentence text: {sentence.text.content}")
        print(f"Sentence sentiment score: {sentence.sentiment.score}")
        print(f"Sentence sentiment magnitude: {sentence.sentiment.magnitude}")

    sorted_entities = sorted(
        response.sentences,
        key=lambda sentence: abs(sentence.sentiment.score),
        reverse=True
    )
    extreme_sentences = sorted_entities[:5]
    # Print or return the extreme entities with their sentiment scores and magnitudes
    for sentence in extreme_sentences:
        print(f"Entity: {sentence.text.content}")
        print(f"Sentiment score: {sentence.sentiment.score}")
        print(f"Sentiment magnitude: {sentence.sentiment.magnitude}")
        print("---")


    print(f"Language of the text: {response.language_code}")

    # ENTITY ANALYSIS
    response = client.analyze_entities(
        request={"document": document, "encoding_type": encoding_type}
    )
    for entity in response.entities:
        print(f"Representative name for the entity: {entity.name}")

        # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al. See https://cloud.google.com/natural-language/docs/reference/rest/v2/Entity#type.
        print(f"Entity type: {language_v2.Entity.Type(entity.type_).name}")

        for metadata_name, metadata_value in entity.metadata.items():
            print(f"{metadata_name}: {metadata_value}")

        for mention in entity.mentions:
            print(f"Mention text: {mention.text.content}")
            print(
                "Mention type:" f" {language_v2.EntityMention.Type(mention.type_).name}"
            )
            print(f"Probability score: {mention.probability}")


from google.cloud import language_v1
def analyze_entity_sentiment(text):
    
    client = language_v1.LanguageServiceClient()
    type_ = language_v1.types.Document.Type.PLAIN_TEXT

    document = {"content": text, "type_": type_}
    encoding_type = language_v1.EncodingType.UTF8
    
    # ENTITY SENTIMENT
    response = client.analyze_entity_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    sorted_entities = sorted(
        response.entities,
        key=lambda entity: entity.sentiment.magnitude,
        reverse=True
    )
    top_entities = sorted_entities[:5]

    # Print or return the top entities with their sentiment magnitude
    for entity in top_entities:
        print(f"Entity: {entity.name}")
        print(f"Sentiment magnitude: {entity.sentiment.magnitude}")
        print(f"Sentiment score: {entity.sentiment.score}")
        print(f"Entity type: {language_v1.Entity.Type(entity.type_).name}")
        for metadata_name, metadata_value in entity.metadata.items():
          print(f"{metadata_name} = {metadata_value}")
        print("---")

    # Sort entities by absolute sentiment score
    sorted_entities = sorted(
        response.entities,
        key=lambda entity: abs(entity.sentiment.score),
        reverse=True
    )
  
    extreme_entities = sorted_entities[:5]

    # Print or return the extreme entities with their sentiment scores and magnitudes
    for entity in extreme_entities:
        print(f"Entity: {entity.name}")
        print(f"Sentiment score: {entity.sentiment.score}")
        print(f"Sentiment magnitude: {entity.sentiment.magnitude}")
        print("---")

    with open("output.txt", "w") as file:
    # Loop through entitites returned from the API
      for entity in response.entities:

          file.write(f"Representative name for the entity: {entity.name}\n")
          # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
          file.write(f"Entity type: {language_v1.Entity.Type(entity.type_).name}\n")
          # Get the salience score associated with the entity in the [0, 1.0] range
          file.write(f"Salience score: {entity.salience}")
          # Get the aggregate sentiment expressed for this entity in the provided document.
          sentiment = entity.sentiment
          file.write(f"Entity sentiment score: {sentiment.score}\n")
          file.write(f"Entity sentiment magnitude: {sentiment.magnitude}\n")
          # Loop over the metadata associated with entity. For many known entities,
          # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
          # Some entity types may have additional metadata, e.g. ADDRESS entities
          # may have metadata for the address street_name, postal_code, et al.
          for metadata_name, metadata_value in entity.metadata.items():
              file.write(f"{metadata_name} = {metadata_value}\n")

          # Loop over the mentions of this entity in the input document.
          # The API currently supports proper noun mentions.
          for mention in entity.mentions:
              file.write(f"Mention text: {mention.text.content}\n")
              # Get the mention type, e.g. PROPER for proper noun
              file.write(
                  "Mention type: {}\n".format(
                      language_v1.EntityMention.Type(mention.type_).name
                  )
              )

#sample_analyze_sentiment()

url = "https://www.nytimes.com/2024/11/03/us/politics/harris-trump-times-siena-poll.html"
url = "https://www.infowars.com/posts/roger-stone-the-democrats-are-playing-possum-planning-to-strike-back"
url = "https://www.newyorker.com/magazine/dispatches/what-does-it-mean-that-donald-trump-is-a-fascist"
# url = "https://www.infowars.com/posts/your-kids-are-already-communist-and-college-will-make-it-worse"
# url = "https://abcnews.go.com/Politics/trump-gets-warm-house-republicans-1st-stop-back/story?id=115810334"
url = "https://www.foxnews.com/media/feminists-argue-trad-wife-influencers-social-media-may-have-helped-trump-win-over-womens-vote"

article = newspaper.article(url)
text = article.text
print(text)

analyze_entity_sentiment(text)
print("-----------------------")
sample_analyze_sentiment(text)
# sample_analyze_sentiment(text)

