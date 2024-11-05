from flask import Flask, jsonify, render_template
from apify_client import ApifyClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import pandas as pd

app = Flask(__name__)

# Initialize ApifyClient and TextAnalyticsClient with your credentials
client = ApifyClient(
    "apify_api_161VWbPtMkCidsrmli8TCbD65qJOlt45tH36"
)  # Replace with your actual token
azure_endpoint = "https://nestleanalysis.cognitiveservices.azure.com/"
azure_api_key = "2lOmejx1yLk6eRrafw4x6zz8hrY6Svxoksk1vYPCitRgBSgVbRX9JQQJ99AKACYeBjFXJ3w3AAAaACOGX3EP"

text_analytics_client = TextAnalyticsClient(
    endpoint=azure_endpoint, credential=AzureKeyCredential(azure_api_key)
)


def fetch_and_analyze_sentiment():
    # Apify settings to retrieve social media posts
    run_input = {
        "directUrls": [
            "https://www.instagram.com/nestle/",
            "https://www.instagram.com/nespresso/",
        ],
        "resultsType": "posts",
        "resultsLimit": 2,
        "searchType": "hashtag",
        "searchLimit": 1,
        "addParentData": False,
    }

    # Run Apify Actor to get data
    run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
    items = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]

    # Extract comments
    comments = []
    for post in items:
        brand = post["inputUrl"].split("/")[-2]
        if "latestComments" in post:
            for comment in post["latestComments"]:
                comment_data = {"text": comment["text"], "brand": brand}
                comments.append(comment_data)

    # Perform sentiment analysis on comments in batches of 10
    batch_size = 10
    for i in range(0, len(comments), batch_size):
        batch = comments[i : i + batch_size]  # Slice the batch of up to 10 comments
        texts = [comment["text"] for comment in batch]
        response = text_analytics_client.analyze_sentiment(texts)

        # Append sentiment and confidence scores to each comment
        for j, sentiment in enumerate(response):
            batch[j]["sentiment"] = sentiment.sentiment
            # Convert confidence scores to a dictionary
            batch[j]["confidence_scores"] = {
                "positive": sentiment.confidence_scores.positive,
                "neutral": sentiment.confidence_scores.neutral,
                "negative": sentiment.confidence_scores.negative,
            }

     # Calculate sentiment counts
    sentiment_df = pd.DataFrame(comments)
    sentiment_counts = sentiment_df["sentiment"].value_counts().to_dict()

    return {
        "overallSentimentScore": sentiment_counts,
        "positiveScore": sentiment_counts.get("positive", 0),
        "neutralScore": sentiment_counts.get("neutral", 0),
        "negativeScore": sentiment_counts.get("negative", 0),
        "trend": comments,
    }


# Endpoint to fetch sentiment data
@app.route("/sentiment-data", methods=["GET"])
def sentiment_data():
    data = fetch_and_analyze_sentiment()
    return jsonify(data)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5000)
