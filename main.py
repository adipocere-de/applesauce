from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
# False = Try to fetch real data from TikWM
# True = Use fake data (useful if the API is down or blocking us)
USE_MOCK = False 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search_proxy():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    if USE_MOCK:
        return jsonify(get_mock_data(query))

    try:
        # We request data from TikWM (a public TikTok archiver)
        # doing this in Python bypasses CORS errors.
        url = "https://www.tikwm.com/api/feed/search"
        payload = {
            "keywords": query,
            "count": 12,
            "cursor": 0,
            "web": 1,
            "hd": 1
        }
        
        # Send POST request
        resp = requests.post(url, data=payload)
        data = resp.json()

        # Parse the specific response structure of TikWM
        clean_videos = []
        
        if data.get('code') == 0 and 'data' in data and 'videos' in data['data']:
            for v in data['data']['videos']:
                clean_videos.append({
                    'id': v.get('video_id'),
                    'desc': v.get('title', 'No Description'),
                    'cover': v.get('cover'),
                    'play': v.get('play'), # The mp4 link
                    'author': v.get('author', {}).get('nickname', 'Unknown')
                })
            return jsonify({'videos': clean_videos})
        else:
            return jsonify({'error': 'No results found', 'raw': data})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Server error fetching data'}), 500

def get_mock_data(query):
    """Fallback data to test the UI if API fails"""
    return {
        'videos': [
            {
                'desc': f'Test Result for {query}',
                'cover': 'https://placehold.co/300x500/1a1a1a/white?text=Video+1',
                'play': 'https://www.w3schools.com/html/mov_bbb.mp4',
                'author': 'DemoUser'
            },
            {
                'desc': 'Another video',
                'cover': 'https://placehold.co/300x500/2a2a2a/white?text=Video+2',
                'play': 'https://www.w3schools.com/html/mov_bbb.mp4',
                'author': 'TestAccount'
            }
        ]
    }

if __name__ == '__main__':
    # Run on 0.0.0.0 to work on Replit/Codespaces
    app.run(host='0.0.0.0', port=8080, debug=True)