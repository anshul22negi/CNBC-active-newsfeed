from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sources.homepage_scraper import HomepageScraperSource
from typing import List
from fastapi.responses import HTMLResponse

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/news")
def get_news():
    source = HomepageScraperSource()
    news = source.fetch_news()
    # Sort by last_updated (descending), keep only 10 most recent
    def parse_date_safe(date_str):
        from email.utils import parsedate_to_datetime
        try:
            return parsedate_to_datetime(date_str) if date_str else None
        except Exception:
            return None
    news = [a for a in news if a.get('last_updated')]
    news.sort(key=lambda x: parse_date_safe(x.get('last_updated')), reverse=True)
    news = news[:10]
    return news

@app.get("/", response_class=HTMLResponse)
def root_html():
    return """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Recent News</title>
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='0.9em' font-size='90'%3E%F0%9F%93%B0%3C/text%3E%3C/svg%3E"/>
        <style>
            body { font-family: Arial, sans-serif; margin: 2em; background: #f9f9f9; }
            h1 { color: #333; display: flex; align-items: center; gap: 0.5em; }
            .news-list { list-style: none; padding: 0; }
            .news-item { background: #fff; margin-bottom: 1em; padding: 1em; border-radius: 8px; box-shadow: 0 2px 8px #0001; }
            .news-title { font-weight: bold; display: flex; align-items: center; gap: 0.5em; }
            .news-url { color: #1a0dab; text-decoration: none; }
            .news-icon { font-size: 1.2em; margin-right: 0.3em; }
        </style>
    </head>
    <body>
        <h1><span class='news-icon'>📰</span>10 Most Recent News</h1>
        <div id='last-refreshed' style='margin-bottom:1em; color:#666;'></div>
        <ul class='news-list' id='news-list'></ul>
        <script>
            function formatDateTime(date) {
                return date.toLocaleDateString([], {year: 'numeric', month: 'short', day: 'numeric'}) + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
            }
            function updateLastRefreshed() {
                const now = new Date();
                document.getElementById('last-refreshed').textContent = 'Last refreshed: ' + formatDateTime(now);
            }
            async function fetchNews() {
                const res = await fetch('/api/news');
                const news = await res.json();
                const list = document.getElementById('news-list');
                list.innerHTML = '';
                news.forEach(item => {
                    const li = document.createElement('li');
                    li.className = 'news-item';
                    let published = '';
                    if (item.last_updated) {
                        const d = new Date(item.last_updated);
                        published = `<div style='color:#888;font-size:0.95em;'>Published: ${d.toLocaleDateString([], {year: 'numeric', month: 'short', day: 'numeric'})} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}</div>`;
                    }
                    li.innerHTML = `<div class='news-title'><span class='news-icon'>🗞️</span>${item.text || item.title || ''}</div>` +
                        published +
                        (item.user ? `<div>User: <b>${item.user}</b></div>` : '') +
                        `<a class='news-url' href='${item.url}' target='_blank'>Read Article</a>`;
                    list.appendChild(li);
                });
                updateLastRefreshed();
            }
            fetchNews();
            setInterval(fetchNews, 15000);
        </script>
    </body>
    </html>
    """ 
