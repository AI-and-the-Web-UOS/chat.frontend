from flask import Flask, request, render_template, jsonify, redirect, url_for
import requests
import urllib.parse
import datetime

app = Flask(__name__)

HUB_AUTHKEY = '1234567890'
HUB_URL = 'http://localhost:5555'

CHANNELS = None
LAST_CHANNEL_UPDATE = None


def update_channels():
    global CHANNELS, LAST_CHANNEL_UPDATE
    if CHANNELS and LAST_CHANNEL_UPDATE and (datetime.datetime.now() - LAST_CHANNEL_UPDATE).seconds < 60:
        return CHANNELS
    # fetch list of channels from server
    response = requests.get(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY})
    if response.status_code != 200:
        return "Error fetching channels: "+str(response.text), 400
    channels_response = response.json()
    if not 'channels' in channels_response:
        return "No channels in response", 400
    CHANNELS = channels_response['channels']
    LAST_CHANNEL_UPDATE = datetime.datetime.now()
    return CHANNELS


@app.route('/')
def home_page():
    channelId = request.args.get('channelId', default=None, type=str)
    channels = update_channels()
    # Fetch messages for the first channel initially
    if channelId:
        channelId = next((channel['endpoint'] for channel in channels if channel['endpoint'] == channelId), None)
        messages = fetch_messages(channelId)
        return render_template("home.html", channels=channels, messages=messages, initialChannelId=channelId)
    else:
        default_channel = channels[0]['endpoint'] if channels else None
        messages = fetch_messages(default_channel)
        return render_template("home.html", channels=channels, messages=messages, initialChannelId=default_channel)


@app.route('/get_messages/<channel_id>')
def get_messages(channel_id):
    channel_id = urllib.parse.unquote(channel_id)
    messages = fetch_messages(channel_id)
    return jsonify(messages)


@app.route('/post_message', methods=['POST'])
def post_message():
    post_channel = request.form['channel']
    if not post_channel:
        return "No channel specified", 400
    channel = None
    for c in update_channels():
        if c['endpoint'] == urllib.parse.unquote(post_channel):
            channel = c
            break
    if not channel:
        return "Channel not found", 404
    message_content = request.form['content']
    message_sender = request.form['sender']
    message_timestamp = datetime.datetime.now().isoformat()
    response = requests.post(channel['endpoint'],
                             headers={'Authorization': 'authkey ' + channel['authkey']},
                             json={'content': message_content, 'sender': message_sender, 'timestamp': message_timestamp})
    if response.status_code != 200:
        return "Error posting message: "+str(response.text), 400
    return redirect(url_for('home_page', channelId=channel['endpoint']))


def fetch_messages(channel_id):
    if not channel_id:
        return []
    channels = update_channels()
    channel = next((channel for channel in channels if channel['endpoint'] == channel_id), None)
    response = requests.get(channel["endpoint"], headers={'Authorization': 'authkey ' + channel['authkey']})
    if response.status_code != 200:
        return [{"sender": "Error", "content": "Error fetching messages"}]
    return response.json()


# Start development web server
if __name__ == '__main__':
    app.run(port=5005, debug=True)
