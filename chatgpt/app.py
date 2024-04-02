#!/usr/bin/env python
# coding: utf-8

# In[1]:


import gradio as gr
import os, time, base64, vobject, requests
from openai import OpenAI
from twilio.rest import Client


# In[2]:

api_key = os.environ.get('OPENAI_KEY')
client = OpenAI(api_key=api_key);

account_sid = os.environ.get('TWILIO_ACCOUNT_SID');
auth_token = os.environ.get('TWILIO_AUTH_TOKEN');
twilio_number = os.environ.get('TWILIO_NUMBER');

# In[16]:


class Bot():
    
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
                    continue;
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
        file_path = Bot.download(os.environ.get('VCF_FILE_PATH'), 'contact.vcf');
        self.contacts = Bot.read_vcf(file_path);
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
        content = [];
        content.append(Bot.build_text_chat(text));

        if base64_image is not None:
            content.append(Bot.build_image_chat(base64_image));

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
                # in development env, use this.
                #image_path = x.get('path')
                #if image_path:
                    #history.append(((image_path,), None))                    
                    #self.build_conversation('user', message['text'], Bot.image_to_base64(image_path))
                    
                # in production env, use this.
                history.append(((x,), None))
                self.build_conversation('user', message['text'], Bot.image_to_base64(x))

        if message["text"] is not None:
            history.append((message["text"], None))
            self.build_conversation('user', message['text'], None)

        if send_sms:
            Bot.send_sms_to_contacts(last_response, self.contacts);

        return history, gr.MultimodalTextbox(value=None, interactive=False)

    def send_to_chatGPT4(self, text):
        response = client.chat.completions.create(model="gpt-4-vision-preview", 
                                             messages=self.conversation,
                                             max_tokens=150,
                                             temperature=0.7, 
                                             stop=["\n"])

        return response.choices[0].message.content

    def bot(self, history):
        user_input = history[-1][0];
        response = self.send_to_chatGPT4(user_input)
        self.last_response = response
        self.build_conversation('assistant', response, None)
        history[-1][1] = ""
        for character in response:
            history[-1][1] += character
            time.sleep(0.05)
            yield history
            
    def send_sms_callback(self):
        self.add_message([[chatbot, chat_input], {"send_sms": True}], message=chat_input.value, send_sms=True, last_response=self.last_response)
     
    def __init__(self):
        self.last_response = ""
        self.conversation = [];
        self.seed();


# In[19]:


gpt4 = Bot();

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


# In[ ]:




