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
  initEntryAnimation();
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

