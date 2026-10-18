/**
 * DIVINENEST — ADMIN DASHBOARD JAVASCRIPT
 */

document.addEventListener('DOMContentLoaded', () => {
  initAdminTabs();
  initTableSearch();
});

function initAdminTabs() {
  const tabs = document.querySelectorAll('.admin-tab-btn');
  const panes = document.querySelectorAll('.admin-tab-pane');

  function activateTab(targetId) {
    tabs.forEach(t => t.classList.remove('active'));
    panes.forEach(p => p.classList.remove('active'));

    const activeBtn = document.querySelector(`.admin-tab-btn[data-target="${targetId}"]`);
    const activePane = document.getElementById(targetId);

    if (activeBtn && activePane) {
      activeBtn.classList.add('active');
      activePane.classList.add('active');
      window.location.hash = targetId;
    }
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.target;
      activateTab(target);
    });
  });

  // Check URL hash
  if (window.location.hash) {
    const hash = window.location.hash.substring(1);
    activateTab(hash);
  }
}

function initTableSearch() {
  const searchInput = document.getElementById('adminTableSearch');
  if (!searchInput) return;

  searchInput.addEventListener('input', () => {
    const term = searchInput.value.toLowerCase();
    const rows = document.querySelectorAll('.admin-table tbody tr');

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(term) ? '' : 'none';
    });
  });
}
