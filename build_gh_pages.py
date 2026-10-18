import urllib.request
import os
import shutil

BASE_URL = 'http://127.0.0.1:5000'
DIST_DIR = os.path.join(os.path.dirname(__file__), 'dist')

if os.path.exists(DIST_DIR):
    shutil.rmtree(DIST_DIR)
os.makedirs(DIST_DIR, exist_ok=True)

# Copy static assets (css, js, images)
shutil.copytree(os.path.join(os.path.dirname(__file__), 'static'), os.path.join(DIST_DIR, 'static'))

routes = [
    ('/', 'index.html'),
    ('/music', 'music.html'),
    ('/devotional', 'devotional.html'),
    ('/kids', 'kids.html'),
    ('/shorts', 'shorts.html'),
    ('/videos', 'videos.html'),
    ('/artists', 'artists.html'),
    ('/playlists', 'playlists.html'),
    ('/blog', 'blog.html'),
    ('/about', 'about.html'),
    ('/contact', 'contact.html'),
    ('/collaborate', 'collaborate.html'),
    ('/submit-music', 'submit-music.html'),
    ('/search', 'search.html'),
    ('/admin', 'admin.html'),
    ('/privacy-policy', 'privacy-policy.html'),
    ('/terms', 'terms.html'),
    ('/copyright', 'copyright.html'),
    ('/disclaimer', 'disclaimer.html')
]

replacements = [
    ('/static/', '/DIVINENESTWEBSITE/static/'),
    ('href="/music"', 'href="/DIVINENESTWEBSITE/music.html"'),
    ('href="/devotional"', 'href="/DIVINENESTWEBSITE/devotional.html"'),
    ('href="/kids"', 'href="/DIVINENESTWEBSITE/kids.html"'),
    ('href="/shorts"', 'href="/DIVINENESTWEBSITE/shorts.html"'),
    ('href="/videos"', 'href="/DIVINENESTWEBSITE/videos.html"'),
    ('href="/artists"', 'href="/DIVINENESTWEBSITE/artists.html"'),
    ('href="/playlists"', 'href="/DIVINENESTWEBSITE/playlists.html"'),
    ('href="/blog"', 'href="/DIVINENESTWEBSITE/blog.html"'),
    ('href="/about"', 'href="/DIVINENESTWEBSITE/about.html"'),
    ('href="/contact"', 'href="/DIVINENESTWEBSITE/contact.html"'),
    ('href="/collaborate"', 'href="/DIVINENESTWEBSITE/collaborate.html"'),
    ('href="/submit-music"', 'href="/DIVINENESTWEBSITE/submit-music.html"'),
    ('href="/search"', 'href="/DIVINENESTWEBSITE/search.html"'),
    ('href="/admin"', 'href="/DIVINENESTWEBSITE/admin.html"'),
    ('href="/privacy-policy"', 'href="/DIVINENESTWEBSITE/privacy-policy.html"'),
    ('href="/terms"', 'href="/DIVINENESTWEBSITE/terms.html"'),
    ('href="/copyright"', 'href="/DIVINENESTWEBSITE/copyright.html"'),
    ('href="/disclaimer"', 'href="/DIVINENESTWEBSITE/disclaimer.html"'),
    ('href="/"', 'href="/DIVINENESTWEBSITE/"')
]

for route, filename in routes:
    url = f'{BASE_URL}{route}'
    try:
        content = urllib.request.urlopen(url).read().decode('utf-8')

        # Insert <base href="/DIVINENESTWEBSITE/">
        content = content.replace('<head>', '<head>\n  <base href="/DIVINENESTWEBSITE/">')

        # Apply path replacements
        for old, new in replacements:
            content = content.replace(old, new)

        with open(os.path.join(DIST_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Rendered {route} -> {filename}")
    except Exception as e:
        print(f"[FAIL] {route}: {e}")

# 404.html
try:
    urllib.request.urlopen(f'{BASE_URL}/404')
except urllib.error.HTTPError as e:
    c404 = e.read().decode('utf-8')
    c404 = c404.replace('<head>', '<head>\n  <base href="/DIVINENESTWEBSITE/">')
    for old, new in replacements:
        c404 = c404.replace(old, new)
    with open(os.path.join(DIST_DIR, '404.html'), 'w', encoding='utf-8') as f:
        f.write(c404)
    print("[OK] Rendered 404.html")

# Create .nojekyll file to ensure GitHub Pages does not ignore underscore or css files
with open(os.path.join(DIST_DIR, '.nojekyll'), 'w') as f:
    f.write('')

print("Static build for GitHub Pages completed successfully!")
