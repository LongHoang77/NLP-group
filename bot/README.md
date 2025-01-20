# TOPIC: Building a chatbot on chat apps on Discord with Ollama

## Overview

This project is a **Discord Bot** that uses Natural Language Processing (NLP) techniques to interact with users, recognize intents, perform sentiment analysis, and respond intelligently. The bot integrates multiple components including a custom-trained intent recognition model, an AWS Lambda function for saving data to DynamoDB, and Ollama for AI-based conversational responses.

---

## Features

- **Custom Intent Recognition:** Classify user intents using a trained model.
- **Sentiment Analysis:** Analyze the sentiment of user messages.
- **Ollama Integration:** Leverage advanced language models for natural conversation.
- **AWS Lambda Integration:** Store user interactions securely in DynamoDB.
- **Dynamic Responses:** Provide concise and intelligent answers to user queries.

---

## Requirements

### Software and Libraries

- Python 3.8+
- `discord.py` for Discord bot interactions
- `requests` for API communication
- `dotenv` for environment variable management
- `ollama` for interfacing with the language model
- Custom Python scripts:
  - `intent_recognition.py`: For intent classification
  - `sentiment_analysis.py`: For sentiment analysis

### Data and Models

- `intents.json`: File containing training data for custom intents.
- A pre-trained model for intent recognition, trained using the script provided in the repository.

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

### 4. Train Intent Classifier

Train the intent classification model using the provided script:

```bash
python intent_recognition.py
```

This will create a trained model and vectorizer stored locally.

### 5. Run the Bot

Start the bot by running:

```bash
python bot.py
```

---

## Using the Bot

### Commands

- **`/hello`:** Responds with a simple greeting message.
- **`/ask <message>`:** Sends a query to the Ollama model and returns the response.

### Customization

You can modify the bot's behavior by editing the intent data in `intents.json` and retraining the model.

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

---

## Future Enhancements

- Add multilingual support.
- Implement dynamic intent learning from user feedback.
- Expand functionality with additional NLP models or APIs.
