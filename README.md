# ChatGPT and Gemini Chatbots

This repository contains two chatbot implementations: ChatGPT and Gemini. Both chatbots are designed to engage in conversations on IOT-related topics. Below is a brief overview of each chatbot and how to use them:

## ChatGPT
ChatGPT is a chatbot powered by OpenAI's GPT-4 model. It is designed to discuss topics related to the Internet of Things (IoT). The chatbot interface allows users to input text messages or upload images for conversation. ChatGPT provides concise and meaningful responses to user queries or statements. Additionally, it has the capability to send SMS notifications to contacts.

## Gemini
Gemini is another chatbot implementation utilizing Vertex AI's Generative Models. Like ChatGPT, Gemini engages in conversations based on a given prompt. It is specifically trained to recognize images and provide relevant responses. Users can interact with Gemini by typing messages or uploading images. Similar to ChatGPT, Gemini also supports sending SMS notifications to contacts.

## Usage
To use either chatbot, follow these steps:
1. Launch the respective chatbot by executing the provided script.
2. Interact with the chatbot by typing messages or uploading images.
3. Explore the capabilities of each chatbot and engage in meaningful conversations.

## Requirements
Ensure you have the necessary dependencies installed to run the chatbots:
- Gradio
- Requests
- Vobject
- Twilio (for SMS functionality)
- Vertex AI (for Gemini)

## Environment Variables
Make sure to set the required environment variables for each chatbot to function correctly. These variables include:
- `OPENAI_KEY`: OpenAI API key (for ChatGPT)
- `TWILIO_ACCOUNT_SID`: Twilio account SID (for SMS functionality)
- `TWILIO_AUTH_TOKEN`: Twilio authentication token (for SMS functionality)
- `TWILIO_NUMBER`: Twilio phone number (for SMS functionality)
- `GAC_FILE_PATH`: Google Application Credentials file path (for Gemini)
- `PROJECT_ID`: Google Cloud project ID (for Gemini)
- `LOCATION`: Google Cloud location (for Gemini)
- `VCF_FILE_PATH`: Path to the VCF file containing contacts (for both chatbots)
