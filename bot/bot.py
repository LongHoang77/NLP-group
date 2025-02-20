import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import requests
from sentiment_analysis import analyze_sentiment
from dotenv import load_dotenv
import os
import ollama
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from googletrans import Translator
import time
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")  

# Discord Bot Configuration
intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="/", intents=intents)
synced = False  # Prevent multiple syncs

# Store chat history per user
conversation_history = {}
# Translate using googletrans
translator = Translator()

# Function to preprocess text using NLTK
def preprocess_text(text: str) -> str:
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [token for token in tokens if token not in string.punctuation]
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    return " ".join(tokens)

# Function to save chat data to DynamoDB via AWS Lambda
async def save_to_dynamodb(user_id, message, response):
    payload = {"user_id": str(user_id), "message": message, "response": response}
    try:
        requests.post(API_GATEWAY_URL, json=payload)  
    except requests.RequestException as e:
        print(f"Error saving to DynamoDB: {e}")
@bot.event
async def on_ready():
    global synced
    if not synced:
        await bot.tree.sync()
        synced = True
    print(f"Bot is online as {bot.user.name}")

@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, I'm a bot!")

@bot.tree.command(name="ask", description="Ask the bot anything")
async def ask(interaction: discord.Interaction, message: str):
    try:
        
        await interaction.response.defer(thinking=True)
        user_id = str(interaction.user.id)

        if user_id not in conversation_history:
            conversation_history[user_id] = []

        start_time = time.time()

        # Detect input language 
        detected_lang = (await translator.detect(message)).lang or "en"

        # Translate message to English for processing
        if detected_lang != "en":
        # Translate the message to English only if it's not already in English
            message_in_english = (await translator.translate(message, src=detected_lang, dest="en")).text
        else:
        # If the message is already in English, use it directly
            message_in_english = message

        # Preprocess the message
        preprocessed_message = preprocess_text(message_in_english)
        logging.info(f"Original: '{message}', Detected Lang: {detected_lang}, Translated: '{preprocessed_message}'")

        sentiment = analyze_sentiment(message)

        print(f"Sentiment of message '{message}': {sentiment}")

        conversation_history[user_id].append({'role': 'user', 'content': message_in_english})
        conversation_history[user_id] = conversation_history[user_id][-3:]  # Keep last 10 messages

        async with interaction.channel.typing():
            ollama_response = ollama.chat(
                model='llama2',
                messages=[
                    {'role': 'system', 'content': 'You are an AI assistant that provides helpful and friendly responses.'}
                ] + conversation_history[user_id]
            )
            response_in_english = ollama_response.get('message', {}).get('content', 'I could not generate a response.')

        # Adjust response based on sentiment
        if sentiment == "negative":
            response_in_english += "\n\nI'm here to help! Let me know if I can assist you in any way."

        # Translate 
        response_translated = (await translator.translate(response_in_english, src="en", dest=detected_lang)).text

        response_time = time.time() - start_time  # End timer
        
        # Send response in chunks
        for chunk in [response_translated[i:i+2000] for i in range(0, len(response_translated), 2000)]:
            await interaction.followup.send(chunk, ephemeral=True)
        print(f"⏱ **Response Time:** {response_time:.2f} seconds")
        
        # Store bot's response in history
        conversation_history[user_id].append({'role': 'assistant', 'content': response_in_english})
        
        # Save conversation to DynamoDB
        # if save_to_dynamodb(user_id=user_id, message=message, response=response_translated):
        #     print("Conversation saved successfully.")
        # else:
        #     print("Failed to save conversation.")

        # ✅ Save to DynamoDB in background
        asyncio.create_task(save_to_dynamodb(user_id=user_id, message=message, response=response_translated))

    except Exception as e:
        print(f"Error in ask command: {e}")
        if interaction.response.is_done():
            await interaction.followup.send("⚠️ An error occurred while processing your request.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ An error occurred while processing your request.", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Bot token not found. Please check your .env file.")
