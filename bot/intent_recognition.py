import json
import random
import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertModel
from torch import nn
import numpy as np

# Function to load intents
def load_intents(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Reusing the BertClassifier from the training script
class BertClassifier(nn.Module):
    def __init__(self, dropout=0.2, num_classes=22):  # num_classes adjusted to match cfg.num_classes
        super(BertClassifier, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-cased')
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, num_classes)

    def forward(self, input_id, mask):
        _, pooled_output = self.bert(input_ids=input_id, attention_mask=mask, return_dict=False)
        dropout_output = self.dropout(pooled_output)
        linear_output = self.linear(dropout_output)
        return linear_output

# Function to load the trained model
def load_trained_model(model_path, num_classes=22):
    model = BertClassifier(num_classes=num_classes)  # Adjust num_classes as per training configuration
    tokenizer = BertTokenizer.from_pretrained('bert-base-cased')  # Use the same tokenizer

    try:
        # Load saved state_dict
        state_dict = torch.load(model_path, map_location=torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
        model.load_state_dict(state_dict)
        print("Model weights loaded successfully.")
    except Exception as e:
        print(f"Error loading model weights: {e}")

    model.eval()  # Set the model to evaluation mode
    return model, tokenizer

# Predict function
def predict(model, tokenizer, text, max_length=15):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    text_dict = tokenizer(text, padding='max_length', max_length=len(text.split()) + 2, truncation=True, return_tensors="pt")
    input_id = text_dict['input_ids'].to(device)
    mask = text_dict['attention_mask'].to(device)

    with torch.no_grad():
        output = model(input_id, mask)
        probabilities = F.softmax(output, dim=1)  # Convert logits to probabilities
        confidence, label_id = torch.max(probabilities, dim=1)
        return label_id.item(), confidence.item()

# Function to retrieve a random response based on intent
def get_response_for_intent(intents, intent):
    for item in intents["intents"]:
        if item["intent"] == intent:
            responses = item.get("responses", [])
            if responses:
                return random.choice(responses)
    return None

# Main script
if __name__ == "__main__":
    intents_path = "intents.json"
    model_path = "bert_intent_classifier.pth"

    intents = load_intents(intents_path)
    model, tokenizer = load_trained_model(model_path)

    labels = {intent["intent"]: idx for idx, intent in enumerate(intents["intents"])}
    label_to_intent = {idx: intent for intent, idx in labels.items()}

    # Test with a sample message
    test_message = "My name is Adam"
    predicted_label = predict(model, tokenizer, test_message)
    predicted_intent = label_to_intent[predicted_label]

    response = get_response_for_intent(intents, predicted_intent)

    print(f"User Message: {test_message}")
    print(f"Predicted Intent: {predicted_intent}")
    print(f"Bot Response: {response}")
