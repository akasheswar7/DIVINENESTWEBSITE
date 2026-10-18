/**
 * DIVINENEST — MAIN CLIENT-SIDE INTERACTIVITY
 * Audio Player, Video Modal, AJAX Forms, Likes, Favorites & Share
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initVideoModal();
  initAudioPlayer();
  initLikeButtons();
  initShareButtons();
  initAjaxForms();
  initLanguageSwitcher();
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

// 1. Mobile Menu Drawer
function initMobileMenu() {
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const mainNav = document.querySelector('.main-nav');

  if (menuBtn && mainNav) {
    menuBtn.addEventListener('click', () => {
      const isOpen = mainNav.classList.toggle('mobile-open');
      menuBtn.innerHTML = isOpen ? '✕' : '☰';
      if (isOpen) {
        mainNav.style.display = 'flex';
        mainNav.style.flexDirection = 'column';
        mainNav.style.position = 'absolute';
        mainNav.style.top = '72px';
        mainNav.style.left = '0';
        mainNav.style.right = '0';
        mainNav.style.background = 'var(--bg-card)';
        mainNav.style.padding = '1.5rem';
        mainNav.style.borderBottom = '1px solid var(--border-light)';
        mainNav.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
      } else {
        mainNav.style.display = '';
      }
    });
  }
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

// 3. Audio Mini-Player Bar
let audioObj = null;

function initAudioPlayer() {
  const playerBar = document.getElementById('audioPlayerBar');
  if (!playerBar) return;

  const playBtn = document.getElementById('playerPlayBtn');
  const titleEl = document.getElementById('playerSongTitle');
  const artistEl = document.getElementById('playerSongArtist');
  const thumbEl = document.getElementById('playerSongThumb');
  const progressFill = document.getElementById('playerProgressFill');
  const progressBar = document.getElementById('playerProgressBar');
  const timeCurrent = document.getElementById('playerCurrentTime');
  const timeDuration = document.getElementById('playerDuration');
  const closeBtn = document.getElementById('playerCloseBtn');

  audioObj = new Audio();

  // Play audio trigger buttons on song cards
  document.querySelectorAll('[data-audio-url]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const audioUrl = btn.dataset.audioUrl;
      const title = btn.dataset.title || 'Soulful Melody';
      const artist = btn.dataset.artist || 'DivineNest Music';
      const thumb = btn.dataset.thumb || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=200';

      if (!audioUrl) return;

      if (audioObj.src !== audioUrl) {
        audioObj.src = audioUrl;
      }

      titleEl.textContent = title;
      artistEl.textContent = artist;
      thumbEl.src = thumb;
      playerBar.classList.add('active');

      audioObj.play().then(() => {
        if (playBtn) playBtn.innerHTML = '⏸';
      }).catch(err => {
        console.warn('Audio play restricted:', err);
      });
    });
  });

  if (playBtn) {
    playBtn.addEventListener('click', () => {
      if (audioObj.paused) {
        audioObj.play();
        playBtn.innerHTML = '⏸';
      } else {
        audioObj.pause();
        playBtn.innerHTML = '▶';
      }
    });
  }

  // Update time and progress bar
  audioObj.addEventListener('timeupdate', () => {
    if (audioObj.duration) {
      const pct = (audioObj.currentTime / audioObj.duration) * 100;
      if (progressFill) progressFill.style.width = `${pct}%`;
      if (timeCurrent) timeCurrent.textContent = formatTime(audioObj.currentTime);
      if (timeDuration) timeDuration.textContent = formatTime(audioObj.duration);
    }
  });

  // Seek on progress bar click
  if (progressBar) {
    progressBar.addEventListener('click', (e) => {
      const rect = progressBar.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const width = rect.width;
      if (audioObj.duration) {
        audioObj.currentTime = (clickX / width) * audioObj.duration;
      }
    });
  }

  // Close player
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      audioObj.pause();
      playerBar.classList.remove('active');
    });
  }
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60) || 0;
  const secs = Math.floor(seconds % 60) || 0;
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// 4. Video Likes Handler
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

// 5. Share Buttons Handler
function initShareButtons() {
  document.querySelectorAll('.btn-share').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const shareData = {
        title: document.title || 'DivineNest',
        text: 'Listen to this beautiful melody on DivineNest — Where Music, Stories & Joy Come Together!',
        url: window.location.href
      };

      if (navigator.share) {
        try {
          await navigator.share(shareData);
        } catch (err) {
          // user cancelled
        }
      } else {
        // Fallback: Copy to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
          showToast('Link copied to clipboard! 🔗');
        }).catch(() => {
          showToast('Share link ready!');
        });
      }
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
