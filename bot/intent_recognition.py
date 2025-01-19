import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

def load_intents(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def train_intent_classifier(intents):
    sentences = [pattern for intent in intents["intents"] for pattern in intent["patterns"]]
    labels = [intent["tag"] for intent in intents["intents"] for _ in intent["patterns"]]

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(sentences)
    model = MultinomialNB()
    model.fit(X, labels)

    return model, vectorizer

def classify_intent(model, vectorizer, message):
    return model.predict(vectorizer.transform([message]))[0]

# Load intents and train model
if __name__ == "__main__":
    intents = load_intents("intents.json")
    model, vectorizer = train_intent_classifier(intents)
    print(classify_intent(model, vectorizer, "hello"))
