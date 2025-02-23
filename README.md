# TOPIC: Building a chatbot on chat apps on Discord with Ollama

## Overview

This project is a **Discord chatbot** that uses **Ollama's Llama2** model to generate responses based on user input. It supports **multilingual translation**, **sentiment analysis**, and **conversation history storage** via **AWS DynamoDB**.

The chatbot is designed to:

- Provide AI-generated responses to user queries.
- Detect and translate messages into English before processing.
- Analyze sentiment in user messages and adjust responses accordingly.
- Maintain recent chat history per user for contextual responses.
- Store conversation logs in **AWS DynamoDB** through an API Gateway.

---

## Features

### AI-Powered Responses

- Uses **Ollama’s Llama2** model to generate meaningful responses.

### Multi-Language Support

- Detects message language and translates it to English for processing.
- Responses are translated back to the original language before sending.

### Sentiment Analysis

- Analyzes whether a message is **positive, neutral, or negative**.
- Adjusts responses to be more supportive if sentiment is negative.

### Chat History

- Stores the last **3 messages** per user to provide contextual responses.

### AWS DynamoDB Storage

- Saves conversations to **AWS DynamoDB** via **API Gateway**.

---

## Requirements

### Software and Libraries

- Python 3.8+
- `discord.py` for Discord bot interactions
- `requests` for API communication
- `dotenv` for environment variable management
- `ollama` for interfacing with the language model
- `googletrans` for google translate
- `nltk` for natural laanguage toolkit
- Custom Python scripts: 
  - `sentiment_analysis.py`: For sentiment analysis

### Cloud Services

- AWS Lambda and API Gateway: Used for saving interaction data to DynamoDB.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <https://github.com/LongHoang77/NLP-group.git>
cd <NLP-group/bot>
```

### 2. Install Dependencies

Use `pip` to install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root and add the following keys:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
API_GATEWAY_URL=your_api_gateway_url
```

### 4. Run the Bot

Start the bot by running:

```bash
python bot.py
```

---

## Using the Bot

### Commands

- **`/hello`:** Responds with a simple greeting message.
- **`/ask <message>`:** The bot generates a response based on the message. 

#### Example Usage

```bash
/ask How does machine learning work?
```

---

## How It Works

### Message Processing Steps
1. **Detect Language**  
   - The bot detects the language of the input message.

2. **Translate to English**  
   - If the message is not in English, it is translated before processing.

3. **Preprocess the Message**  
   - Text is converted to lowercase.
   - Tokenization is applied using `nltk`.
   - Stop words and punctuation are removed.

4. **Analyze Sentiment**  
   - The sentiment of the message is classified as **positive, neutral, or negative**.

5. **Generate a Response**  
   - The bot sends the processed message to **Ollama’s Llama2** model for response generation.

6. **Translate Back**  
   - If the original message was in a different language, the response is translated back.

7. **Send Response**  
   - The bot replies to the user in their original language.

8. **Store Conversation in DynamoDB**  
   - The user’s message and the bot’s response are logged in AWS DynamoDB via API Gateway.

---

## Deployment Instructions

### AWS Lambda and DynamoDB Setup

1. **Create a DynamoDB Table:**
   - Name: `chat_history`
   - Primary Key: `user_id`

2. **Deploy Lambda Function:**
   - Write a Lambda function to receive and save interaction data to DynamoDB.
   - Integrate it with an API Gateway for HTTP requests.

3. **Update `.env`:**
   - Add the API Gateway URL for the Lambda function.

### Hosting Options

- **Local Hosting:** Run the bot locally by executing `bot.py`.

---

## References and Documentation

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Ollama API Documentation](https://ollama.ai/docs)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [AWS DynamoDB](https://docs.aws.amazon.com/dynamodb/)

---

