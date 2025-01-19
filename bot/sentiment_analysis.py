from transformers import pipeline

# Initialize sentiment analysis pipeline
def analyze_sentiment(message):
    sentiment_pipeline = pipeline("sentiment-analysis")
    result = sentiment_pipeline(message)
    return result[0]["label"]  # Returns POSITIVE, NEGATIVE, or NEUTRAL

# Test the function
if __name__ == "__main__":
    print(analyze_sentiment("I am very happy today!"))
