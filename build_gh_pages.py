import urllib.request
import os
import shutil
import sqlite3
import database

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

# Fetch dynamic routes from database
conn = database.get_db()
cursor = conn.cursor()

# Videos
cursor.execute("SELECT slug FROM videos WHERE slug IS NOT NULL")
for row in cursor.fetchall():
    slug = row['slug']
    routes.append((f'/video/{slug}', f'video/{slug}.html'))

# Artists
cursor.execute("SELECT slug FROM artists WHERE slug IS NOT NULL")
for row in cursor.fetchall():
    slug = row['slug']
    routes.append((f'/artists/{slug}', f'artists/{slug}.html'))

# Playlists
cursor.execute("SELECT slug FROM playlists WHERE slug IS NOT NULL")
for row in cursor.fetchall():
    slug = row['slug']
    routes.append((f'/playlists/{slug}', f'playlists/{slug}.html'))

# Blogs
cursor.execute("SELECT slug FROM blogs WHERE slug IS NOT NULL")
for row in cursor.fetchall():
    slug = row['slug']
    routes.append((f'/blog/{slug}', f'blog/{slug}.html'))

conn.close()

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
    ('href="/video/', 'href="/DIVINENESTWEBSITE/video/'),
    ('href="/artists/', 'href="/DIVINENESTWEBSITE/artists/'),
    ('href="/playlists/', 'href="/DIVINENESTWEBSITE/playlists/'),
    ('href="/blog/', 'href="/DIVINENESTWEBSITE/blog/'),
    ('href="/"', 'href="/DIVINENESTWEBSITE/"')
]

for route, rel_path in routes:
    url = f'{BASE_URL}{route}'
    try:
        content = urllib.request.urlopen(url).read().decode('utf-8')

        # Insert <base href="/DIVINENESTWEBSITE/">
        content = content.replace('<head>', '<head>\n  <base href="/DIVINENESTWEBSITE/">')

        # Apply path replacements
        for old, new in replacements:
            content = content.replace(old, new)

        # For links like href="/DIVINENESTWEBSITE/video/some-slug" turn into "href="/DIVINENESTWEBSITE/video/some-slug.html"
        import re
        content = re.sub(r'href="/DIVINENESTWEBSITE/video/([a-zA-Z0-9_-]+)"', r'href="/DIVINENESTWEBSITE/video/\1.html"', content)
        content = re.sub(r'href="/DIVINENESTWEBSITE/artists/([a-zA-Z0-9_-]+)"', r'href="/DIVINENESTWEBSITE/artists/\1.html"', content)
        content = re.sub(r'href="/DIVINENESTWEBSITE/playlists/([a-zA-Z0-9_-]+)"', r'href="/DIVINENESTWEBSITE/playlists/\1.html"', content)
        content = re.sub(r'href="/DIVINENESTWEBSITE/blog/([a-zA-Z0-9_-]+)"', r'href="/DIVINENESTWEBSITE/blog/\1.html"', content)

        out_file = os.path.join(DIST_DIR, rel_path)
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Also write index.html in the folder for directory URLs
        if rel_path.endswith('.html') and '/' in rel_path:
            dir_path = os.path.join(DIST_DIR, rel_path[:-5])
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content)

        print(f"[OK] Rendered {route} -> {rel_path}")
    except Exception as e:
        print(f"[FAIL] {route}: {e}")

# 404.html with automatic path recovery script
c404 = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <base href="/DIVINENESTWEBSITE/">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Redirecting — DivineNest</title>
  <script>
    var path = window.location.pathname;
    if (path.includes('/DIVINENESTWEBSITE/')) {
      var sub = path.replace(/.*\\/DIVINENESTWEBSITE\\//, '');
      if (sub && !sub.endsWith('.html') && !sub.includes('.')) {
        window.location.replace('/DIVINENESTWEBSITE/' + sub + '.html' + window.location.search);
      } else if (!sub || sub === '/') {
        window.location.replace('/DIVINENESTWEBSITE/');
      }
    }
  </script>
  <link rel="stylesheet" href="/DIVINENESTWEBSITE/static/css/style.css">
</head>
<body style="min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; background: #060810; color: #fff; font-family: sans-serif; padding: 2rem;">
  <div>
    <h1 style="font-size: 3rem; margin-bottom: 1rem; color: #FBBF24;">404 — Divine Joy Awaits</h1>
    <p style="font-size: 1.2rem; color: #94A3B8; margin-bottom: 2rem;">The page you are looking for has taken flight into the melodies of DivineNest.</p>
    <a href="/DIVINENESTWEBSITE/" style="background: linear-gradient(135deg, #F59E0B, #EC4899); color: #fff; text-decoration: none; padding: 0.8rem 1.8rem; border-radius: 9999px; font-weight: 700; display: inline-block;">Return to DivineNest Home</a>
  </div>
</body>
</html>
"""

with open(os.path.join(DIST_DIR, '404.html'), 'w', encoding='utf-8') as f:
    f.write(c404)
print("[OK] Rendered 404.html")

# Create .nojekyll file to ensure GitHub Pages does not ignore underscore or css files
with open(os.path.join(DIST_DIR, '.nojekyll'), 'w') as f:
    f.write('')

print(f"Static build for GitHub Pages completed successfully! Total pages: {len(routes)}")
