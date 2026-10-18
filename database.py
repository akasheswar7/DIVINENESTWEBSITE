import sqlite3
import os
import re
import tempfile
import shutil
from datetime import datetime

# In serverless environments like Vercel, root filesystem is read-only, use /tmp
if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    TEMP_DIR = tempfile.gettempdir()
    DB_PATH = os.path.join(TEMP_DIR, 'divinenest.db')
    LOCAL_DB = os.path.join(os.path.dirname(__file__), 'divinenest.db')
    if not os.path.exists(DB_PATH) and os.path.exists(LOCAL_DB):
        shutil.copyfile(LOCAL_DB, DB_PATH)
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'divinenest.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text).strip('-')
    return text

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Videos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        title TEXT NOT NULL,
        youtube_id TEXT NOT NULL,
        thumbnail TEXT,
        category TEXT NOT NULL,
        subcategory TEXT,
        artist_id INTEGER,
        artist_name TEXT,
        language TEXT DEFAULT 'Telugu',
        duration TEXT DEFAULT '4:15',
        views INTEGER DEFAULT 1200,
        likes INTEGER DEFAULT 150,
        published_date TEXT,
        description TEXT,
        tags TEXT,
        is_featured INTEGER DEFAULT 0,
        is_trending INTEGER DEFAULT 0,
        age_group TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Music table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS music (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        title TEXT NOT NULL,
        artist_name TEXT,
        singer TEXT,
        composer TEXT,
        lyricist TEXT,
        language TEXT DEFAULT 'Telugu',
        genre TEXT NOT NULL,
        youtube_id TEXT NOT NULL,
        audio_url TEXT,
        thumbnail TEXT,
        duration TEXT DEFAULT '3:50',
        release_date TEXT,
        featured INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Artists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        genre TEXT,
        languages TEXT,
        photo TEXT,
        bio TEXT,
        youtube TEXT,
        instagram TEXT,
        facebook TEXT,
        featured INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Playlists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        title TEXT NOT NULL,
        description TEXT,
        cover_image TEXT,
        category TEXT,
        video_count INTEGER DEFAULT 0,
        youtube_playlist_id TEXT,
        featured INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Playlist Videos relationship
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlist_videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER NOT NULL,
        video_id INTEGER NOT NULL,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE,
        FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE
    )
    ''')

    # Blog table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        featured_image TEXT,
        summary TEXT,
        content TEXT,
        author TEXT DEFAULT 'DivineNest Team',
        published_date TEXT,
        read_time TEXT DEFAULT '5 min read',
        tags TEXT,
        youtube_video_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Inquiries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        subject TEXT,
        message TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new'
    )
    ''')

    # Collaborations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS collaborations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        category TEXT NOT NULL,
        portfolio_link TEXT,
        proposal TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending'
    )
    ''')

    # Music submissions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS music_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_name TEXT NOT NULL,
        song_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        language TEXT,
        genre TEXT,
        youtube_link TEXT,
        audio_link TEXT,
        social_media TEXT,
        message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'under_review'
    )
    ''')

    # Newsletter subscribers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute('SELECT COUNT(*) FROM videos')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Seed Artists
    artists_data = [
        (
            'ananya-sharma',
            'Ananya Sharma',
            'Lead Singer & Composer',
            'Melody, Classical Fusion, Devotional',
            'Telugu, Hindi, English',
            'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&auto=format&fit=crop&q=80',
            'Ananya is a gifted vocalist and composer with over a decade of training in Carnatic classical music. Her soulful renditions of devotional and romantic melodies have captivated millions of listeners worldwide.',
            'https://youtube.com/@DivineNest',
            'https://instagram.com/divinenest',
            'https://facebook.com/divinenest',
            1
        ),
        (
            'karthik-varma',
            'Karthik Varma',
            'Spiritual Vocalist & Chants Master',
            'Bhajans, Mantras, Vedic Chants',
            'Telugu, Sanskrit, Hindi',
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&auto=format&fit=crop&q=80',
            'Karthik specializes in authentic Vedic stotrams, powerful Shiva chants, and heart-melting bhajans. His resonance creates a serene sanctuary of peace and devotion.',
            'https://youtube.com/@DivineNest',
            'https://instagram.com/divinenest',
            'https://facebook.com/divinenest',
            1
        ),
        (
            'rahul-roy',
            'Rahul Roy & The Storytoons',
            'Voice Artist & Animator',
            'Kids Stories, Cartoons, Rhymes',
            'Telugu, Hindi, English',
            'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&auto=format&fit=crop&q=80',
            'Rahul leads the children animation wing at DivineNest, bringing playful characters, vibrant fables, and inspiring bedtime stories to life for kids of all ages.',
            'https://youtube.com/@DivineNest',
            'https://instagram.com/divinenest',
            'https://facebook.com/divinenest',
            1
        ),
        (
            'sneha-menon',
            'Sneha Menon',
            'Instrumental Flautist & Producer',
            'Bansuri, Ambient, Meditation, Relaxing',
            'Instrumental',
            'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&auto=format&fit=crop&q=80',
            'Sneha weaves magic with the Indian bamboo flute (Bansuri), blending traditional ragas with ambient soundscapes to create deeply soothing sound journeys.',
            'https://youtube.com/@DivineNest',
            'https://instagram.com/divinenest',
            'https://facebook.com/divinenest',
            1
        ),
        (
            'priya-sen',
            'Priya Sen',
            'Acoustic Pop & Contemporary Artist',
            'Indie Acoustic, Inspiring Ballads',
            'English, Hindi',
            'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&auto=format&fit=crop&q=80',
            'Priya brings contemporary heartfelt acoustic music with uplifting messages of hope, joy, and family togetherness.',
            'https://youtube.com/@DivineNest',
            'https://instagram.com/divinenest',
            'https://facebook.com/divinenest',
            0
        )
    ]

    cursor.executemany('''
    INSERT INTO artists (slug, name, role, genre, languages, photo, bio, youtube, instagram, facebook, featured)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', artists_data)

    # Seed Videos (with safe YouTube embed IDs: e.g. popular royalty-free/official safe IDs like lTRiuFIWV54, JFcgOboQZ08, 5qap5aO4i9A, etc.)
    videos_data = [
        # MUSIC
        (
            'divine-morning-melody',
            'Soulful Morning Melody | DivineNest Music Original',
            'jfKfPfyJRdk', # lofi / soothing music stream safe id
            'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80',
            'music',
            'original',
            1,
            'Ananya Sharma',
            'Telugu',
            '4:45',
            45200,
            3800,
            'Oct 12, 2026',
            'Experience this enchanting original morning melody from DivineNest Music. An uplifting combination of acoustic guitars, flute, and soulful vocals to brighten your day.',
            'music, melody, telugu song, morning song, divinenest original',
            1,
            1,
            ''
        ),
        (
            'chandamama-love-song',
            'Chandamama Love Melody | Romantic Acoustic Song',
            'DWcJFNfaw9c',
            'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80',
            'music',
            'love',
            1,
            'Ananya Sharma',
            'Telugu',
            '3:58',
            38900,
            2950,
            'Oct 05, 2026',
            'A sweet romantic composition celebrating pure love under the starry moonlight. Listen, relax, and share with your loved ones.',
            'love song, romantic, acoustic, telugu, divinenest',
            1,
            1,
            ''
        ),
        (
            'divine-flute-meditation',
            'Bansuri Flute Serenity | Relaxing Instrumental Peace',
            'e3L1PIY1pN8',
            'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format&fit=crop&q=80',
            'music',
            'instrumental',
            4,
            'Sneha Menon',
            'Instrumental',
            '10:15',
            89400,
            7600,
            'Sep 28, 2026',
            'Deeply relaxing bamboo flute meditation music for calm study, deep sleep, yoga, and inner peace.',
            'flute, bansuri, instrumental, meditation, relaxing',
            1,
            0,
            ''
        ),
        (
            'raaga-symphony-classical',
            'Raaga Symphony | Indian Classical Fusion',
            '9bZkp7q19f0',
            'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80',
            'music',
            'classical',
            1,
            'Ananya Sharma',
            'Hindi',
            '5:30',
            24500,
            1840,
            'Sep 18, 2026',
            'A glorious fusion of traditional Indian raga movements with modern orchestral grandeur.',
            'classical, raga, fusion, traditional, divinenest',
            0,
            0,
            ''
        ),
        (
            'journey-of-hope',
            'Journey of Hope | Uplifting English Acoustic Ballad',
            'kJQP7kiw5Fk',
            'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=800&auto=format&fit=crop&q=80',
            'music',
            'trending',
            5,
            'Priya Sen',
            'English',
            '3:45',
            18200,
            1450,
            'Sep 10, 2026',
            'An inspirational acoustic anthem reminding every listener that brighter days are ahead.',
            'english song, acoustic, inspirational, hope, divinenest',
            0,
            0,
            ''
        ),

        # DEVOTIONAL
        (
            'maha-mrityunjaya-mantra',
            'Maha Mrityunjaya Mantra 108 Times | Divine Shiva Chants',
            'H5v3kku4y6Q',
            'https://images.unsplash.com/photo-1545062990-4a95e8e4b96d?w=800&auto=format&fit=crop&q=80',
            'devotional',
            'shiva',
            2,
            'Karthik Varma',
            'Sanskrit',
            '21:00',
            154000,
            12800,
            'Oct 10, 2026',
            'Powerful Maha Mrityunjaya Mantra chanted 108 times for health, peace, protection, and overcoming all fears. Soulfully rendered by Karthik Varma.',
            'shiva, maha mrityunjaya mantra, 108 times, chants, devotional',
            1,
            1,
            ''
        ),
        (
            'achyutam-keshavam-krishna-bhajan',
            'Achyutam Keshavam Krishna Bhajan | Soulful Devotion',
            '1ZYbU88VHWY',
            'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=800&auto=format&fit=crop&q=80',
            'devotional',
            'krishna',
            1,
            'Ananya Sharma',
            'Telugu',
            '6:15',
            98700,
            8450,
            'Oct 02, 2026',
            'Achyutam Keshavam Rama Narayanam - The sweetest praise of Lord Sri Krishna and Rama. Let your mind dive into divine ecstasy.',
            'krishna, achyutam keshavam, bhajan, devotional songs, divinenest',
            1,
            1,
            ''
        ),
        (
            'hanuman-chalisa-peaceful',
            'Peaceful Hanuman Chalisa | Divine Strength & Peace',
            'A6g_0k3zZ_M',
            'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&auto=format&fit=crop&q=80',
            'devotional',
            'hanuman',
            2,
            'Karthik Varma',
            'Hindi',
            '9:40',
            121000,
            10900,
            'Sep 24, 2026',
            'A serene, devotional rendition of Sri Hanuman Chalisa. Listen every Tuesday and Saturday to invite strength, courage, and auspiciousness.',
            'hanuman, hanuman chalisa, bajrangbali, bhakti, divinenest devotional',
            1,
            1,
            ''
        ),
        (
            'sri-ganesha-suprabhatam',
            'Sri Ganesha Pancharatnam | Morning Divine Chants',
            'kffacxfA7G4',
            'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=800&auto=format&fit=crop&q=80',
            'devotional',
            'ganesha',
            2,
            'Karthik Varma',
            'Telugu',
            '5:45',
            45600,
            3900,
            'Sep 15, 2026',
            'Start your morning with Lord Ganesha Pancharatnam for removal of obstacles and prosperous beginnings.',
            'ganesha, morning chants, vinayaka, bhakti, telugu devotional',
            0,
            0,
            ''
        ),
        (
            'sri-venkateswara-govinda-namalu',
            'Govinda Namalu | Lord Venkateswara Devotional Melodies',
            '2vjPBrBU-TM',
            'https://images.unsplash.com/photo-1545062990-4a95e8e4b96d?w=800&auto=format&fit=crop&q=80',
            'devotional',
            'venkateswara',
            1,
            'Ananya Sharma',
            'Telugu',
            '7:20',
            78900,
            6700,
            'Sep 08, 2026',
            'Govinda Hari Govinda Venkataramana Govinda - Soul-stirring Venkateswara Swamy devotional song.',
            'venkateswara, balaji, tirupati, govinda namalu, telugu devotional',
            0,
            0,
            ''
        ),

        # KIDS
        (
            'the-little-rabbit-adventure',
            'The Little Rabbit Adventure | Panchatantra Moral Story',
            'C0DPdy98e4c',
            'https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=800&auto=format&fit=crop&q=80',
            'kids',
            'moral stories',
            3,
            'Rahul Roy & The Storytoons',
            'Telugu',
            '6:40',
            67400,
            5400,
            'Oct 11, 2026',
            'Follow Benny the little rabbit on an exciting quest in the enchanted forest! Teaches children bravery, sharing, and kindness.',
            'kids cartoon, rabbit story, moral story, telugu kids, divinenest kids',
            1,
            1,
            '5–8 Years'
        ),
        (
            'chuchu-the-elephant-friend',
            'Chuchu the Elephant & The Magical River | Animated Tale',
            'dQw4w9WgXcQ',
            'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=800&auto=format&fit=crop&q=80',
            'kids',
            'cartoons',
            3,
            'Rahul Roy & The Storytoons',
            'Hindi',
            '8:15',
            53200,
            4120,
            'Oct 04, 2026',
            'An adorable animated journey of Chuchu the baby elephant who learns how true teamwork saves the jungle animals.',
            'kids cartoon, elephant story, animated, hindi kids, divinenest kids',
            1,
            1,
            '2–5 Years'
        ),
        (
            'nursery-rhymes-abc-phonics',
            'Fun ABC Phonics & Numbers Song | Kids Learning Melodies',
            '3JZ_D3ELwOQ',
            'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&auto=format&fit=crop&q=80',
            'kids',
            'rhymes',
            3,
            'Rahul Roy & The Storytoons',
            'English',
            '4:50',
            82100,
            6800,
            'Sep 25, 2026',
            'Sing along with colourful 3D characters to learn alphabet phonics and counting 1 to 20 in a joyful musical rhythm.',
            'nursery rhymes, abc song, phonics, kids learning, rhymes',
            1,
            0,
            '2–5 Years'
        ),
        (
            'little-krishna-butter-thief',
            'Little Krishna & The Butter Pot | Kids Animated Story',
            'fJ9rUzIMcZQ',
            'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=800&auto=format&fit=crop&q=80',
            'kids',
            'kids songs',
            3,
            'Rahul Roy & The Storytoons',
            'Telugu',
            '7:30',
            74500,
            5900,
            'Sep 14, 2026',
            'Playful Little Krishna and his friends embark on a fun adventure to taste Yashoda Maiyas sweet homemade butter.',
            'krishna cartoon, kids story, animated cartoon, telugu kids',
            0,
            0,
            '5–8 Years'
        ),

        # VIDEOS / ENTERTAINMENT
        (
            'behind-the-scenes-divinenest-music',
            'Behind The Scenes: How We Create Soulful Melodies',
            'OPf0YbXqDm0',
            'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=800&auto=format&fit=crop&q=80',
            'entertainment',
            'creative',
            1,
            'Ananya Sharma',
            'English',
            '8:50',
            32100,
            2700,
            'Oct 08, 2026',
            'Step into the DivineNest recording studio! Witness the live orchestration, lyric discussions, vocal warmups, and mixing magic.',
            'behind the scenes, studio, music production, entertainment, divinenest',
            1,
            0,
            ''
        ),
        (
            'inspiring-stories-of-faith',
            'Stories of Faith & Positivity | Episode 1',
            'L_LUpnjgPso',
            'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&auto=format&fit=crop&q=80',
            'entertainment',
            'inspirational',
            2,
            'Karthik Varma',
            'Telugu',
            '11:20',
            28900,
            2400,
            'Sep 29, 2026',
            'Inspirational narrative highlighting compassion, perseverance, and spiritual clarity during difficult seasons of life.',
            'inspiration, stories, motivation, spiritual, divinenest',
            0,
            0,
            ''
        ),

        # SHORTS (Vertical 9:16)
        (
            'divine-shiva-chant-short',
            'Om Namah Shivaya 15-Second Bliss #Shorts',
            'hY7m5jjJ9mM',
            'https://images.unsplash.com/photo-1545062990-4a95e8e4b96d?w=600&auto=format&fit=crop&q=80',
            'shorts',
            'devotional shorts',
            2,
            'Karthik Varma',
            'Sanskrit',
            '0:30',
            184000,
            16500,
            'Oct 14, 2026',
            'Feel the divine vibrations of Om Namah Shivaya in 30 seconds. Subscribe to DivineNest for daily peace.',
            'shorts, shiva, chants, reels, divinenest shorts',
            1,
            1,
            ''
        ),
        (
            'sweet-telugu-melody-snippet-short',
            'When the Flute Hits Your Heart #Shorts',
            'e3L1PIY1pN8',
            'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=600&auto=format&fit=crop&q=80',
            'shorts',
            'music shorts',
            4,
            'Sneha Menon',
            'Instrumental',
            '0:45',
            142000,
            12800,
            'Oct 13, 2026',
            'Pure soul in 45 seconds. Bansuri magic live from DivineNest Studio.',
            'shorts, flute, bansuri, music reels, divinenest',
            1,
            1,
            ''
        ),
        (
            'funny-bunny-laugh-short',
            'Benny Rabbit Laughs So Hard! #KidsShorts',
            'C0DPdy98e4c',
            'https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=600&auto=format&fit=crop&q=80',
            'shorts',
            'kids shorts',
            3,
            'Rahul Roy & The Storytoons',
            'Telugu',
            '0:25',
            95000,
            8100,
            'Oct 09, 2026',
            'Cute Benny Rabbit funny cartoon moments to make kids giggle with joy!',
            'kids shorts, funny cartoon, bunny, divinenest kids',
            1,
            1,
            '2–5 Years'
        ),
        (
            'studio-vocal-warmup-short',
            'Singer Warm Up Magic: Classical Notes to Pop #Shorts',
            'jfKfPfyJRdk',
            'https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=600&auto=format&fit=crop&q=80',
            'shorts',
            'behind the scenes',
            1,
            'Ananya Sharma',
            'Telugu',
            '0:50',
            67000,
            5900,
            'Sep 30, 2026',
            'Ananya Sharma shows how classical riyaaz warms up the voice for cinematic recording sessions.',
            'shorts, singer, vocal warm up, behind the scenes, divinenest',
            0,
            0,
            ''
        )
    ]

    cursor.executemany('''
    INSERT INTO videos (slug, title, youtube_id, thumbnail, category, subcategory, artist_id, artist_name, language, duration, views, likes, published_date, description, tags, is_featured, is_trending, age_group)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', videos_data)

    # Seed Music items
    music_data = [
        (
            'soulful-morning-melody',
            'Soulful Morning Melody',
            'Ananya Sharma',
            'Ananya Sharma',
            'K. R. Varma',
            'Sri Ram Murthy',
            'Telugu',
            'Original Music',
            'jfKfPfyJRdk',
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
            'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=80',
            '4:45',
            'Oct 12, 2026',
            1
        ),
        (
            'chandamama-love-melody',
            'Chandamama Love Melody',
            'Ananya Sharma',
            'Ananya Sharma & Rahul',
            'DivineNest Music',
            'Chandra Bose',
            'Telugu',
            'Love & Melody',
            'DWcJFNfaw9c',
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3',
            'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=600&auto=format&fit=crop&q=80',
            '3:58',
            'Oct 05, 2026',
            1
        ),
        (
            'bansuri-flute-serenity',
            'Bansuri Flute Serenity',
            'Sneha Menon',
            'Sneha Menon (Flute)',
            'Sneha Menon',
            'Traditional',
            'Instrumental',
            'Instrumental',
            'e3L1PIY1pN8',
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3',
            'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=600&auto=format&fit=crop&q=80',
            '10:15',
            'Sep 28, 2026',
            1
        ),
        (
            'raaga-symphony',
            'Raaga Symphony',
            'Ananya Sharma',
            'Ananya Sharma',
            'Pandit Hariprasad V.',
            'Sanskrit Hymns',
            'Hindi',
            'Classical & Traditional',
            '9bZkp7q19f0',
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3',
            'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&auto=format&fit=crop&q=80',
            '5:30',
            'Sep 18, 2026',
            0
        ),
        (
            'journey-of-hope-acoustic',
            'Journey of Hope',
            'Priya Sen',
            'Priya Sen',
            'David Lee & DivineNest',
            'Priya Sen',
            'English',
            'Trending Music',
            'kJQP7kiw5Fk',
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3',
            'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=600&auto=format&fit=crop&q=80',
            '3:45',
            'Sep 10, 2026',
            0
        )
    ]

    cursor.executemany('''
    INSERT INTO music (slug, title, artist_name, singer, composer, lyricist, language, genre, youtube_id, audio_url, thumbnail, duration, release_date, featured)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', music_data)

    # Seed Playlists
    playlists_data = [
        (
            'best-divine-melodies',
            'Best Music Collection 2026',
            'Our flagship compilation of romantic, soothing, and original melodies crafted by DivineNest artists.',
            'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=80',
            'Music',
            5,
            'PLmusic01',
            1
        ),
        (
            'morning-devotional-peace',
            'Morning Devotional Songs & Chants',
            'Sacred morning stotrams, Shiva chants, and Ganesha hymns to commence every day with inner peace.',
            'https://images.unsplash.com/photo-1545062990-4a95e8e4b96d?w=600&auto=format&fit=crop&q=80',
            'Devotional',
            6,
            'PLdevo01',
            1
        ),
        (
            'shiva-mahadev-chants',
            'Om Namah Shivaya & Shiva Bhajans',
            'Deeply transcendent chants and stotrams dedicated to Lord Shiva, the eternal yogi.',
            'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&auto=format&fit=crop&q=80',
            'Devotional',
            4,
            'PLshiva01',
            1
        ),
        (
            'kids-cartoons-moral-tales',
            'Kids Songs, Cartoons & Moral Stories',
            'Fun-filled animated stories, nursery rhymes, and educational entertainment for curious young minds.',
            'https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=600&auto=format&fit=crop&q=80',
            'Kids',
            8,
            'PLkids01',
            1
        ),
        (
            'trending-divinenest-shorts',
            'Trending Shorts & Quick Vibes',
            'The quickest and most engaging 30-second shorts: devotion, melodies, smiles, and inspiration.',
            'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=600&auto=format&fit=crop&q=80',
            'Shorts',
            10,
            'PLshorts01',
            1
        )
    ]

    cursor.executemany('''
    INSERT INTO playlists (slug, title, description, cover_image, category, video_count, youtube_playlist_id, featured)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', playlists_data)

    # Seed Blogs
    blogs_data = [
        (
            'top-devotional-songs-for-peaceful-morning',
            'Top Devotional Songs for a Peaceful Morning',
            'Devotional',
            'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&auto=format&fit=crop&q=80',
            'Discover how waking up to soulful chants, Ganesha stotrams, and Suprabhatam calms nervous energy and sets an auspicious tone for your entire day.',
            '''<h3>The Power of Sacred Morning Sounds</h3>
<p>In Indian tradition, the early morning hours known as <em>Brahma Muhurta</em> (roughly 90 minutes before sunrise) hold the purest cosmic energy. During this time, the surrounding world is quiet, our conscious thoughts are still untangled, and our mind is most receptive to spiritual vibrations.</p>

<p>Listening to sacred mantras like the <strong>Maha Mrityunjaya Mantra</strong>, <strong>Gayatri Mantra</strong>, or the melodious <strong>Govinda Namalu</strong> acts like an acoustic purification for the mind and soul.</p>

<h3>Recommended Morning Devotional Routine</h3>
<ul>
    <li><strong>6:00 AM:</strong> Begin with Sri Ganesha Pancharatnam to invite clarity and remove obstacles.</li>
    <li><strong>6:15 AM:</strong> Chant or listen to Lord Shiva Maha Mrityunjaya Mantra for protection and health.</li>
    <li><strong>6:30 AM:</strong> Immerse in Achyutam Keshavam or Krishna Bhajans for joyful gratitude.</li>
</ul>

<p>At <strong>DivineNest</strong>, we produce our devotional audio with pure acoustic resonance and crystal clear Sanskrit pronunciation, ensuring your home resonates with peace and positivity.</p>''',
            'Karthik Varma',
            'Oct 14, 2026',
            '6 min read',
            'devotional, morning routine, mantras, shiva, krishna',
            'H5v3kku4y6Q'
        ),
        (
            'nursery-rhymes-and-child-brain-development',
            'How Nursery Rhymes & Stories Shape Child Brain Development',
            'Kids',
            'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&auto=format&fit=crop&q=80',
            'Explore the science behind melodic repetition, moral storytelling, and animated engagement in early childhood literacy and emotional intelligence.',
            '''<h3>Why Rhymes Matter More Than Ever</h3>
<p>Modern neuroscience shows that rhythmic speech and musical patterns accelerate language acquisition in toddlers and preschoolers. When children hear repeating rhymes paired with colorful animation, their brains form neural pathways connecting phonics, spatial awareness, and vocabulary.</p>

<h3>The 3 Pillars of DivineNest Kids Content</h3>
<ol>
    <li><strong>Moral Anchors:</strong> Every story highlights timeless virtues like honesty, kindness to animals, and respecting elders.</li>
    <li><strong>Wholesome Visuals:</strong> We intentionally avoid over-stimulating rapid flashing lights, opting for soft, delightful pastel tones that spark creativity rather than stress.</li>
    <li><strong>Active Participation:</strong> Rhymes with easy hand movements and sing-along lyrics encourage physical coordination and joyful memory retention.</li>
</ol>''',
            'Rahul Roy',
            'Oct 08, 2026',
            '5 min read',
            'kids, education, parenting, rhymes, stories',
            'C0DPdy98e4c'
        ),
        (
            'the-magic-of-indian-melodies-across-generations',
            'The Magic of Indian Melodies: Blending Tradition with Modern Soul',
            'Music',
            'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80',
            'How DivineNest blends acoustic guitars, flute, and Indian ragas to create family-friendly music that connects grandparents and grandkids alike.',
            '''<h3>Bridging the Generational Sound Gap</h3>
<p>Music is the universal language of emotion. Yet, modern commercial music often alienates older family members with aggressive beats, while classical concerts can sometimes feel inaccessible to young children.</p>

<p>At <strong>DivineNest Music</strong>, our vision was simple: What if a song could be enjoyed together in the living room by grandparents, parents, and children with equal love and reverence?</p>

<p>By blending the acoustic warmth of nylon string guitars with the ethereal sweetness of the Indian bansuri and heartfelt lyrical poetry, we create songs that stay in your heart for years.</p>''',
            'Ananya Sharma',
            'Sep 27, 2026',
            '4 min read',
            'music, indian melody, classical fusion, acoustic, divinenest',
            'jfKfPfyJRdk'
        )
    ]

    cursor.executemany('''
    INSERT INTO blogs (slug, title, category, featured_image, summary, content, author, published_date, read_time, tags, youtube_video_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', blogs_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    seed_db()
    print("DivineNest Database initialized and seeded successfully!")
