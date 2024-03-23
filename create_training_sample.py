import requests
import os
import sys
import copy
import json
from dotenv import load_dotenv

def diarize_approach(audio_file_path):
    print("In main")
    print('audio_file_path name: ', audio_file_path)
    load_dotenv()

    # Call Deepgram API with diarize true
    headers = {
        'Authorization': os.getenv('AUTH_TOKEN'),
        'Content-Type': 'audio/mp3'
    }
    url = 'https://api.deepgram.com/v1/listen?punctuate=true&diarize=true&model=base-phonecall'

    with open(audio_file_path, 'rb') as f:
        res = requests.post(url, headers=headers, data=f)

    transcription = res.json()

    utterance = ''
    lastSpeaker = 0
    messages = []
    for word in transcription['results']['channels'][0]['alternatives'][0]['words']:
        if word['speaker'] == lastSpeaker:
            utterance = utterance + ' ' + word['punctuated_word']
        else:
            # How do we know which speaker to clone? I'm not even sure I know that
            role = 'user' if lastSpeaker == 0 else 'assistant'
            messages.append({
                'role': role,  
                'content': copy.copy(utterance)
            })

            # Wipe utterance
            lastSpeaker = word['speaker']
            utterance = word['punctuated_word']

    role = 'user' if lastSpeaker == 0 else 'assistant'
    messages.append({
                'role': role,
                'content': utterance
            })

    data = { 'messages': messages }
    # Convert it to JSONL and write it to a file
    with open('diarize_output.jsonl', 'w') as f:
        f.write(json.dumps(data) + '\n')



def utterance_approach(audio_file_path):
    load_dotenv()

    # Call Deepgram API with diarize true
    headers = {
        'Authorization': os.getenv('AUTH_TOKEN'),
        'Content-Type': 'audio/mp3'
    }
    url = 'https://api.deepgram.com/v1/listen?punctuate=true&utterances=true&diarize=true&model=base-phonecall'

    with open(audio_file_path, 'rb') as f:
        res = requests.post(url, headers=headers, data=f)

    transcription = res.json()

    messages = []
    for utterance in transcription['results']['utterances']:
        messages.append({
            'role': 'user' if utterance['speaker'] == 0 else 'assistant',
            'content': utterance['transcript']
        })
    
    data = { 'messages': messages }
    with open('utterances_output.jsonl', 'w') as f:
        f.write(json.dumps(data) + '\n')



if __name__ == "__main__":
    file_path = sys.argv[1]
    diarize_approach(file_path)
    # utterance_approach(file_path)