from flask import Flask, jsonify, render_template, request
import sqlite3
import random
import openai
import logging
logging.basicConfig(level=logging.DEBUG)
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Get the API key
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)


def generate_tweet(tool):
    # Generate the text for each tool using the ChatGPT API.
    logging.debug('Generating tweet for tool: %s', tool['Tool'])
    try:
        chat = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": "You are a Twitter copywriter expert in writing Twitter threads."},
                {"role": "user", "content": f"Generate a brief description for an AI tool named {tool['Tool']}, which has the following description: {tool['Short description']}. It costs {tool['Pricing']}. Here is the link: {tool['Url without ref']}"},
            ]
        )
    except Exception as e:
        logging.error('Failed to generate tweet: %s', e)
        raise
    logging.debug('Generated tweet: %s', chat['choices'][0]['message']['content'])
    return chat['choices'][0]['message']['content']


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generate():
    # Connect to the SQLite database
    conn = sqlite3.connect('MyDatabase.db')
    c = conn.cursor()

    # Fetch tools from the database based on the selected category
    category = request.args.get('category', '')
    c.execute("SELECT * FROM Tools WHERE `Category 2` = ?", (category,))
    tools = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]

    # Randomly select 7 tools
    selected_tools = random.sample(tools, min(7, len(tools)))

    # Generate the tweets
    tweets = []
    tweets.append(f"Here are {len(selected_tools)} cool AI tools in the {category} category you should check out today:")
    for tool in selected_tools:
        tweet = generate_tweet(tool)
        tweets.append(tweet)

    # Close the database connection
    conn.close()

    # Return the tweets
    return jsonify(tweets)


if __name__ == '__main__':
    app.run(debug=True)
