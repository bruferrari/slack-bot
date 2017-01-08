# -*- coding: utf-8 -*-
import os
import time
import requests
from slackclient import SlackClient

BOT_ID = os.environ.get("BOT_ID")

AT_BOT = "<@" + BOT_ID + ">"
COMMAND = "news"

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

responses = []

def handle_message(message, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    default_response = "Ahn?? Só me diga o que fazer. Use o comando * "  + COMMAND  + \
            " * delimitado por espaços."
    print(message)
    if message.startswith(COMMAND):
        if 'iot' in message:
            responses.append("Ok, vamos ver o que temos hoje sobre internet das coisas aqui...")
            responses.append("Isso foi o que encontrei de mais recente sobre o assunto que pesquisou:")
        else:
            postMessage('Veremos o que eu acho de relevante na internet sobre o que pesquisou')
        subject = message.split(COMMAND)[1].strip().lower()
        results = news_crawler(subject)
        for r in results:
            responses.append(r)
            
    elif 'quem' in message:
        if 'vc' or 'voce' or 'você' in message:
            responses.append("Sou apenas um bot sabichão...")

    else:
        print responses
        responses.append(default_response)

    for response in responses:
            postMessage(response)
    del responses[:]

def postMessage(message):
    slack_client.api_call("chat.postMessage", channel=channel,
                               text=message, as_user=True)

def news_crawler(subject):
    base_url = 'https://webhose.io'
    payload = {'q': subject + ' language:(english) performance_score:>3'}
    request_url = (base_url + '/search?token=41941689-d978-4c61-9ab2-e3fef95933a6&format=json').replace('25', '%')
    result = []

    raw_request = requests.get(request_url, params=payload)

    if raw_request.status_code == 200:
        parsed_result = raw_request.json()
        if parsed_result['totalResults'] > 0 and parsed_result['totalResults'] < 10:
            for r in parsed_result['posts']:
                print r['thread']['title']
                result.append(r['thread']['title'] + ' => (' + r['thread']['url'] + ')')
            
            return result

        elif parsed_result['totalResults'] > 10:
            for x in range(10):
                print parsed_result['posts'][x]['title']
                result.append(parsed_result['posts'][x]['title'] + ' => (' + parsed_result['posts'][x]['url'] + ')')
            return result
                
        else:
            print 'None results to show'
    else:
        print 'A problem has been ocurred when trying to access API, status_code=' + \
                parsed_result.status_code
        

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                        output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print("Nxer connected and running!")
    while True:
        message, channel = parse_slack_output(slack_client.rtm_read())
        if message and channel:
            handle_message(message, channel)
        time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID.")
