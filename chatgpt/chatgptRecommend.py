import gradio as gr
import os
import time
import base64
import vobject
import requests
import openai
from twilio.rest import Client
from pymongo import MongoClient

account_sid = '<account_sid_of_twillio>'
auth_token = '<auth_token_of_twillio>'
twilio_number = '<twillio_number>'

vcf_file_path = '<path_to_vcf_file>'

api_key = "<chatgpt_api_key>"
client = openai.OpenAI(api_key=api_key)

class Bot():
    flag = 0  # Declare flag as a class variable

    @staticmethod
    def download(url, filename):
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename

    @staticmethod
    def read_vcf(file_path):
        contacts = []
        with open(file_path, 'r') as f:
            vcard_str = f.read()
            for vcard in vobject.readComponents(vcard_str):
                if 'fn' not in vcard.contents:
                    continue
                name = vcard.fn.value
                if 'tel' in vcard.contents:
                    phone = vcard.tel.value
                else:
                    phone = None
                if 'email' in vcard.contents:
                    email = vcard.email.value
                else:
                    email = None
                contacts.append((name, phone, email))
        return contacts

    def seed(self):
        file_path = vcf_file_path
        self.contacts = Bot.read_vcf(file_path)
        self.build_conversation('user', 'You are designed to discuss only topics relating Internet of Things. You should not be distracted from the context of this conversation.', None)
    
    @staticmethod
    def send_sms(recipient_number, message):
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=message, from_=twilio_number, to=recipient_number)
        gr.Info(f'Message sent to {recipient_number}')

    @staticmethod
    def send_sms_to_contacts(message, contacts):
        for contact in contacts:
            name, phone, email = contact
            if phone:
                Bot.send_sms(phone, message)

    @staticmethod
    def build_text_chat(text):
        return { "type" : "text", "text" : text }

    @staticmethod
    def build_image_chat(base64_image):
        return { "type": "image_url", "image_url": { "url" : f"data:image/jpeg;base64,{base64_image}" }}

    def build_conversation(self, role, text, base64_image):
        content = []
        content.append(Bot.build_text_chat(text))
        if base64_image is not None:
            Bot.flag = 1  # Set flag to 1 if an image is received
            content.append(Bot.build_image_chat(base64_image))

        data = { "role": role, "content": content }
        self.conversation.append(data)

    @staticmethod
    def image_to_base64(file_path):
        with open(file_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode("utf-8")
        return base64_image

    def print_like_dislike(self, x: gr.LikeData):
        print(x.index, x.value, x.liked)

    def add_message(self, history, message, send_sms=False, last_response=None):
        if len(message['files']) > 0:
            for x in message["files"]:
                image_path = x.get('path')
                if image_path:
                    history.append(((image_path,), None))                    
                    self.build_conversation('user', message['text'], Bot.image_to_base64(image_path))

        if message["text"] is not None:
            history.append((message["text"], None))
            self.build_conversation('user', message['text'], None)

        if send_sms:
            Bot.send_sms_to_contacts(last_response, self.contacts);

        return history, gr.MultimodalTextbox(value=None, interactive=False)

    def get_iot_device_names(self):
        collection = self.db['tutorials']
        device_names = []
        for doc in collection.find({}, {'_id': 0, 'Tutorials': 1}):
            tutorials = doc.get('Tutorials', [])
            for tutorial in tutorials:
                iot_device = tutorial.get('IOT_Device', {})
                device_name = iot_device.get('Name')
                if device_name:
                    device_names.append(device_name)
        return device_names


    def get_tutorial_links(self, matched_device_pairs):
        collection = self.db['tutorials']
        tutorial_links = []
        for response, device_name in matched_device_pairs:
            tutorial = collection.find_one({'Tutorials.IOT_Device.Name': device_name}, {'_id': 0, 'Tutorials.$': 1})
            if tutorial and 'Tutorials' in tutorial:
                tutorial_links.append((device_name, tutorial['Tutorials'][0]['IOT_Device']['URL']))
        if tutorial_links:
            return tutorial_links
        else:
            return None

    def send_to_chatGPT4(self, text):
        response = client.chat.completions.create(model="gpt-4-vision-preview", 
                                             messages=self.conversation,
                                             max_tokens=150,
                                             temperature=0.7)

        return response.choices[0].message.content

    def bot(self, history):
        user_input = history[-1][0]
        response = self.send_to_chatGPT4(user_input)

        if Bot.flag == 1:  
            iot_device_names = self.get_iot_device_names()
            response_contains_iot_device = any(device_name in response for device_name in iot_device_names)
            matched_device_pairs = [(response, device_name) for response in [response] for device_name in iot_device_names if device_name in response]

            if response_contains_iot_device:
                tutorial_links = self.get_tutorial_links(matched_device_pairs)
                if tutorial_links:
                    for device_name, tutorial_url in tutorial_links:
                        tutorial_response = f"\n\nRecommendation: Here, you can find few project tutorials based on {device_name}: {tutorial_url}\n"
                    response += tutorial_response

        self.last_response = response
        self.build_conversation('assistant', response, None)
        history[-1][1] = ""
        for character in response:
            history[-1][1] += character
            time.sleep(0.05)
            yield history
        Bot.flag = 0

    def send_sms_callback(self):
        self.add_message([[chatbot, chat_input], {"send_sms": True}], message=chat_input.value, send_sms=True, last_response=self.last_response)
     
    def __init__(self):
        self.last_response = ""
        self.conversation = []
        self.seed()
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo_client['IOT']

gpt4 = Bot()

with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot", bubble_full_width=False,)

    chat_input = gr.MultimodalTextbox(interactive=True, file_types=["image"], placeholder="Enter message or upload file...", show_label=False)

    chat_msg = chat_input.submit(gpt4.add_message, [chatbot, chat_input], [chatbot, chat_input])
    bot_msg = chat_msg.then(gpt4.bot, chatbot, chatbot, api_name="bot_response")
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    chatbot.like(gpt4.print_like_dislike, None, None)

    send_sms_button = gr.Button(value="Send as SMS")
    send_sms_button.click(gpt4.send_sms_callback)

demo.queue()

if __name__ == "__main__":
    demo.launch()