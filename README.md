# ChatGPT and Gemini Chatbots

This repository contains two chatbot implementations: ChatGPT and Gemini. Both chatbots are designed to engage in conversations on IOT-related topics. Below is a brief overview of each chatbot and how to use them:

## ChatGPT
ChatGPT is a chatbot powered by OpenAI's GPT-4 model. It is designed to discuss topics related to the Internet of Things (IoT). The chatbot interface allows users to input text messages or upload images for conversation. ChatGPT provides concise and meaningful responses to user queries or statements. Additionally, it has the capability to send SMS notifications to contacts.

## Gemini
Gemini is another chatbot implementation utilizing Vertex AI's Generative Models. Like ChatGPT, Gemini engages in conversations based on a given prompt. It is specifically trained to recognize images and provide relevant responses. Users can interact with Gemini by typing messages or uploading images. Similar to ChatGPT, Gemini also supports sending SMS notifications to contacts.

## Project Tutorial Recommendation System with MongoDB Setup

This project consists of two Python scripts, `chatgptRecommend.py` and `geminiRecommend.py`, implementing a chat recommendation system using different AI models. The `chatgptRecommend.py` script utilizes OpenAI's GPT-4 model, while `geminiRecommend.py` employs the Gemini generative model by Vertex AI. The system allows users to interact with a chatbot, which provides recommendations related to Internet of Things (IoT) based on the conversation.

## Features

- **Multi-Model Chatbot**: Users can interact with the chatbot through text input or by uploading images. The chatbot generates responses based on the input using either the GPT-4 or Gemini model.
- **Recommendation System**: The chatbot can provide recommendations for IoT-related topics, including tutorials and project links, based on the conversation context.
- **SMS Integration**: Users can choose to send the chatbot's responses as SMS messages to contacts stored in a VCF file.
- **Like/Dislike Feedback**: Users can provide feedback on the chatbot's responses by liking or disliking them.

## Setup Instructions

1. **Install Dependencies**: Install the required Python packages listed in `requirements.txt`.
2. Ensure you have the necessary dependencies installed to run the chatbots:
- Gradio
- Requests
- Vobject
- Twilio (for SMS functionality)
- Vertex AI (for Gemini)
3. You can use pip to install them:

    ```
    pip install -r requirements.txt
    ```

4. **MongoDB Setup**:
   
   - **Install MongoDB**: Follow the official MongoDB installation guide for your operating system: [MongoDB Installation Guide](https://docs.mongodb.com/manual/installation/)
   - **Start MongoDB Service**: Start the MongoDB service on your local machine.
   - **Create Database and Collection**: Run the following commands in the MongoDB shell to create a database named `IOT` and a collection named `tutorials`:

    ```shell
    > use IOT
    switched to db IOT
    > db.createCollection("tutorials")
    ```

5. **API Keys and Credentials**:
   
   - Obtain API keys for OpenAI and Vertex AI and replace the placeholders in the scripts (`api_key` in `chatgptRecommend.py`, `GOOGLE_APPLICATION_CREDENTIALS` in `geminiRecommend.py`).
   - Provide Twilio credentials (`account_sid`, `auth_token`, `twilio_number`) for sending SMS messages in both scripts.

Make sure to set all the required environment variables for each chatbot to function correctly. These variables include:
- `OPENAI_KEY`: OpenAI API key (for ChatGPT)
- `TWILIO_ACCOUNT_SID`: Twilio account SID (for SMS functionality)
- `TWILIO_AUTH_TOKEN`: Twilio authentication token (for SMS functionality)
- `TWILIO_NUMBER`: Twilio phone number (for SMS functionality)
- `GAC_FILE_PATH`: Google Application Credentials file path (for Gemini)
- `PROJECT_ID`: Google Cloud project ID (for Gemini)
- `LOCATION`: Google Cloud location (for Gemini)
- `VCF_FILE_PATH`: Path to the VCF file containing contacts (for both chatbots)

## Usage

- Run either `chatgptRecommend.py` or `geminiRecommend.py` to start the chat recommendation system.
- Interact with the chatbot by entering text messages or uploading images.
- Explore the capabilities of each chatbot and engage in meaningful conversations.
- Optionally, click the "Send as SMS" button to send the chatbot's response as an SMS message to the contacts in the VCF file.

## Notes

- Ensure that MongoDB is running and accessible before running the scripts.
- Adjust environment variables and file paths according to your system configuration.
- This README assumes basic familiarity with Python, MongoDB, and API usage.

By following these setup instructions, you should be able to deploy and use the chat recommendation system successfully.

