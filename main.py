import requests
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Reddit requires a unique User-Agent or it will block requests
HEADERS = {'User-Agent': 'MyAnimeList-Reddit-Clone/1.0'}

def format_timestamp(created_utc):
    return datetime.fromtimestamp(created_utc).strftime('%b %d, %Y')

app.jinja_env.filters['date'] = format_timestamp

def get_reddit_data(url):
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            return None
        return resp.json()
    except:
        return None

@app.route('/')
def home():
    # Defaults to r/all or user selected subreddit
    subreddit = request.args.get('r', 'all')
    sort = request.args.get('sort', 'hot')
    
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit=25"
    data = get_reddit_data(url)
    
    posts = []
    if data:
        for child in data['data']['children']:
            posts.append(child['data'])
            
    return render_template('index.html', posts=posts, subreddit=subreddit, sort=sort)

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('home'))
        
    url = f"https://www.reddit.com/search.json?q={query}&limit=25"
    data = get_reddit_data(url)
    
    posts = []
    if data:
        for child in data['data']['children']:
            posts.append(child['data'])
            
    return render_template('index.html', posts=posts, subreddit="Search Results", sort="relevance")

@app.route('/comments/<path:permalink>')
def comments(permalink):
    # Reddit permalinks usually start with /r/, we need to append .json
    url = f"https://www.reddit.com/{permalink}.json"
    data = get_reddit_data(url)
    
    if not data:
        return "Error loading post"

    post = data[0]['data']['children'][0]['data']
    comments_raw = data[1]['data']['children']
    
    return render_template('comments.html', post=post, comments=comments_raw)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)