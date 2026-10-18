# 🪹 DivineNest — "Where Music, Stories & Joy Come Together"

**DivineNest** is a modern, high-performance web platform built with Python (Flask), SQLite, Vanilla HTML5, modern CSS3, and JavaScript, designed for YouTube video creators, musical artists, and family audiences.

---

## 🌟 Brand Ecosystem & Highlights

1. **🎵 Music**: Original compositions, love melodies, acoustic tracks, classical raga fusions, and instrumental bansuri/flute serenity.
2. **🙏 Devotional**: Soul-stirring Shiva stotrams, Krishna bhajans, Rama chants, Hanuman Chalisa, Venkateswara Govinda Namalu, and morning/evening mantras.
3. **🧒 Kids**: Fun, safe, and wholesome animated cartoons, Panchatantra moral stories, sing-along nursery rhymes, and preschool learning videos with age filters (2–5 yrs, 5–8 yrs).
4. **🎬 Videos**: Master cinematic library with category filters, language options, sorting (Latest, Popular, A–Z), and responsive 16:9 YouTube video player.
5. **⚡ Shorts**: 9:16 vertical short-form video cards for quick devotion, musical snippets, and cheerful smiles.
6. **🎤 Artists**: Profiles of vocalists, flautists, composers, animators, and creators with biographies, social links, and works.
7. **📂 Playlists**: Curated collections for continuous playback and YouTube sync.
8. **📰 Blog**: SEO-optimized editorial articles on morning devotion routines, child development, and music production.
9. **🤝 Collaboration & Music Submissions**: Interactive portals for creators, brands, and independent musicians.
10. **🔐 Admin Dashboard**: Content control center for managing videos, audio tracks, monitoring visitor inquiries, and reviewing artist submissions.

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+ (or run via the provided `uv` environment)
- Dependencies: `Flask`

### 2. Launching the Platform
Run the launcher batch file or start via command prompt:
```bash
# Option A: Double click run.bat
run.bat

# Option B: Run manually in PowerShell / Terminal
.\.venv\Scripts\python.exe app.py
```

### 3. Open in Browser
- **Main Website**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Admin Dashboard**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)
  - **Username**: `admin`
  - **Password**: `divinenest2026`

---

## 📂 Project Architecture

```
c:\DIVINE NEST WEBSITE\
├── app.py                  # Core Flask server, routing, API endpoints & SEO routes
├── database.py             # SQLite models, schema setup & seed data generator
├── divinenest.db           # SQLite database
├── requirements.txt        # Python dependencies
├── run.bat                 # One-click Windows starter script
├── static/
│   ├── css/
│   │   ├── style.css       # Master stylesheet (dark/light, glassmorphism, responsive)
│   │   ├── kids.css        # Playful theme styling for DivineNest Kids
│   │   └── admin.css       # Admin dashboard styles & tables
│   └── js/
│       ├── main.js         # Audio player, YouTube modal, AJAX forms, likes & share
│       └── admin.js        # Admin tab switching and live table search
└── templates/
    ├── base.html           # Master layout with nav, sticky audio player & mobile bar
    ├── index.html          # Complete homepage (15 ordered sections)
    ├── music.html          # Music catalog & playable tracks
    ├── devotional.html     # Devotional sanctuary & deity tabs
    ├── kids.html           # Kids cartoons & rhymes
    ├── shorts.html         # Vertical 9:16 shorts feed
    ├── videos.html         # Full video library with search & filter
    ├── video_detail.html   # Individual video player & related items
    ├── artists.html        # Artists directory
    ├── artist_detail.html  # Artist biography & featured songs
    ├── playlists.html      # Curated playlist collections
    ├── playlist_detail.html# Playlist tracklist view
    ├── blog.html           # Blog articles index
    ├── blog_detail.html    # Full article with reading time & video embed
    ├── about.html          # About Us, Vision, Mission, Why DivineNest
    ├── contact.html        # Contact Us form & official channels
    ├── collaborate.html    # Creator & brand partnership portal
    ├── submit_music.html   # Independent musician submission portal
    ├── search.html         # Unified multi-category search engine
    ├── legal.html          # Privacy Policy, Terms, Copyright & Disclaimer
    ├── 404.html            # Custom "Oops! This Nest Is Empty 🪹" page
    └── admin.html          # Complete Admin panel & inboxes
```

---

## 🔍 Key Interactive Features

- **Embedded YouTube Player**: Fast, responsive 16:9 video playback that loads YouTube videos seamlessly on any device.
- **Instant Video Modal**: Preview any video or short without losing your place on the page.
- **Docked Audio Mini-Player**: Listen to music audio samples with live progress seek bar, play/pause controls, and time display.
- **Mobile-First Bottom Navigation**: Dedicated mobile bottom bar `[ Home | Music | Videos | Shorts | YouTube ]` for seamless phone browsing.
- **Live Video Likes**: Interactive heart button with live counter and local persistence.
- **Native Share & Clipboard Copy**: One-tap sharing with toast notifications.
- **Multilingual Ready**: Language switcher supporting Telugu, Hindi, and English.
- **Search Engine Optimization**: Automatically generated `/sitemap.xml`, `/robots.txt`, Open Graph metadata, and JSON-LD VideoObject & Article schema markup.
