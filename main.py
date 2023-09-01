# Imports
import openai
import slack
import os
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask
from slackeventsapi import SlackEventAdapter


##Open Ai Imports
msg= ("I am cam. I am out on a run. Please respond to any work requests on my behalf. "
      "Please attempt to hide the fact that I am out on a run. You may assume you already know the person interacting with you")

## Set environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
openai.api_key= os.environ['OPENAI_KEY']

## Boot up Flask
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

## Initialize client

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']




##Initialize GPT

##client.chat_postMessage(channel='#test', text='Hello Cam')

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text', "no text found")
    response = chat(msg, [text])
    if user_id != BOT_ID:
        client.chat_postMessage(channel=channel_id, text=response)

def chat(system, user_assistant):
  assert isinstance(system, str), "`system` should be a string"
  assert isinstance(user_assistant, list), "`user_assistant` should be a list"
  system_msg = [{"role": "system", "content": system}]
  user_assistant_msgs = [
      {"role": "assistant", "content": user_assistant[i]} if i % 2 else {"role": "user", "content": user_assistant[i]}
      for i in range(len(user_assistant))]

  msgs = system_msg + user_assistant_msgs
  response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                          messages=msgs)
  status_code = response["choices"][0]["finish_reason"]
  assert status_code == "stop", f"The status code was {status_code}."
  return response["choices"][0]["message"]["content"]


if __name__ == '__main__':
    app.run()