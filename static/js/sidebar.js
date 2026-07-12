function renderSidebar(activePage) {
  const pages = [
    { id: 'dashboard', label: 'Dashboard', href: '/dashboard/', icon: `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>` },
    { id: 'live', label: 'Live Surveillance', href: '/live/', icon: `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="6" width="20" height="14" rx="2"/><path d="M8 6V4h8v2"/></svg>` },
    { id: 'timeline', label: 'Activity Timeline', href: '/timeline/', icon: `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>` },
    { id: 'alerts', label: 'Alerts', href: '/alerts/', icon: `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>` },
  ];
  const managePages = [
    { id: 'members', label: 'Members', href: '/members/', icon: `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>` },
    { id: 'devices', label: 'Devices', href: '/devices/', icon: `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>` },
    { id: 'assistant', label: 'Smart Assistant', href: '/assistant/', icon: `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>` },
    { id: 'settings', label: 'Settings', href: '/settings/', icon: `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>` },
  ];

  const navItem = (p) => `
    <a href="${p.href}" class="nav-item ${activePage === p.id ? 'active' : ''}">
      ${p.icon} ${p.label}
    </a>`;

  return `
    <div class="sidebar-logo">
      <div class="sidebar-logo-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
      </div>
      <div>
        <div class="sidebar-logo-text">HOMEGUARD</div>
        <div class="sidebar-logo-sub">V2.4 · SECURE</div>
      </div>
    </div>
    <div class="sidebar-home-switcher" id="homeSwitcherWrap" style="position:relative;margin:14px 16px 4px;">
      <div style="font-size:9px;letter-spacing:.1em;color:#3a4a6a;margin-bottom:6px;padding-left:2px;">ACTIVE HOME</div>
      <div id="homeSwitcherBtn" onclick="toggleHomeSwitcher()" style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:9px;padding:9px 12px;cursor:pointer;">
        <div style="display:flex;align-items:center;gap:8px;overflow:hidden;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" style="flex-shrink:0;"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          <span id="activeHomeName" style="color:white;font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">My Home</span>
        </div>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#6a8aaa" stroke-width="2" style="flex-shrink:0;"><polyline points="6 9 12 15 18 9"/></svg>
      </div>
      <div id="homeSwitcherMenu" style="display:none;position:absolute;top:100%;left:0;right:0;margin-top:6px;background:#0d1929;border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:6px;z-index:50;box-shadow:0 10px 30px rgba(0,0,0,0.5);"></div>
    </div>
    <div class="sidebar-section-label">MONITOR</div>
    ${pages.map(navItem).join('')}
    <div class="sidebar-section-label">MANAGE</div>
    ${managePages.map(navItem).join('')}
    <div style="flex:1"></div>
    <div class="sidebar-status">
      <div class="sidebar-status-label">SYSTEM STATUS</div>
      <div class="sidebar-status-main">● <span>Armed · Normal</span></div>
      <div class="sidebar-status-sub">Uptime 99.98% · 4 cams live</div>
    </div>
  `;
}

function renderTopbar(title, subtitle) {
  const userName = localStorage.getItem('hg_user_name') || 'Alex Reyes';
  const initials = userName.split(' ').filter(Boolean).slice(0,2).map(w => w[0].toUpperCase()).join('');
  return `
    <div class="topbar">
      <div>
        <div class="topbar-title">${title}</div>
        <div class="topbar-sub">${subtitle}</div>
      </div>
      <div class="topbar-right">
        <div class="mode-badge"><span class="mode-dot"></span> NORMAL MODE</div>
        <div class="notif-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8a9ab8" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span class="notif-dot"></span>
        </div>
        <div class="avatar-btn" title="${userName}">${initials}</div>
      </div>
    </div>
  `;
}

/* ===== ACTIVE HOME SWITCHER ===== */
function getHomesList() {
  let homes = JSON.parse(localStorage.getItem('hg_your_homes') || '[]');
  if (homes.length === 0) {
    // sensible demo fallback so the dropdown is never empty
    homes = [{ name: 'My Home', address: '', role: 'Owner' }];
    localStorage.setItem('hg_your_homes', JSON.stringify(homes));
  }
  return homes;
}

function initHomeSwitcher() {
  const homes = getHomesList();
  let active = localStorage.getItem('hg_active_home') || homes[0].name;
  if (!homes.find(h => h.name === active)) active = homes[0].name;
  localStorage.setItem('hg_active_home', active);

  const nameEl = document.getElementById('activeHomeName');
  if (nameEl) nameEl.textContent = active;

  const menu = document.getElementById('homeSwitcherMenu');
  if (!menu) return;
  menu.innerHTML = homes.map(h => `
    <div onclick="switchHome('${h.name}')" style="display:flex;align-items:center;justify-content:space-between;padding:9px 10px;border-radius:7px;cursor:pointer;${h.name===active?'background:rgba(59,130,246,0.12);':''}" onmouseover="this.style.background='rgba(255,255,255,0.06)'" onmouseout="this.style.background='${h.name===active?'rgba(59,130,246,0.12)':'transparent'}'">
      <div style="display:flex;align-items:center;gap:8px;">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="${h.name===active?'#3b82f6':'#6a8aaa'}" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <span style="color:${h.name===active?'white':'#a0b0d0'};font-size:13px;">${h.name}</span>
      </div>
      <span style="font-size:9px;font-weight:700;letter-spacing:.06em;padding:2px 6px;border-radius:4px;background:rgba(255,255,255,0.08);color:#8a9ab8;">${h.role.toUpperCase()}</span>
    </div>
  `).join('') + `
    <div style="border-top:1px solid rgba(255,255,255,0.07);margin-top:6px;padding-top:6px;">
      <a href="/home-setup/" style="display:flex;align-items:center;gap:8px;padding:9px 10px;color:#3b82f6;font-size:13px;text-decoration:none;border-radius:7px;" onmouseover="this.style.background='rgba(255,255,255,0.06)'" onmouseout="this.style.background='transparent'">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Add or manage homes
      </a>
    </div>
  `;
}

function toggleHomeSwitcher() {
  const menu = document.getElementById('homeSwitcherMenu');
  if (!menu) return;
  menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

function switchHome(name) {
  localStorage.setItem('hg_active_home', name);
  initHomeSwitcher();
  toggleHomeSwitcher();
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
  const wrap = document.getElementById('homeSwitcherWrap');
  const menu = document.getElementById('homeSwitcherMenu');
  if (wrap && menu && !wrap.contains(e.target)) menu.style.display = 'none';
});