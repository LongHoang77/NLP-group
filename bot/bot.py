import discord
from discord.ext import commands
import requests
from intent_recognition import load_intents, train_intent_classifier, classify_intent
from sentiment_analysis import analyze_sentiment
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")  # Store your API Gateway URL in the .env file
OLLAMA_URL = "http://127.0.0.1:11434"  # Change this if you're using a remote Ollama API

# Load intents and train model
custom_intents = load_intents("intents.json")
model, vectorizer = train_intent_classifier(custom_intents)


# Discord Bot Configuration
bot_intents = discord.Intents.default()
bot_intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="!", intents=bot_intents)


# Function to call Ollama API for NLP processing
def get_ollama_response(user_message):
    payload = {
        "prompt": user_message,
        "max_tokens": 100
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response_data = response.json()
        return response_data.get("choices", [{}])[0].get("text", "Sorry, I couldn't understand.")
    except requests.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return "Error connecting to Ollama."

# Function to call AWS Lambda for saving data to DynamoDB
def save_to_dynamodb(user_id, message, response):
    payload = {
        "user_id": str(user_id),
        "message": message,
        "response": response
    }
    try:
        response = requests.post(API_GATEWAY_URL, json=payload)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error saving data: {e}")
        return False

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_message = message.content.lower()

    # Classify intent (optional)
    intent = classify_intent(model, vectorizer, user_message)

    # Analyze sentiment (optional)
    sentiment = analyze_sentiment(user_message)

    # Get response from Ollama API
    response = get_ollama_response(user_message)

    # Save conversation to DynamoDB via AWS Lambda
    if save_to_dynamodb(user_id=message.author.id, message=user_message, response=response):
        print("Data saved successfully")
    else:
        print("Failed to save data")

    # Send response to user
    await message.channel.send(response)

# Run the bot
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Bot token not found. Please check your .env file.")
