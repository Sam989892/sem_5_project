import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from textblob import TextBlob
from io import BytesIO, StringIO
import base64
from flask_socketio import SocketIO, emit
import json
import os

# Add these at the top of your file

app = Flask(__name__)
socketio = SocketIO(app)

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        category = 'Positive'
    elif sentiment < 0:
        category = 'Negative'
    else:
        category = 'Neutral'
    strength = abs(sentiment)
    return category, strength

def generate_graph(results):
    sentiments = [result['sentiment'] for result in results]
    sentiment_counts = {'Positive': sentiments.count('Positive'),
                        'Negative': sentiments.count('Negative'),
                        'Neutral': sentiments.count('Neutral')}
    
    plt.figure(figsize=(8, 6))
    plt.bar(sentiment_counts.keys(), sentiment_counts.values())
    plt.title('Sentiment Analysis Results')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return f'data:image/png;base64,{graph_url}'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        results = []
        
        # Handle CSV file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                try:
                    file_content = file.read().decode('utf-8')
                    csv_data = StringIO(file_content)
                    df = pd.read_csv(csv_data)
                    
                    if df.empty:
                        return "The uploaded CSV file is empty."
                    
                    # Try to identify the text column
                    text_column = None
                    possible_column_names = ['review_text', 'text', 'comment', 'description', 'content']
                    for col in df.columns:
                        if col.lower() in possible_column_names:
                            text_column = col
                            break
                    
                    # If no specific text column is found, use the column with the longest average string length
                    if text_column is None:
                        text_column = df.astype(str).apply(lambda x: x.str.len().mean()).idxmax()
                    
                    total_rows = len(df)
                    for index, row in df.iterrows():
                        text = row[text_column]
                        sentiment, strength = analyze_sentiment(str(text))
                        results.append({'text': str(text), 'sentiment': sentiment, 'strength': strength})
                        progress = (index + 1) / total_rows * 100
                        socketio.emit('progress_update', {'progress': progress})
                    
                    graph_url = generate_graph(results)
                    return render_template('results.html', results=results, graph_url=graph_url)
                except Exception as e:
                    return f"An error occurred while processing the CSV file: {str(e)}"
        
        # Handle text input
        text_input = request.form.get('text_input')
        if text_input:
            lines = text_input.split('\n')
            for line in lines:
                if line.strip():  # Skip empty lines
                    sentiment, strength = analyze_sentiment(line)
                    results.append({'text': line, 'sentiment': sentiment, 'strength': strength})
            graph_url = generate_graph(results)
            return render_template('results.html', results=results, graph_url=graph_url)

    return render_template('index.html')

@app.route('/save_result', methods=['POST'])
def save_result():
    data = request.json
    username = data['username']
    result = data['result']
    
    # Create a directory for user data if it doesn't exist
    if not os.path.exists('user_data'):
        os.makedirs('user_data')
    
    # Save the result to a JSON file
    filename = f'user_data/{username}_results.json'
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            user_results = json.load(f)
    else:
        user_results = []
    
    user_results.append(result)
    
    with open(filename, 'w') as f:
        json.dump(user_results, f)
    
    return jsonify({'status': 'success'})

@app.route('/get_results/<username>')
def get_results(username):
    filename = f'user_data/{username}_results.json'
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            user_results = json.load(f)
        return jsonify(user_results)
    else:
        return jsonify([])

@app.route('/my_results')
def my_results():
    return render_template('my_results.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
