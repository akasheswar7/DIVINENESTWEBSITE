from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Response, abort
import sqlite3
import os
import json
from datetime import datetime
from database import get_db, init_db, seed_db, slugify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'divinenest_super_secret_key_2026')

# Initialize DB on start
init_db()
seed_db()

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'divinenest2026'

@app.context_processor
def inject_global_data():
    """Inject common stats and settings across all templates"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM videos')
    total_videos = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM music')
    total_music = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM artists')
    total_artists = cursor.fetchone()[0]
    conn.close()

    return {
        'brand_name': 'DivineNest',
        'tagline': 'Where Music, Stories & Joy Come Together',
        'youtube_url': 'https://youtube.com/@DivineNest',
        'instagram_url': 'https://instagram.com/divinenest',
        'facebook_url': 'https://facebook.com/divinenest',
        'x_url': 'https://twitter.com/divinenest',
        'total_videos': total_videos,
        'total_music': total_music,
        'total_artists': total_artists,
        'current_year': 2026,
        'is_admin': session.get('admin_logged_in', False)
    }

# ----------------- HOME & CORE PAGES -----------------

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()

    # Latest 8 videos
    cursor.execute('''
        SELECT * FROM videos 
        ORDER BY id DESC LIMIT 8
    ''')
    latest_videos = cursor.fetchall()

    # Trending Music (category = 'music' or is_trending = 1)
    cursor.execute('''
        SELECT * FROM videos 
        WHERE category = 'music' 
        ORDER BY is_trending DESC, views DESC LIMIT 6
    ''')
    trending_music = cursor.fetchall()

    # Devotional videos
    cursor.execute('''
        SELECT * FROM videos 
        WHERE category = 'devotional' 
        ORDER BY id DESC LIMIT 6
    ''')
    devotional_videos = cursor.fetchall()

    # Kids videos
    cursor.execute('''
        SELECT * FROM videos 
        WHERE category = 'kids' 
        ORDER BY id DESC LIMIT 6
    ''')
    kids_videos = cursor.fetchall()

    # Shorts
    cursor.execute('''
        SELECT * FROM videos 
        WHERE category = 'shorts' 
        ORDER BY views DESC LIMIT 4
    ''')
    shorts_videos = cursor.fetchall()

    # Featured Artists
    cursor.execute('''
        SELECT * FROM artists 
        WHERE featured = 1 
        ORDER BY id ASC LIMIT 4
    ''')
    featured_artists = cursor.fetchall()

    # Playlists
    cursor.execute('''
        SELECT * FROM playlists 
        WHERE featured = 1 
        ORDER BY id ASC LIMIT 4
    ''')
    popular_playlists = cursor.fetchall()

    # Latest Blogs
    cursor.execute('''
        SELECT * FROM blogs 
        ORDER BY id DESC LIMIT 3
    ''')
    latest_blogs = cursor.fetchall()

    conn.close()

    return render_template(
        'index.html',
        latest_videos=latest_videos,
        trending_music=trending_music,
        devotional_videos=devotional_videos,
        kids_videos=kids_videos,
        shorts_videos=shorts_videos,
        featured_artists=featured_artists,
        popular_playlists=popular_playlists,
        latest_blogs=latest_blogs
    )

@app.route('/music')
def music():
    genre = request.args.get('genre', 'all').strip().lower()
    lang = request.args.get('lang', 'all').strip().capitalize()

    conn = get_db()
    cursor = conn.cursor()

    query = 'SELECT * FROM music WHERE 1=1'
    params = []

    if genre != 'all':
        query += ' AND LOWER(genre) LIKE ?'
        params.append(f'%{genre}%')
    
    if lang != 'All':
        query += ' AND language = ?'
        params.append(lang)

    query += ' ORDER BY featured DESC, id DESC'
    cursor.execute(query, params)
    music_items = cursor.fetchall()

    # Also fetch music video clips
    cursor.execute("SELECT * FROM videos WHERE category = 'music' ORDER BY is_trending DESC, id DESC LIMIT 8")
    music_videos = cursor.fetchall()

    conn.close()

    genres = ['All', 'Original Music', 'Love & Melody', 'Classical & Traditional', 'Trending Music', 'Instrumental']
    languages = ['All', 'Telugu', 'Hindi', 'English', 'Instrumental']

    return render_template(
        'music.html',
        music_items=music_items,
        music_videos=music_videos,
        current_genre=genre,
        current_lang=lang,
        genres=genres,
        languages=languages
    )

@app.route('/devotional')
def devotional():
    deity = request.args.get('deity', 'all').strip().lower()
    category_type = request.args.get('type', 'all').strip().lower()

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM videos WHERE category = 'devotional'"
    params = []

    if deity != 'all':
        query += ' AND LOWER(subcategory) LIKE ?'
        params.append(f'%{deity}%')

    query += ' ORDER BY views DESC, id DESC'
    cursor.execute(query, params)
    devotional_videos = cursor.fetchall()

    conn.close()

    deities = [
        ('all', 'All Deities'),
        ('shiva', '🕉️ Shiva'),
        ('krishna', '💙 Krishna'),
        ('rama', '🏹 Rama'),
        ('hanuman', '🙏 Hanuman'),
        ('ganesha', '🐘 Ganesha'),
        ('venkateswara', '🛕 Venkateswara'),
        ('durga', '🔱 Durga'),
        ('lakshmi', '🪷 Lakshmi')
    ]

    return render_template(
        'devotional.html',
        devotional_videos=devotional_videos,
        current_deity=deity,
        current_type=category_type,
        deities=deities
    )

@app.route('/kids')
def kids():
    subcat = request.args.get('category', 'all').strip().lower()
    age = request.args.get('age', 'all').strip()

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM videos WHERE category = 'kids'"
    params = []

    if subcat != 'all':
        query += ' AND LOWER(subcategory) LIKE ?'
        params.append(f'%{subcat}%')

    if age != 'all' and age:
        query += ' AND age_group LIKE ?'
        params.append(f'%{age}%')

    query += ' ORDER BY id DESC'
    cursor.execute(query, params)
    kids_videos = cursor.fetchall()

    conn.close()

    categories = [
        ('all', '🌟 All Kids'),
        ('rhymes', '🎵 Nursery & Telugu Rhymes'),
        ('bedtime songs', '🌙 Bedtime Songs'),
        ('moral stories', '📖 Animated Stories (Benny & Chuchu)'),
        ('cartoons', '🐻 Fun Cartoons'),
        ('learning', '🌈 Early Learning (ABC & Numbers)')
    ]

    return render_template(
        'kids.html',
        kids_videos=kids_videos,
        current_category=subcat,
        current_age=age,
        categories=categories
    )

@app.route('/shorts')
def shorts():
    cat = request.args.get('category', 'all').strip().lower()

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM videos WHERE category = 'shorts'"
    params = []

    if cat != 'all':
        query += ' AND LOWER(subcategory) LIKE ?'
        params.append(f'%{cat}%')

    query += ' ORDER BY views DESC, id DESC'
    cursor.execute(query, params)
    shorts_list = cursor.fetchall()

    conn.close()

    categories = [
        ('all', '⚡ All Shorts'),
        ('music', '🎵 Music Shorts'),
        ('devotional', '🙏 Devotional Shorts'),
        ('kids', '🧒 Kids Shorts'),
        ('behind the scenes', '🎬 Behind The Scenes')
    ]

    return render_template(
        'shorts.html',
        shorts_list=shorts_list,
        current_category=cat,
        categories=categories
    )

@app.route('/videos')
def videos():
    category = request.args.get('category', 'all').strip().lower()
    lang = request.args.get('lang', 'all').strip().capitalize()
    sort = request.args.get('sort', 'latest').strip().lower()
    q = request.args.get('q', '').strip()

    conn = get_db()
    cursor = conn.cursor()

    query = 'SELECT * FROM videos WHERE 1=1'
    params = []

    if category != 'all':
        query += ' AND category = ?'
        params.append(category)

    if lang != 'All':
        query += ' AND language = ?'
        params.append(lang)

    if q:
        query += ' AND (title LIKE ? OR description LIKE ? OR tags LIKE ?)'
        wildcard = f'%{q}%'
        params.extend([wildcard, wildcard, wildcard])

    if sort == 'popular' or sort == 'views':
        query += ' ORDER BY views DESC'
    elif sort == 'az':
        query += ' ORDER BY title ASC'
    else:
        query += ' ORDER BY id DESC'

    cursor.execute(query, params)
    video_list = cursor.fetchall()

    conn.close()

    categories = ['all', 'music', 'devotional', 'kids', 'entertainment', 'shorts']
    languages = ['All', 'Telugu', 'Hindi', 'English']

    return render_template(
        'videos.html',
        videos=video_list,
        current_category=category,
        current_lang=lang,
        current_sort=sort,
        search_query=q,
        categories=categories,
        languages=languages
    )

@app.route('/video/<slug>')
def video_detail(slug):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM videos WHERE slug = ? OR id = ?', (slug, slug))
    video = cursor.fetchone()

    if not video:
        conn.close()
        abort(404)

    # Increment view count
    cursor.execute('UPDATE videos SET views = views + 1 WHERE id = ?', (video['id'],))
    conn.commit()

    # Get 6 related videos (same category or general)
    cursor.execute('''
        SELECT * FROM videos 
        WHERE category = ? AND id != ? 
        ORDER BY views DESC LIMIT 6
    ''', (video['category'], video['id']))
    related_videos = cursor.fetchall()

    # If fewer than 6, backfill with top videos
    if len(related_videos) < 6:
        cursor.execute('''
            SELECT * FROM videos 
            WHERE id != ? 
            ORDER BY views DESC LIMIT ?
        ''', (video['id'], 6 - len(related_videos)))
        more_videos = cursor.fetchall()
        related_videos = list(related_videos) + list(more_videos)

    conn.close()

    return render_template(
        'video_detail.html',
        video=video,
        related_videos=related_videos
    )

@app.route('/artists')
def artists():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM artists ORDER BY featured DESC, id ASC')
    artist_list = cursor.fetchall()
    conn.close()

    return render_template('artists.html', artists=artist_list)

@app.route('/artists/<slug>')
def artist_detail(slug):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM artists WHERE slug = ? OR id = ?', (slug, slug))
    artist = cursor.fetchone()

    if not artist:
        conn.close()
        abort(404)

    # Videos by this artist
    cursor.execute('''
        SELECT * FROM videos 
        WHERE artist_id = ? OR artist_name LIKE ? 
        ORDER BY views DESC
    ''', (artist['id'], f"%{artist['name']}%"))
    artist_videos = cursor.fetchall()

    # Music by this artist
    cursor.execute('''
        SELECT * FROM music 
        WHERE artist_name LIKE ? OR singer LIKE ?
        ORDER BY id DESC
    ''', (f"%{artist['name']}%", f"%{artist['name']}%"))
    artist_music = cursor.fetchall()

    conn.close()

    return render_template(
        'artist_detail.html',
        artist=artist,
        artist_videos=artist_videos,
        artist_music=artist_music
    )

@app.route('/playlists')
def playlists():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM playlists ORDER BY featured DESC, id ASC')
    playlist_list = cursor.fetchall()
    conn.close()

    return render_template('playlists.html', playlists=playlist_list)

@app.route('/playlists/<slug>')
def playlist_detail(slug):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM playlists WHERE slug = ? OR id = ?', (slug, slug))
    playlist = cursor.fetchone()

    if not playlist:
        conn.close()
        abort(404)

    # Fetch videos in this playlist category
    cursor.execute('''
        SELECT * FROM videos 
        WHERE category = ? OR subcategory LIKE ? 
        ORDER BY id ASC LIMIT 10
    ''', (playlist['category'].lower(), f"%{playlist['category'].lower()}%"))
    playlist_videos = cursor.fetchall()

    if not playlist_videos:
        cursor.execute('SELECT * FROM videos ORDER BY views DESC LIMIT 8')
        playlist_videos = cursor.fetchall()

    conn.close()

    return render_template(
        'playlist_detail.html',
        playlist=playlist,
        playlist_videos=playlist_videos
    )

@app.route('/blog')
def blog():
    cat = request.args.get('category', 'all').strip().lower()

    conn = get_db()
    cursor = conn.cursor()

    query = 'SELECT * FROM blogs WHERE 1=1'
    params = []

    if cat != 'all':
        query += ' AND LOWER(category) = ?'
        params.append(cat)

    query += ' ORDER BY id DESC'
    cursor.execute(query, params)
    blog_list = cursor.fetchall()

    conn.close()

    categories = ['All', 'Music', 'Devotional', 'Kids', 'Entertainment', 'Artists', 'Inspiration']

    return render_template(
        'blog.html',
        blogs=blog_list,
        current_category=cat,
        categories=categories
    )

@app.route('/blog/<slug>')
def blog_detail(slug):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM blogs WHERE slug = ? OR id = ?', (slug, slug))
    article = cursor.fetchone()

    if not article:
        conn.close()
        abort(404)

    # Recent blogs
    cursor.execute('SELECT * FROM blogs WHERE id != ? ORDER BY id DESC LIMIT 3', (article['id'],))
    recent_blogs = cursor.fetchall()

    conn.close()

    return render_template(
        'blog_detail.html',
        article=article,
        recent_blogs=recent_blogs
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/collaborate')
def collaborate():
    return render_template('collaborate.html')

@app.route('/submit-music')
def submit_music():
    return render_template('submit_music.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    
    conn = get_db()
    cursor = conn.cursor()

    if query:
        wildcard = f'%{query}%'

        # Search in videos (titles, descriptions, tags, singers, deities/subcategories, languages, lyrics)
        cursor.execute('''
            SELECT * FROM videos 
            WHERE title LIKE ? OR description LIKE ? OR tags LIKE ? OR artist_name LIKE ? 
               OR subcategory LIKE ? OR category LIKE ? OR language LIKE ? OR lyrics LIKE ?
            ORDER BY views DESC LIMIT 20
        ''', (wildcard, wildcard, wildcard, wildcard, wildcard, wildcard, wildcard, wildcard))
        videos_found = cursor.fetchall()

        # Search in music
        cursor.execute('''
            SELECT * FROM music 
            WHERE title LIKE ? OR artist_name LIKE ? OR singer LIKE ? OR composer LIKE ? 
               OR genre LIKE ? OR language LIKE ? OR lyrics LIKE ?
            ORDER BY id DESC LIMIT 12
        ''', (wildcard, wildcard, wildcard, wildcard, wildcard, wildcard, wildcard))
        music_found = cursor.fetchall()

        # Search in artists
        cursor.execute('''
            SELECT * FROM artists 
            WHERE name LIKE ? OR bio LIKE ? OR role LIKE ?
            LIMIT 6
        ''', (wildcard, wildcard, wildcard))
        artists_found = cursor.fetchall()

        # Search in blogs
        cursor.execute('''
            SELECT * FROM blogs 
            WHERE title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ?
            LIMIT 4
        ''', (wildcard, wildcard, wildcard, wildcard))
        blogs_found = cursor.fetchall()

        total_results = len(videos_found) + len(music_found) + len(artists_found) + len(blogs_found)
    else:
        # Default top discovery content when visiting search without a query
        cursor.execute('SELECT * FROM videos ORDER BY views DESC LIMIT 12')
        videos_found = cursor.fetchall()
        cursor.execute('SELECT * FROM music ORDER BY id DESC LIMIT 6')
        music_found = cursor.fetchall()
        cursor.execute('SELECT * FROM artists LIMIT 4')
        artists_found = cursor.fetchall()
        cursor.execute('SELECT * FROM blogs LIMIT 4')
        blogs_found = cursor.fetchall()
        total_results = len(videos_found) + len(music_found)

    return render_template(
        'search.html',
        query=query,
        total_results=total_results,
        videos=videos_found,
        music=music_found,
        artists=artists_found,
        blogs=blogs_found
    )

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('legal.html', page_type='privacy')

@app.route('/terms')
def terms():
    return render_template('legal.html', page_type='terms')

@app.route('/copyright')
def copyright_page():
    return render_template('legal.html', page_type='copyright')

@app.route('/disclaimer')
def disclaimer():
    return render_template('legal.html', page_type='disclaimer')

# ----------------- API ENDPOINTS -----------------

@app.route('/api/newsletter', methods=['POST'])
def api_newsletter():
    data = request.get_json(silent=True) or request.form
    email = data.get('email', '').strip().lower()

    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Please provide a valid email address.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Thank you for subscribing to DivineNest updates!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': True, 'message': 'You are already subscribed to DivineNest!'})
    finally:
        conn.close()

@app.route('/api/inquiry', methods=['POST'])
def api_inquiry():
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'Name, email, and message are required.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inquiries (name, email, phone, subject, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, phone, subject, message))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Thank you! Your message has been sent to the DivineNest team.'})

@app.route('/api/collaborate', methods=['POST'])
def api_collaborate():
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    category = data.get('category', '').strip()
    portfolio = data.get('portfolio_link', '').strip()
    proposal = data.get('proposal', '').strip()

    if not name or not email or not proposal:
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collaborations (name, email, phone, category, portfolio_link, proposal)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, phone, category, portfolio, proposal))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Your collaboration request has been submitted successfully!'})

@app.route('/api/submit-music', methods=['POST'])
def api_submit_music():
    data = request.get_json(silent=True) or request.form
    artist_name = data.get('artist_name', '').strip()
    song_name = data.get('song_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    language = data.get('language', '').strip()
    genre = data.get('genre', '').strip()
    youtube_link = data.get('youtube_link', '').strip()
    audio_link = data.get('audio_link', '').strip()
    social_media = data.get('social_media', '').strip()
    message = data.get('message', '').strip()

    if not artist_name or not song_name or not email:
        return jsonify({'success': False, 'message': 'Artist name, song name, and email are required.'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO music_submissions (artist_name, song_name, email, phone, language, genre, youtube_link, audio_link, social_media, message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (artist_name, song_name, email, phone, language, genre, youtube_link, audio_link, social_media, message))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Your song has been received for review by DivineNest Music!'})

@app.route('/api/videos/<int:video_id>/like', methods=['POST'])
def api_like_video(video_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE videos SET likes = likes + 1 WHERE id = ?', (video_id,))
    conn.commit()
    cursor.execute('SELECT likes FROM videos WHERE id = ?', (video_id,))
    likes = cursor.fetchone()[0]
    conn.close()
    return jsonify({'success': True, 'likes': likes})

# ----------------- ADMIN DASHBOARD & CRUD -----------------

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin.html', error='Invalid admin credentials. Use admin / divinenest2026')

    if not session.get('admin_logged_in'):
        return render_template('admin.html', need_login=True)

    conn = get_db()
    cursor = conn.cursor()

    # Stats
    cursor.execute('SELECT COUNT(*) FROM videos')
    stats_videos = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM music')
    stats_music = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM artists')
    stats_artists = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM playlists')
    stats_playlists = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM blogs')
    stats_blogs = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM subscribers')
    stats_subscribers = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM inquiries')
    stats_inquiries = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM collaborations')
    stats_collabs = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM music_submissions')
    stats_submissions = cursor.fetchone()[0]

    # Video list
    cursor.execute('SELECT * FROM videos ORDER BY id DESC')
    all_videos = cursor.fetchall()

    # Music list
    cursor.execute('SELECT * FROM music ORDER BY id DESC')
    all_music = cursor.fetchall()

    # Artists list
    cursor.execute('SELECT * FROM artists ORDER BY id DESC')
    all_artists = cursor.fetchall()

    # Playlists list
    cursor.execute('SELECT * FROM playlists ORDER BY id DESC')
    all_playlists = cursor.fetchall()

    # Blog list
    cursor.execute('SELECT * FROM blogs ORDER BY id DESC')
    all_blogs = cursor.fetchall()

    # Recent inquiries
    cursor.execute('SELECT * FROM inquiries ORDER BY id DESC LIMIT 20')
    inquiries = cursor.fetchall()

    # Recent submissions
    cursor.execute('SELECT * FROM music_submissions ORDER BY id DESC LIMIT 20')
    submissions = cursor.fetchall()

    # Collaborations
    cursor.execute('SELECT * FROM collaborations ORDER BY id DESC LIMIT 20')
    collabs = cursor.fetchall()

    conn.close()

    stats = {
        'videos': stats_videos,
        'music': stats_music,
        'artists': stats_artists,
        'playlists': stats_playlists,
        'blogs': stats_blogs,
        'subscribers': stats_subscribers,
        'inquiries': stats_inquiries,
        'collabs': stats_collabs,
        'submissions': stats_submissions
    }

    return render_template(
        'admin.html',
        need_login=False,
        stats=stats,
        videos=all_videos,
        music=all_music,
        artists=all_artists,
        playlists=all_playlists,
        blogs=all_blogs,
        inquiries=inquiries,
        submissions=submissions,
        collabs=collabs
    )

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

@app.route('/admin/video/add', methods=['POST'])
def admin_add_video():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    title = request.form.get('title')
    youtube_id = request.form.get('youtube_id')
    category = request.form.get('category')
    subcategory = request.form.get('subcategory', '')
    artist_name = request.form.get('artist_name', 'DivineNest')
    language = request.form.get('language', 'Telugu')
    duration = request.form.get('duration', '4:00')
    description = request.form.get('description', '')
    tags = request.form.get('tags', '')
    age_group = request.form.get('age_group', '')
    thumbnail = request.form.get('thumbnail') or f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"
    is_featured = 1 if request.form.get('is_featured') else 0
    is_trending = 1 if request.form.get('is_trending') else 0
    published_date = datetime.now().strftime('%b %d, %Y')
    slug = slugify(title)

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO videos (slug, title, youtube_id, thumbnail, category, subcategory, artist_name, language, duration, published_date, description, tags, is_featured, is_trending, age_group)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (slug, title, youtube_id, thumbnail, category, subcategory, artist_name, language, duration, published_date, description, tags, is_featured, is_trending, age_group))
        conn.commit()
    except sqlite3.IntegrityError:
        slug = f"{slug}-{int(datetime.now().timestamp())}"
        cursor.execute('''
            INSERT INTO videos (slug, title, youtube_id, thumbnail, category, subcategory, artist_name, language, duration, published_date, description, tags, is_featured, is_trending, age_group)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (slug, title, youtube_id, thumbnail, category, subcategory, artist_name, language, duration, published_date, description, tags, is_featured, is_trending, age_group))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for('admin') + '#videos')

@app.route('/admin/video/delete/<int:video_id>', methods=['POST'])
def admin_delete_video(video_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM videos WHERE id = ?', (video_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin') + '#videos')

@app.route('/admin/music/add', methods=['POST'])
def admin_add_music():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    title = request.form.get('title')
    artist_name = request.form.get('artist_name')
    singer = request.form.get('singer', '')
    composer = request.form.get('composer', '')
    lyricist = request.form.get('lyricist', '')
    language = request.form.get('language', 'Telugu')
    genre = request.form.get('genre', 'Original Music')
    youtube_id = request.form.get('youtube_id', '')
    audio_url = request.form.get('audio_url', '')
    thumbnail = request.form.get('thumbnail', '')
    duration = request.form.get('duration', '3:45')
    release_date = datetime.now().strftime('%b %d, %Y')
    slug = slugify(title)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO music (slug, title, artist_name, singer, composer, lyricist, language, genre, youtube_id, audio_url, thumbnail, duration, release_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (slug, title, artist_name, singer, composer, lyricist, language, genre, youtube_id, audio_url, thumbnail, duration, release_date))
    conn.commit()
    conn.close()

    return redirect(url_for('admin') + '#music')

@app.route('/admin/music/delete/<int:music_id>', methods=['POST'])
def admin_delete_music(music_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM music WHERE id = ?', (music_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin') + '#music')

# ----------------- SEO: SITEMAP & ROBOTS -----------------

@app.route('/sitemap.xml')
def sitemap():
    pages = [
        '', 'music', 'devotional', 'kids', 'shorts', 'videos',
        'artists', 'playlists', 'blog', 'about', 'contact',
        'collaborate', 'submit-music', 'privacy-policy', 'terms', 'copyright', 'disclaimer'
    ]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT slug FROM videos')
    video_slugs = [row['slug'] for row in cursor.fetchall()]
    cursor.execute('SELECT slug FROM artists')
    artist_slugs = [row['slug'] for row in cursor.fetchall()]
    cursor.execute('SELECT slug FROM blogs')
    blog_slugs = [row['slug'] for row in cursor.fetchall()]
    conn.close()

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    base_url = request.url_root.rstrip('/')

    for page in pages:
        loc = f"{base_url}/{page}".rstrip('/')
        xml.append(f'  <url><loc>{loc}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>')

    for slug in video_slugs:
        xml.append(f'  <url><loc>{base_url}/video/{slug}</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>')

    for slug in artist_slugs:
        xml.append(f'  <url><loc>{base_url}/artists/{slug}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>')

    for slug in blog_slugs:
        xml.append(f'  <url><loc>{base_url}/blog/{slug}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>')

    xml.append('</urlset>')

    return Response('\n'.join(xml), mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/

Sitemap: {request.url_root}sitemap.xml
"""
    return Response(content, mimetype='text/plain')

# ----------------- 404 ERROR HANDLER -----------------

@app.errorhandler(404)
def error_404(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
