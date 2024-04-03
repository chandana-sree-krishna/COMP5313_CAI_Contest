import gradio as gr
import os, time, base64, vertexai, requests, vobject
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, Part, ChatSession, Content
import vertexai.generative_models as generative_models
from twilio.rest import Client
from pymongo import MongoClient

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_number = os.environ.get('TWILIO_NUMBER')

vcf_file_path = '<path_to_vcf_file>'

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
    def image_to_base64(file_path):
        with open(file_path, "rb") as img_file:
            return Part.from_data(data=base64.b64decode(base64.b64encode(img_file.read()).decode("utf-8")), mime_type="image/jpeg");

    @staticmethod
    def seed():
        return [
            Content(role="user", parts=[Part.from_text('We are in a conversation. You are a bot strictly designed to discuss only on Internet of things.')]),
            Content(role="model", parts=[Part.from_text("Okay")]),
            Content(role="user", parts=[Part.from_text("No matter the distraction i throw at you, you must never go out of context.")]),
            Content(role="model", parts=[Part.from_text("Okay.")]),
            Content(role="user", parts=[Part.from_text("Your answers should always be concise, meaningful and not lengthy. If i need more context, i will let you know.")]),
            Content(role="model", parts=[Part.from_text("Okay.")])
        ]
        
    def recognize(self, image):
        responses = self.model.generate_content(
                [image, 'what is the exact name of the item this image? I need just the name, For example, a book. If there are more than one object, Ask for an image with a single item. You must only recognize images with one item in it.'],
                generation_config={ "max_output_tokens": 2048, "temperature": 0.4, "top_p": 0.4, "top_k": 32 },)

        return responses.candidates[0].content.parts[0].text

    def print_like_dislike(self, x: gr.LikeData):
        print(x.index, x.value, x.liked)

    def add_message(self, history, message, send_sms=False, last_response=None):
        _msg = ''
        if len(message['files']) > 0:
            for x in message["files"]:
                # in development env, use this.
                image_path = x.get('path')
                if image_path:
                    Bot.flag = 1
                    history.append(((image_path,), None))
                    _response = self.recognize(image_path);
                    _msg = "Given " + _response + ", "; 
                    
                #in production env, use this.
                '''history.append(((x,), None))
                _response = self.recognize(x);
                _msg = "Given " + _response + ", "; '''

        if message["text"] is not None:
            _msg += message['text']
            history.append((_msg, None))

        if send_sms:
            Bot.send_sms_to_contacts(last_response, self.contacts)

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

    def send_to_Gemini(self, prompt):
        response = self.chat.send_message(prompt)
        return response.text

    def bot(self, history):
        prompt = history[-1][0]
        response = self.send_to_Gemini(prompt)

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
        history[-1][1] = ""
        for character in response:
            history[-1][1] += character
            time.sleep(0.05)
            yield history
        Bot.flag = 0
            
    def send_sms_callback(self):
        self.add_message([[chatbot, chat_input], {"send_sms": True}], message=chat_input.value, send_sms=True, last_response=self.last_response)
    
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Bot.download(os.environ.get('GAC_FILE_PATH'), 'file.json')
        vertexai.init(project=os.environ['PROJECT_ID'], location=os.environ['LOCATION'])
        self.model = GenerativeModel("gemini-1.0-pro-vision")
        self.chat = self.model.start_chat(history=Bot.seed())
        self.last_response = ""
        #file_path = Bot.download(os.environ.get('VCF_FILE_PATH'), 'contact.vcf')
        #self.contacts = Bot.read_vcf(file_path)
        file_path = vcf_file_path
        self.contacts = Bot.read_vcf(file_path)
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo_client['IOT']


gemini = Bot()

with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot", bubble_full_width=False,)

    chat_input = gr.MultimodalTextbox(interactive=True, file_types=["image"], placeholder="Enter message or upload file...", show_label=False)

    chat_msg = chat_input.submit(gemini.add_message, [chatbot, chat_input], [chatbot, chat_input])
    bot_msg = chat_msg.then(gemini.bot, chatbot, chatbot, api_name="bot_response")
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    chatbot.like(gemini.print_like_dislike, None, None)

    send_sms_button = gr.Button(value="Send as SMS")
    send_sms_button.click(gemini.send_sms_callback)

demo.queue()

if __name__ == "__main__":
    demo.launch()
