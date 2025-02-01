from transformers import pipeline

# Initialize sentiment analysis pipeline globally to avoid reloading every call
sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(message):
    result = sentiment_pipeline(message)
    label = result[0]["label"]

    # Standardize the labels
    if label in ["NEGATIVE"]:  # Handle different model outputs
        return "negative"
    elif label in ["LABEL_1", "POSITIVE"]:
        return "positive"
    else:
        return "neutral"
    
# Test the function
if __name__ == "__main__":
    print(analyze_sentiment("I am very disappointed in you!"))

