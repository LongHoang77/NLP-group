import discord
from discord.ext import commands
import requests
from intent_recognition import load_intents, train_intent_classifier, classify_intent
from sentiment_analysis import analyze_sentiment
from dotenv import load_dotenv
import os
import ollama

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")  # Store your API Gateway URL in the .env file

# Load intents and train model
custom_intents = load_intents("intents.json")
model, vectorizer = train_intent_classifier(custom_intents)

# Discord Bot Configuration
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="/", intents=intents)


# Function to call AWS Lambda for saving data to DynamoDB
def save_to_dynamodb(user_id, message, response):
    payload = {
        "user_id": str(user_id),
        "message": message,
        "response": response
    }
    try:
        response = requests.post(API_GATEWAY_URL, json=payload)
        if response.status_code == 200:
            print("Data saved to DynamoDB successfully.")
            return True
        else:
            print(f"Failed to save data. Status code: {response.status_code}, Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"Error connecting to API Gateway: {e}")
        return False


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user.name}")


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hello, I'm a bot!")


@bot.command(name="ask")
async def ask(ctx, *, message):
    try:
        # Call Ollama API for a response
        response = ollama.chat(
            model='llama2',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful bot assistant who provides concise answers to questions in no more than 1000 words.',
                },
                {
                    'role': 'user',
                    'content': message,
                }
            ]
        )
        bot_response = response.get('message', {}).get('content', 'I could not generate a response.')
        print(bot_response)
        await ctx.send(bot_response)

    except Exception as e:
        print(f"Error in ask command: {e}")
        await ctx.send("An error occurred while processing your request.")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_message = message.content.strip()

    try:
        # Generate response using Ollama
        ollama_response = ollama.chat(
            model='llama2',
            messages=[
                {'role': 'system', 'content': 'You are a helpful bot assistant who provides concise answers.'},
                {'role': 'user', 'content': user_message}
            ]
        )
        bot_response = ollama_response.get('message', {}).get('content', 'I could not generate a response.')
        await message.channel.send(bot_response)

        # Save the conversation to DynamoDB via AWS Lambda
        if save_to_dynamodb(user_id=message.author.id, message=user_message, response=bot_response):
            print("Conversation saved successfully.")
        else:
            print("Failed to save conversation.")

    except Exception as e:
        print(f"Error handling message: {e}")
        await message.channel.send("An error occurred while processing your message.")

    # Process commands after on_message
    await bot.process_commands(message)


# Run the bot
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Bot token not found. Please check your .env file.")
