import discord
from discord.ext import commands
import requests
from intent_recognition import load_intents, predict, get_response_for_intent, load_trained_model
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

# Load intents and train model
custom_intents = load_intents("intents.json")
model, tokenizer = load_trained_model("bert_intent_classifier.pth")

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

# @bot.command(name="ask")
# async def ask(ctx, *, message):
#     try:
#         # First, classify the user's message based on predefined intents
#         predicted_label, confidence = predict(model, tokenizer, message)
#         label_to_intent = {idx: intent["intent"] for idx, intent in enumerate(custom_intents["intents"])}
#         predicted_intent = label_to_intent[predicted_label]
        
#         # Try to get a response from the predefined intents
#         # response = get_response_for_intent(custom_intents, predicted_intent)
        
#          # Only use intent response if confidence is above 0.6
#         if confidence > 0.3:
#             response = get_response_for_intent(custom_intents, predicted_intent)
#         else:
#             response = None
            
#         if response is None:
#             # If no predefined response exists, fall back to Ollama
#             ollama_response = ollama.chat(
#                 model='llama2',
#                 messages=[
#                     {'role': 'system', 'content': 'You are a helpful bot assistant who provides concise answers.'},
#                     {'role': 'user', 'content': message}
#                 ]
#             )
#             response = ollama_response.get('message', {}).get('content', 'I could not generate a response.')
            
#             # Log that the response is from Ollama
#             logging.info(f"Ollama response: {response}")
#         else:
#             # Log that the response is from intent recognition
#             logging.info(f"Intent recognition response: {response}")    

#         # Send the response to the user
#         await ctx.send(response)

#         # Save the conversation to DynamoDB via AWS Lambda
#         if save_to_dynamodb(user_id=ctx.author.id, message=message, response=response):
#             print("Conversation saved successfully.")
#         else:
#             print("Failed to save conversation.")

#     except Exception as e:
#         print(f"Error in ask command: {e}")
#         await ctx.send("An error occurred while processing your request.")
@bot.command(name="ask")
async def ask(ctx, *, message):
    try:
        # First, classify the user's message based on predefined intents
        predicted_label, confidence = predict(model, tokenizer, message)
        label_to_intent = {idx: intent["intent"] for idx, intent in enumerate(custom_intents["intents"])}
        predicted_intent = label_to_intent[predicted_label]
        
        print(f"Confidence: {confidence}, Predicted Intent: {predicted_intent}")

        # Use intent-based responses exclusively
        if confidence < 0.3:
            response = "I'm not confident in understanding your request. Could you clarify?"
        else:
            response = get_response_for_intent(custom_intents, predicted_intent)

        # Send the response to the user
        await ctx.send(response)

        # Save the conversation to DynamoDB via AWS Lambda
        if save_to_dynamodb(user_id=ctx.author.id, message=message, response=response):
            print("Conversation saved successfully.")
        else:
            print("Failed to save conversation.")

    except Exception as e:
        print(f"Error in ask command: {e}")
        await ctx.send("An error occurred while processing your request.")


# Run the bot
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Bot token not found. Please check your .env file.")
