import discord
from discord.ext import commands
from discord import app_commands
import requests
from sentiment_analysis import analyze_sentiment
from dotenv import load_dotenv
import os
import ollama
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")  # Store your API Gateway URL in the .env file

# Discord Bot Configuration
intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="/", intents=intents)
synced = False  # Prevent multiple syncs

# Store chat history per user
conversation_history = {}

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
    global synced
    if not synced:
        await bot.tree.sync()
        synced = True
    print(f"Bot is online as {bot.user.name}")

    
# Define the slash command
@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, I'm a bot!")
    
    
@bot.tree.command(name="ask", description="Ask the bot anything")
async def ask(interaction: discord.Interaction, message: str):
    try:
        # Prevent timeout for the command from expiring
        await interaction.response.defer(thinking=True)
        
        user_id = str(interaction.user.id)

        # Retrieve previous messages or start new conversation
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        sentiment = analyze_sentiment(message)
        
        print(f"Sentiment of message '{message}': {sentiment}")
        
        # Add user's message to history
        conversation_history[user_id].append({'role': 'user', 'content': message})

        # Keep only the last 10 messages for better memory allocation
        conversation_history[user_id] = conversation_history[user_id][-10:]

        async with interaction.channel.typing():
            ollama_response = ollama.chat(
                model='llama2',
                messages=[
                    {'role': 'system', 'content': 'You are an AI assistant that provides informative and engaging answers while maintaining a friendly tone.'}
                ] + conversation_history[user_id]
            )
            response = ollama_response.get('message', {}).get('content', 'I could not generate a response.')

        # Adjust response based on sentiment
        if sentiment == "negative":
            response += "\n\nI'm here to help! Let me know if I can assist you in any way."
            
        # Split the response into chunks of 2000 characters to not overcome the limit of Discord
        for chunk in [response[i:i+2000] for i in range(0, len(response), 2000)]:
            await interaction.followup.send(chunk, ephemeral=True)

        # Store bot's response in history
        conversation_history[user_id].append({'role': 'assistant', 'content': response})

        # Save the conversation to DynamoDB via AWS Lambda
        if save_to_dynamodb(user_id=user_id, message=message, response=response):
            print("Conversation saved successfully.")
        else:
            print("Failed to save conversation.")

    except Exception as e:
        print(f"Error in ask command: {e}")
        await interaction.response.send_message("⚠️ An error occurred while processing your request.")


# Run the bot
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Bot token not found. Please check your .env file.")
