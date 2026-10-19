/**
 * DIVINENEST — MAIN CLIENT-SIDE INTERACTIVITY
 * Audio Player, Video Modal, AJAX Forms, Likes, Favorites & Share
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initVideoModal();
  initAudioPlayer();
  initFavoritesAndHistory();
  initSavedModal();
  initLikeButtons();
  initShareButtons();
  initSearchFilters();
  initAjaxForms();
  initLanguageSwitcher();
  initEntryAnimation();
  renderContinueListeningShelf();
});

// Toast notification helper
function showToast(message, type = 'success') {
  const existing = document.querySelector('.toast-msg');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast-msg';
  const icon = type === 'error' ? '⚠️' : '✨';
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// 1. Mobile App Slide-Out Drawer Navigation
function initMobileMenu() {
  const menuBtn = document.getElementById('mobileMenuBtn') || document.querySelector('.mobile-menu-btn');
  const drawerOverlay = document.getElementById('mobileDrawerOverlay');
  const drawerClose = document.getElementById('mobileDrawerClose');
  const drawerLinks = document.querySelectorAll('.mobile-drawer .drawer-link');

  if (!drawerOverlay) return;

  const openDrawer = () => {
    drawerOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  };

  const closeDrawer = () => {
    drawerOverlay.classList.remove('active');
    document.body.style.overflow = '';
  };

  if (menuBtn) {
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openDrawer();
    });
  }

  if (drawerClose) {
    drawerClose.addEventListener('click', closeDrawer);
  }

  drawerOverlay.addEventListener('click', (e) => {
    if (e.target === drawerOverlay) {
      closeDrawer();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawerOverlay.classList.contains('active')) {
      closeDrawer();
    }
  });

  drawerLinks.forEach(link => {
    link.addEventListener('click', closeDrawer);
  });
}

// 2. YouTube Video Modal
function initVideoModal() {
  const modalBackdrop = document.getElementById('videoModal');
  const modalIframe = document.getElementById('modalVideoIframe');
  const modalTitle = document.getElementById('modalVideoTitle');
  const modalClose = document.getElementById('modalCloseBtn');

  if (!modalBackdrop) return;

  // Open modal triggers
  document.querySelectorAll('[data-youtube-id]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      // Don't trigger if clicking explicit direct page link
      if (e.target.closest('a') && !e.target.closest('[data-modal-play]')) return;

      e.preventDefault();
      const ytId = trigger.dataset.youtubeId;
      const title = trigger.dataset.videoTitle || 'DivineNest Video';

      if (ytId && modalIframe) {
        modalIframe.src = `https://www.youtube.com/embed/${ytId}?autoplay=1&rel=0`;
        if (modalTitle) modalTitle.textContent = title;
        modalBackdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    });
  });

  const closeModal = () => {
    modalBackdrop.classList.remove('active');
    if (modalIframe) modalIframe.src = '';
    document.body.style.overflow = '';
  };

  if (modalClose) modalClose.addEventListener('click', closeModal);
  modalBackdrop.addEventListener('click', (e) => {
    if (e.target === modalBackdrop) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalBackdrop.classList.contains('active')) {
      closeModal();
    }
  });
}

// 3. Advanced Audio Engine & Persistent Mini-Player Bar
let audioObj = null;
let musicQueue = [];
let currentTrackIdx = 0;
let isShuffle = false;
let repeatMode = 'off'; // 'off' | 'all' | 'one'
let lastVolume = 1;

// LocalStorage Keys
const FAV_KEY = 'divinenest_favorites';
const HIST_KEY = 'divinenest_history';

function getFavoritesList() {
  try {
    return JSON.parse(localStorage.getItem(FAV_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function saveFavoritesList(favs) {
  localStorage.setItem(FAV_KEY, JSON.stringify(favs));
  updateFavoritesUI();
}

function getHistoryList() {
  try {
    return JSON.parse(localStorage.getItem(HIST_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function recordListeningHistory(track) {
  if (!track || !track.title) return;
  let hist = getHistoryList();
  // Remove duplicates to keep fresh
  hist = hist.filter(h => h.title !== track.title);
  hist.unshift({
    title: track.title,
    artist: track.artist || 'DivineNest Music',
    thumb: track.thumb || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=200',
    url: track.url,
    ytId: track.ytId || '',
    playedAt: Date.now()
  });
  if (hist.length > 20) hist = hist.slice(0, 20);
  localStorage.setItem(HIST_KEY, JSON.stringify(hist));
  updateHistoryCount();
  renderContinueListeningShelf();
}

function toggleFavoriteItem(item) {
  let favs = getFavoritesList();
  const existsIdx = favs.findIndex(f => f.id === item.id || f.title === item.title);
  if (existsIdx !== -1) {
    favs.splice(existsIdx, 1);
    saveFavoritesList(favs);
    showToast(`Removed "${item.title}" from favourites`);
  } else {
    favs.unshift(item);
    saveFavoritesList(favs);
    showToast(`Saved "${item.title}" to favourites! ❤️`);
  }
  syncFavoriteButtons();
}

function updateFavoritesUI() {
  const favs = getFavoritesList();
  const badge = document.getElementById('headerSavedBadge');
  const pill = document.getElementById('favCountPill');
  if (badge) {
    badge.textContent = favs.length;
    badge.style.display = favs.length > 0 ? 'inline-block' : 'none';
  }
  if (pill) pill.textContent = favs.length;
  renderSavedModalFavorites();
}

function updateHistoryCount() {
  const hist = getHistoryList();
  const pill = document.getElementById('historyCountPill');
  const bar = document.getElementById('historyActionsBar');
  if (pill) pill.textContent = hist.length;
  if (bar) bar.style.display = hist.length > 0 ? 'flex' : 'none';
  renderSavedModalHistory();
}

function syncFavoriteButtons() {
  const favs = getFavoritesList();
  document.querySelectorAll('.btn-favorite-toggle').forEach(btn => {
    const id = btn.dataset.id;
    const title = btn.dataset.title;
    const isFav = favs.some(f => (id && f.id === id) || (title && f.title === title));
    btn.classList.toggle('favorited', isFav);
    const icon = btn.querySelector('.fav-icon');
    if (icon) icon.textContent = isFav ? '❤️' : '🤍';
    const text = btn.querySelector('.fav-text');
    if (text) text.textContent = isFav ? 'Saved' : 'Favourite';
  });

  const playerHeart = document.getElementById('playerHeartBtn');
  if (playerHeart && musicQueue[currentTrackIdx]) {
    const cur = musicQueue[currentTrackIdx];
    const isFav = favs.some(f => f.url === cur.url || f.title === cur.title);
    playerHeart.innerHTML = isFav ? '❤️' : '🤍';
    playerHeart.classList.toggle('favorited', isFav);
  }
}

function initAudioPlayer() {
  const playerBar = document.getElementById('audioPlayerBar');
  if (!playerBar) return;

  const playBtn = document.getElementById('playerPlayBtn');
  const prevBtn = document.getElementById('playerPrevBtn');
  const nextBtn = document.getElementById('playerNextBtn');
  const shuffleBtn = document.getElementById('playerShuffleBtn');
  const repeatBtn = document.getElementById('playerRepeatBtn');
  const heartBtn = document.getElementById('playerHeartBtn');
  const titleEl = document.getElementById('playerSongTitle');
  const artistEl = document.getElementById('playerSongArtist');
  const thumbEl = document.getElementById('playerSongThumb');
  const progressFill = document.getElementById('playerProgressFill');
  const progressBar = document.getElementById('playerProgressBar');
  const timeCurrent = document.getElementById('playerCurrentTime');
  const timeDuration = document.getElementById('playerDuration');
  const volumeSlider = document.getElementById('playerVolumeSlider');
  const muteBtn = document.getElementById('playerMuteBtn');
  const ytSyncBtn = document.getElementById('playerYtSyncBtn');
  const closeBtn = document.getElementById('playerCloseBtn');

  if (!audioObj) {
    audioObj = new Audio();
  }

  // Build audio queue from page or fallback
  function buildQueueFromDom() {
    const triggers = document.querySelectorAll('[data-audio-url]');
    musicQueue = [];
    triggers.forEach(btn => {
      musicQueue.push({
        url: btn.dataset.audioUrl,
        title: btn.dataset.title || 'Soulful Melody',
        artist: btn.dataset.artist || 'DivineNest Music',
        thumb: btn.dataset.thumb || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=200',
        ytId: btn.dataset.youtubeId || ''
      });
    });

    if (musicQueue.length === 0) {
      musicQueue = [
        {
          url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
          title: 'Achyutam Keshavam Krishna Bhajan',
          artist: 'Ananya Sharma',
          thumb: 'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=200',
          ytId: '1ZYbU88VHWY'
        },
        {
          url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3',
          title: 'Govinda Namalu | Lord Venkateswara',
          artist: 'Ananya Sharma',
          thumb: 'https://images.unsplash.com/photo-1609766857041-ed402ea8069a?w=200',
          ytId: '2vjPBrBU-TM'
        },
        {
          url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3',
          title: 'Maha Mrityunjaya Mantra 108 Times',
          artist: 'Karthik Varma',
          thumb: 'https://images.unsplash.com/photo-1621847468516-1ed5d0df56fe?w=200',
          ytId: 'H5v3kku4y6Q'
        }
      ];
    }
  }

  buildQueueFromDom();

  window.playTrack = function(index) {
    if (musicQueue.length === 0) buildQueueFromDom();
    if (index < 0) index = 0;
    if (index >= musicQueue.length) index = 0;
    currentTrackIdx = index;
    const track = musicQueue[currentTrackIdx];
    if (!track || !track.url) return;

    if (audioObj.src !== track.url) {
      audioObj.src = track.url;
    }

    if (titleEl) titleEl.textContent = track.title;
    if (artistEl) artistEl.textContent = track.artist;
    if (thumbEl) thumbEl.src = track.thumb;

    if (ytSyncBtn) {
      if (track.ytId) {
        ytSyncBtn.style.display = 'inline-block';
        ytSyncBtn.onclick = (e) => {
          e.preventDefault();
          const modalBackdrop = document.getElementById('videoModal');
          const modalIframe = document.getElementById('modalVideoIframe');
          const modalTitle = document.getElementById('modalVideoTitle');
          if (modalBackdrop && modalIframe) {
            audioObj.pause();
            if (playBtn) playBtn.innerHTML = '▶';
            modalIframe.src = `https://www.youtube.com/embed/${track.ytId}?autoplay=1&rel=0`;
            if (modalTitle) modalTitle.textContent = track.title;
            modalBackdrop.classList.add('active');
            document.body.style.overflow = 'hidden';
          }
        };
      } else {
        ytSyncBtn.style.display = 'none';
      }
    }

    syncFavoriteButtons();

    playerBar.classList.add('active');
    document.body.classList.add('has-active-player');

    audioObj.play().then(() => {
      if (playBtn) playBtn.innerHTML = '⏸';
      recordListeningHistory(track);
    }).catch(err => {
      console.warn('Playback error / auto-play restriction:', err);
    });
  };

  // Wire trigger buttons
  document.querySelectorAll('[data-audio-url]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const url = btn.dataset.audioUrl;
      const foundIdx = musicQueue.findIndex(t => t.url === url);
      if (foundIdx !== -1) {
        playTrack(foundIdx);
      } else {
        musicQueue.unshift({
          url: url,
          title: btn.dataset.title || 'Divine Melody',
          artist: btn.dataset.artist || 'DivineNest Music',
          thumb: btn.dataset.thumb || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=200',
          ytId: btn.dataset.youtubeId || ''
        });
        playTrack(0);
      }
    });
  });

  // Play / Pause Toggle
  if (playBtn) {
    playBtn.addEventListener('click', () => {
      if (audioObj.paused) {
        audioObj.play().then(() => {
          playBtn.innerHTML = '⏸';
        }).catch(() => {});
      } else {
        audioObj.pause();
        playBtn.innerHTML = '▶';
      }
    });
  }

  // Next Track
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (musicQueue.length <= 1) {
        audioObj.currentTime = 0;
        audioObj.play();
        return;
      }
      if (isShuffle) {
        let randIdx = Math.floor(Math.random() * musicQueue.length);
        if (randIdx === currentTrackIdx && musicQueue.length > 1) {
          randIdx = (randIdx + 1) % musicQueue.length;
        }
        playTrack(randIdx);
      } else {
        playTrack((currentTrackIdx + 1) % musicQueue.length);
      }
    });
  }

  // Previous Track
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (audioObj.currentTime > 3) {
        audioObj.currentTime = 0;
        return;
      }
      const prevIdx = (currentTrackIdx - 1 + musicQueue.length) % musicQueue.length;
      playTrack(prevIdx);
    });
  }

  // Shuffle Button
  if (shuffleBtn) {
    shuffleBtn.addEventListener('click', () => {
      isShuffle = !isShuffle;
      shuffleBtn.classList.toggle('active', isShuffle);
      shuffleBtn.title = isShuffle ? 'Shuffle (On)' : 'Shuffle (Off)';
      showToast(isShuffle ? 'Shuffle enabled 🔀' : 'Shuffle disabled');
    });
  }

  // Repeat Button
  if (repeatBtn) {
    repeatBtn.addEventListener('click', () => {
      if (repeatMode === 'off') {
        repeatMode = 'all';
        repeatBtn.classList.add('active');
        repeatBtn.innerHTML = '🔁';
        repeatBtn.title = 'Repeat (All)';
        showToast('Repeat all tracks 🔁');
      } else if (repeatMode === 'all') {
        repeatMode = 'one';
        repeatBtn.classList.add('active');
        repeatBtn.innerHTML = '🔂';
        repeatBtn.title = 'Repeat (Current Track)';
        showToast('Repeat current track 🔂');
      } else {
        repeatMode = 'off';
        repeatBtn.classList.remove('active');
        repeatBtn.innerHTML = '🔁';
        repeatBtn.title = 'Repeat (Off)';
        showToast('Repeat off');
      }
    });
  }

  // Track Ended Handler
  audioObj.addEventListener('ended', () => {
    if (repeatMode === 'one') {
      audioObj.currentTime = 0;
      audioObj.play();
    } else if (repeatMode === 'all' || musicQueue.length > 1) {
      if (isShuffle) {
        const randIdx = Math.floor(Math.random() * musicQueue.length);
        playTrack(randIdx);
      } else {
        playTrack((currentTrackIdx + 1) % musicQueue.length);
      }
    } else {
      if (playBtn) playBtn.innerHTML = '▶';
    }
  });

  // Time & Progress Update
  audioObj.addEventListener('timeupdate', () => {
    if (audioObj.duration) {
      const pct = (audioObj.currentTime / audioObj.duration) * 100;
      if (progressFill) progressFill.style.width = `${pct}%`;
      if (timeCurrent) timeCurrent.textContent = formatTime(audioObj.currentTime);
      if (timeDuration) timeDuration.textContent = formatTime(audioObj.duration);
    }
  });

  // Seekbar click / scrub
  if (progressBar) {
    progressBar.addEventListener('click', (e) => {
      const rect = progressBar.getBoundingClientRect();
      const clickX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
      const pct = clickX / rect.width;
      if (audioObj.duration) {
        audioObj.currentTime = pct * audioObj.duration;
      }
    });
  }

  // Volume & Mute Controls
  if (volumeSlider) {
    volumeSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      audioObj.volume = val;
      if (muteBtn) {
        muteBtn.innerHTML = val === 0 ? '🔇' : (val < 0.5 ? '🔉' : '🔊');
      }
    });
  }

  if (muteBtn) {
    muteBtn.addEventListener('click', () => {
      if (audioObj.volume > 0) {
        lastVolume = audioObj.volume;
        audioObj.volume = 0;
        if (volumeSlider) volumeSlider.value = 0;
        muteBtn.innerHTML = '🔇';
      } else {
        audioObj.volume = lastVolume || 1;
        if (volumeSlider) volumeSlider.value = audioObj.volume;
        muteBtn.innerHTML = '🔊';
      }
    });
  }

  // Heart toggle on player
  if (heartBtn) {
    heartBtn.addEventListener('click', () => {
      const track = musicQueue[currentTrackIdx];
      if (track) {
        toggleFavoriteItem({
          id: track.url,
          title: track.title,
          artist: track.artist,
          thumb: track.thumb,
          url: track.url,
          type: 'music'
        });
      }
    });
  }

  // Close player
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      audioObj.pause();
      playerBar.classList.remove('active');
      document.body.classList.remove('has-active-player');
      if (playBtn) playBtn.innerHTML = '▶';
    });
  }
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60) || 0;
  const secs = Math.floor(seconds % 60) || 0;
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// 4. Favorites & History Manager
function initFavoritesAndHistory() {
  document.querySelectorAll('.btn-favorite-toggle').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleFavoriteItem({
        id: btn.dataset.id || btn.dataset.title,
        title: btn.dataset.title,
        artist: btn.dataset.artist || 'DivineNest',
        thumb: btn.dataset.thumb || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=200',
        url: btn.dataset.url || '',
        type: btn.dataset.type || 'video'
      });
    });
  });

  updateFavoritesUI();
  updateHistoryCount();
  syncFavoriteButtons();
}

// 5. Saved Favourites & History Modal
function initSavedModal() {
  const modal = document.getElementById('savedModal');
  if (!modal) return;

  const headerBtn = document.getElementById('headerSavedBtn');
  const mobileBtn = document.getElementById('mobileSavedBtn');
  const closeBtn = document.getElementById('savedModalCloseBtn');
  const tabFavBtn = document.getElementById('tabFavoritesBtn');
  const tabHistBtn = document.getElementById('tabHistoryBtn');
  const favPane = document.getElementById('favoritesTab');
  const histPane = document.getElementById('historyTab');
  const clearHistBtn = document.getElementById('clearHistoryBtn');
  const clearHomeHistBtn = document.getElementById('clearHomeHistoryBtn');

  const openModal = (tab = 'favorites') => {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    if (tab === 'history') {
      tabHistBtn.click();
    } else {
      tabFavBtn.click();
    }
  };

  const closeModal = () => {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  };

  if (headerBtn) headerBtn.addEventListener('click', () => openModal('favorites'));
  if (mobileBtn) mobileBtn.addEventListener('click', () => openModal('favorites'));
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) closeModal();
  });

  if (tabFavBtn && tabHistBtn) {
    tabFavBtn.addEventListener('click', () => {
      tabFavBtn.classList.add('active');
      tabHistBtn.classList.remove('active');
      if (favPane) favPane.classList.add('active');
      if (histPane) histPane.classList.remove('active');
      renderSavedModalFavorites();
    });

    tabHistBtn.addEventListener('click', () => {
      tabHistBtn.classList.add('active');
      tabFavBtn.classList.remove('active');
      if (histPane) histPane.classList.add('active');
      if (favPane) favPane.classList.remove('active');
      renderSavedModalHistory();
    });
  }

  const handleClearHistory = () => {
    localStorage.removeItem(HIST_KEY);
    updateHistoryCount();
    renderContinueListeningShelf();
    showToast('Listening history cleared');
  };

  if (clearHistBtn) clearHistBtn.addEventListener('click', handleClearHistory);
  if (clearHomeHistBtn) clearHomeHistBtn.addEventListener('click', handleClearHistory);
}

function renderSavedModalFavorites() {
  const container = document.getElementById('favoritesList');
  const emptyState = document.getElementById('favoritesEmptyState');
  if (!container) return;
  const favs = getFavoritesList();

  if (favs.length === 0) {
    if (emptyState) emptyState.style.display = 'block';
    container.innerHTML = '';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';
  container.innerHTML = favs.map((f, i) => `
    <div class="saved-item-row">
      <img src="${f.thumb}" alt="${f.title}" class="saved-item-thumb">
      <div class="saved-item-meta">
        <div class="saved-item-title">${f.title}</div>
        <div class="saved-item-sub">${f.artist}</div>
      </div>
      <div class="saved-item-actions">
        <button type="button" class="saved-item-play-btn" onclick="playSavedTrack(${i})" title="Play">▶</button>
        <button type="button" class="saved-item-del-btn" onclick="removeFavoriteByIndex(${i})" title="Remove">✕</button>
      </div>
    </div>
  `).join('');
}

window.removeFavoriteByIndex = function(idx) {
  const favs = getFavoritesList();
  if (idx >= 0 && idx < favs.length) {
    const item = favs[idx];
    favs.splice(idx, 1);
    saveFavoritesList(favs);
    syncFavoriteButtons();
    showToast(`Removed "${item.title}"`);
  }
};

window.playSavedTrack = function(idx) {
  const favs = getFavoritesList();
  const item = favs[idx];
  if (!item) return;

  const modal = document.getElementById('savedModal');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = '';

  if (item.url && item.url.includes('.mp3')) {
    musicQueue.unshift({
      url: item.url,
      title: item.title,
      artist: item.artist,
      thumb: item.thumb,
      ytId: item.ytId || ''
    });
    playTrack(0);
  } else if (item.url) {
    window.location.href = item.url;
  }
};

function renderSavedModalHistory() {
  const container = document.getElementById('historyList');
  const emptyState = document.getElementById('historyEmptyState');
  if (!container) return;
  const hist = getHistoryList();

  if (hist.length === 0) {
    if (emptyState) emptyState.style.display = 'block';
    container.innerHTML = '';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';
  container.innerHTML = hist.map((h, i) => `
    <div class="saved-item-row">
      <img src="${h.thumb}" alt="${h.title}" class="saved-item-thumb">
      <div class="saved-item-meta">
        <div class="saved-item-title">${h.title}</div>
        <div class="saved-item-sub">${h.artist}</div>
      </div>
      <div class="saved-item-actions">
        <button type="button" class="saved-item-play-btn" onclick="playHistoryTrack(${i})" title="Resume">▶</button>
      </div>
    </div>
  `).join('');
}

window.playHistoryTrack = function(idx) {
  const hist = getHistoryList();
  const item = hist[idx];
  if (!item) return;

  const modal = document.getElementById('savedModal');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = '';

  if (item.url && item.url.includes('.mp3')) {
    musicQueue.unshift({
      url: item.url,
      title: item.title,
      artist: item.artist,
      thumb: item.thumb,
      ytId: item.ytId || ''
    });
    playTrack(0);
  } else if (item.ytId) {
    const modalBackdrop = document.getElementById('videoModal');
    const modalIframe = document.getElementById('modalVideoIframe');
    const modalTitle = document.getElementById('modalVideoTitle');
    if (modalBackdrop && modalIframe) {
      modalIframe.src = `https://www.youtube.com/embed/${item.ytId}?autoplay=1&rel=0`;
      if (modalTitle) modalTitle.textContent = item.title;
      modalBackdrop.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }
};

function renderContinueListeningShelf() {
  const section = document.getElementById('continueListeningSection');
  const grid = document.getElementById('continueListeningGrid');
  if (!section || !grid) return;

  const hist = getHistoryList();
  if (hist.length === 0) {
    section.style.display = 'none';
    return;
  }

  section.style.display = 'block';
  const displayItems = hist.slice(0, 4);
  grid.innerHTML = displayItems.map((item, idx) => `
    <div class="continue-card">
      <div class="continue-thumb-wrap" onclick="playHistoryTrack(${idx})">
        <img src="${item.thumb}" alt="${item.title}" loading="lazy">
        <div class="play-hover-overlay" style="opacity:1; background:rgba(0,0,0,0.35);">
          <div class="play-hover-btn" style="width:40px; height:40px; font-size:1rem;">▶</div>
        </div>
        <div class="continue-progress-indicator">
          <div class="continue-progress-bar-fill" style="width: ${50 + (idx * 15) % 45}%;"></div>
        </div>
      </div>
      <div class="continue-card-body">
        <div class="continue-card-title">${item.title}</div>
        <div class="continue-card-meta">
          <span>${item.artist}</span>
          <span style="color:#10B981; font-weight:700;">Resume ▶</span>
        </div>
      </div>
    </div>
  `).join('');
}

// 6. Video Likes Handler
function initLikeButtons() {
  document.querySelectorAll('.btn-like').forEach(btn => {
    const videoId = btn.dataset.videoId;
    const likedKey = `divinenest_liked_${videoId}`;

    if (localStorage.getItem(likedKey)) {
      btn.classList.add('liked');
      btn.style.color = '#FF006E';
    }

    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      if (localStorage.getItem(likedKey)) {
        showToast('You already liked this video! ❤️');
        return;
      }

      try {
        const res = await fetch(`/api/videos/${videoId}/like`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          localStorage.setItem(likedKey, 'true');
          btn.classList.add('liked');
          btn.style.color = '#FF006E';
          const countSpan = btn.querySelector('.like-count');
          if (countSpan) countSpan.textContent = data.likes.toLocaleString();
          showToast('Thank you for liking! ❤️');
        }
      } catch (err) {
        console.error('Like error:', err);
      }
    });
  });
}

// 7. Social Share Modal & Direct Link Handler
function initShareButtons() {
  const shareModal = document.getElementById('shareModal');
  const closeBtn = document.getElementById('shareModalCloseBtn');
  const whatsAppBtn = document.getElementById('shareWhatsAppBtn');
  const twitterBtn = document.getElementById('shareTwitterBtn');
  const facebookBtn = document.getElementById('shareFacebookBtn');
  const linkInput = document.getElementById('shareLinkInput');
  const copyBtn = document.getElementById('copyShareLinkBtn');

  const openShareModal = (title, url) => {
    if (!shareModal) return;
    const shareUrl = url || window.location.href;
    const shareTitle = title || document.title || 'DivineNest Music & Stories';

    if (linkInput) linkInput.value = shareUrl;
    if (whatsAppBtn) {
      whatsAppBtn.href = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareTitle + '\n' + shareUrl)}`;
    }
    if (twitterBtn) {
      twitterBtn.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent('Enjoying this melody on DivineNest ✨ ' + shareTitle)}&url=${encodeURIComponent(shareUrl)}`;
    }
    if (facebookBtn) {
      facebookBtn.href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
    }

    shareModal.classList.add('active');
    document.body.style.overflow = 'hidden';
  };

  const closeShareModal = () => {
    if (shareModal) shareModal.classList.remove('active');
    document.body.style.overflow = '';
  };

  document.querySelectorAll('.btn-share').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const title = btn.dataset.title || document.title;
      const url = btn.dataset.url || window.location.href;

      if (navigator.share && window.innerWidth < 768) {
        navigator.share({
          title: title,
          text: 'Enjoy this soulful melody on DivineNest ✨',
          url: url
        }).catch(() => {});
      } else {
        openShareModal(title, url);
      }
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeShareModal);
  if (shareModal) {
    shareModal.addEventListener('click', (e) => {
      if (e.target === shareModal) closeShareModal();
    });
  }

  if (copyBtn && linkInput) {
    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(linkInput.value).then(() => {
        const origText = copyBtn.textContent;
        copyBtn.textContent = 'Copied! ✨';
        copyBtn.style.background = '#10B981';
        showToast('Link copied to clipboard! 🔗');
        setTimeout(() => {
          copyBtn.textContent = origText;
          copyBtn.style.background = '';
        }, 2000);
      }).catch(() => {
        showToast('Direct link ready to copy!');
      });
    });
  }
}

// 8. Search Filter Pills (Instant Client-Side Filtering)
function initSearchFilters() {
  const filterPills = document.querySelectorAll('#searchFilterPills .filter-pill');
  if (filterPills.length === 0) return;

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      const filter = pill.dataset.filter.toLowerCase();
      const cards = document.querySelectorAll('.search-item-card');
      let visibleCount = 0;

      cards.forEach(card => {
        const cat = (card.dataset.category || '').toLowerCase();
        const lang = (card.dataset.language || '').toLowerCase();
        const subcat = (card.dataset.subcategory || '').toLowerCase();
        const genre = (card.dataset.genre || '').toLowerCase();

        let matches = false;
        if (filter === 'all') {
          matches = true;
        } else if (cat.includes(filter) || lang.includes(filter) || subcat.includes(filter) || genre.includes(filter)) {
          matches = true;
        }

        if (matches) {
          card.style.display = '';
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      const countEl = document.getElementById('videoResultCount');
      if (countEl) countEl.textContent = visibleCount;
    });
  });
}

// 6. Form submissions (Newsletter, Contact, Collaborate, Submit Music)
function initAjaxForms() {
  // Newsletter
  const newsletterForm = document.getElementById('newsletterForm');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = newsletterForm.querySelector('input[name="email"]');
      const email = input.value.trim();

      try {
        const res = await fetch('/api/newsletter', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        const data = await res.json();
        showToast(data.message);
        if (data.success) input.value = '';
      } catch (err) {
        showToast('Could not subscribe at this time. Please try again.', 'error');
      }
    });
  }

  // Contact Form
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(contactForm);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/inquiry', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        showToast(data.message, data.success ? 'success' : 'error');
        if (data.success) contactForm.reset();
      } catch (err) {
        showToast('Submission error. Please check your connection.', 'error');
      }
    });
  }

  // Collaborate Form
  const collabForm = document.getElementById('collabForm');
  if (collabForm) {
    collabForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(collabForm);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/collaborate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        showToast(data.message, data.success ? 'success' : 'error');
        if (data.success) collabForm.reset();
      } catch (err) {
        showToast('Submission error. Please try again.', 'error');
      }
    });
  }

  // Submit Music Form
  const submitMusicForm = document.getElementById('submitMusicForm');
  if (submitMusicForm) {
    submitMusicForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(submitMusicForm);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/submit-music', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        showToast(data.message, data.success ? 'success' : 'error');
        if (data.success) submitMusicForm.reset();
      } catch (err) {
        showToast('Submission error. Please try again.', 'error');
      }
    });
  }
}

// 7. Language Switcher
function initLanguageSwitcher() {
  const selector = document.getElementById('languageSelector');
  if (selector) {
    // Read saved preference
    const saved = localStorage.getItem('divinenest_lang') || 'English';
    selector.value = saved;

    selector.addEventListener('change', () => {
      localStorage.setItem('divinenest_lang', selector.value);
      showToast(`Language set to ${selector.value}`);
    });
  }
}

// 8. Cinematic Entry Animation Video & Motion System
function initEntryAnimation() {
  const overlay = document.getElementById('siteIntroOverlay');
  if (!overlay) return;

  const enterBtn = document.getElementById('enterSiteBtn');
  const skipBtn = document.getElementById('skipIntroBtn');
  const replayBtn = document.getElementById('replayIntroBtn');
  const drawerReplayBtn = document.getElementById('drawerReplayIntroBtn');
  const progressBar = document.getElementById('introProgressBar');
  const bgVideo = document.getElementById('introBgVideo');
  const canvas = document.getElementById('introCanvas');

  let animFrameId = null;
  let progressTimer = null;
  const INTRO_DURATION_MS = 4500;

  // Check session storage — only auto-play on initial site entry
  const hasEntered = sessionStorage.getItem('divinenest_intro_played');

  // Gentle Harmonious Celestial Chime (Web Audio API)
  function playCelestialChime() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      // 5 Harmonious notes tuned to celestial pentatonic scale
      const notes = [261.63, 329.63, 392.00, 523.25, 659.25];
      notes.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, ctx.currentTime);

        const startTime = ctx.currentTime + idx * 0.08;
        gain.gain.setValueAtTime(0.0001, startTime);
        gain.gain.exponentialRampToValueAtTime(0.06 / (idx + 1), startTime + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 2.2);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(startTime);
        osc.stop(startTime + 2.3);
      });
    } catch (e) {
      // Audio autoplay policy fallback
    }
  }

  // Canvas 60fps Logo-Colors Cosmic Particle System
  function startCanvasAnimation() {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const colors = ['#01A4DD', '#62C327', '#FDC33D', '#FF6B2B', '#D81B60'];
    const particles = [];
    const PARTICLE_COUNT = Math.min(80, Math.floor((width * height) / 14000));

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: width / 2 + (Math.random() - 0.5) * 100,
        y: height / 2 + (Math.random() - 0.5) * 100,
        vx: (Math.random() - 0.5) * 2.2,
        vy: (Math.random() - 0.5) * 2.2,
        radius: Math.random() * 2.8 + 1,
        color: colors[Math.floor(Math.random() * colors.length)],
        alpha: Math.random() * 0.7 + 0.3,
        pulseSpeed: Math.random() * 0.03 + 0.01
      });
    }

    let waveRadius = 0;

    function render() {
      ctx.clearRect(0, 0, width, height);

      // Expanding soundwave ripple from center
      waveRadius = (waveRadius + 1.2) % (Math.max(width, height) * 0.6);
      ctx.beginPath();
      ctx.arc(width / 2, height / 2, waveRadius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(1, 164, 221, ${Math.max(0, 0.25 - waveRadius / (width * 0.6))})`;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Render star dust particles
      for (let p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        p.alpha += Math.sin(Date.now() * p.pulseSpeed) * 0.02;

        // Wrap around bounds
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = Math.max(0.1, Math.min(0.9, p.alpha));
        ctx.shadowBlur = 12;
        ctx.shadowColor = p.color;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
      ctx.globalAlpha = 1;

      animFrameId = requestAnimationFrame(render);
    }

    render();
  }

  function stopCanvasAnimation() {
    if (animFrameId) {
      cancelAnimationFrame(animFrameId);
      animFrameId = null;
    }
  }

  function dismissIntro(withSound = true) {
    if (withSound) playCelestialChime();
    clearInterval(progressTimer);

    overlay.classList.add('dismissed');
    document.body.classList.remove('intro-active');
    sessionStorage.setItem('divinenest_intro_played', 'true');

    setTimeout(() => {
      stopCanvasAnimation();
      if (bgVideo) bgVideo.pause();
    }, 900);
  }

  function playIntro() {
    overlay.classList.remove('dismissed');
    document.body.classList.add('intro-active');

    // Reset and start progress bar
    if (progressBar) progressBar.style.width = '0%';
    const startTime = Date.now();
    clearInterval(progressTimer);

    progressTimer = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const pct = Math.min(100, (elapsed / INTRO_DURATION_MS) * 100);
      if (progressBar) progressBar.style.width = `${pct}%`;

      if (elapsed >= INTRO_DURATION_MS) {
        clearInterval(progressTimer);
        dismissIntro(false);
      }
    }, 40);

    // Play optional background video if available
    if (bgVideo) {
      bgVideo.currentTime = 0;
      bgVideo.play().catch(() => {});
    }

    startCanvasAnimation();
  }

  // Wire up button click triggers
  if (enterBtn) {
    enterBtn.addEventListener('click', () => dismissIntro(true));
  }

  if (skipBtn) {
    skipBtn.addEventListener('click', () => dismissIntro(false));
  }

  if (replayBtn) {
    replayBtn.addEventListener('click', (e) => {
      e.preventDefault();
      playIntro();
    });
  }

  if (drawerReplayBtn) {
    drawerReplayBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const drawerOverlay = document.getElementById('mobileDrawerOverlay');
      if (drawerOverlay) drawerOverlay.classList.remove('active');
      playIntro();
    });
  }

  // Auto-play on first entry, or dismiss immediately if already seen in this session
  if (!hasEntered) {
    playIntro();
  } else {
    overlay.classList.add('dismissed');
    document.body.classList.remove('intro-active');
  }
}

