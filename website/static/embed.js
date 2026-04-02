(function() {
  'use strict';

  // === Config ===
  var API_URL = 'https://calapi.buerofalk.de/items/events';
  var API_TOKEN = 'IXya-sE0fEPTKsHDqYLy7acTyilIpUdC';
  var DIGIKAL_URL = 'https://www.digikal.org';

  var MONTH_NAMES = ['Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
  var MONTH_NAMES_LONG = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];

  // Sponsor color overrides (organizer name → accent color)
  var SPONSOR_COLORS = {
    'd3': '#fed220'
  };

  function getSponsorColor(organizer) {
    if (!organizer) return null;
    var key = organizer.toLowerCase().trim();
    for (var name in SPONSOR_COLORS) {
      if (key.indexOf(name) !== -1) return SPONSOR_COLORS[name];
    }
    return null;
  }

  // === CSS ===
  var STYLES = `
    :host {
      display: block;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1f2937;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    .dk-container { max-width: 800px; margin: 0 auto; }

    /* Header */
    .dk-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
    .dk-event-count { font-size: 0.85rem; color: #6b7280; }

    /* Filters */
    .dk-filters { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
    .dk-select {
      padding: 8px 32px 8px 12px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 0.875rem;
      color: #374151;
      background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") no-repeat right 10px center;
      appearance: none;
      cursor: pointer;
      width: 170px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .dk-select:focus { outline: none; border-color: #3178ff; box-shadow: 0 0 0 3px rgba(49,120,255,0.15); }

    /* Event list */
    .dk-events { display: flex; flex-direction: column; gap: 14px; }

    /* Event card — clickable link */
    .dk-card {
      position: relative;
      display: flex;
      gap: 16px;
      align-items: flex-start;
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 16px;
      text-decoration: none;
      color: inherit;
      transition: box-shadow 0.2s, border-color 0.2s;
    }
    .dk-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-color: #93c5fd; }
    .dk-card:hover .dk-card-title { color: #3178ff; }

    /* Date badge */
    .dk-date-badge {
      background: #eff6ff;
      color: #1d4ed8;
      min-width: 56px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 8px 6px;
      border-radius: 8px;
      text-align: center;
      flex-shrink: 0;
    }
    .dk-date-day { font-size: 1.25rem; font-weight: 700; line-height: 1.1; }
    .dk-date-month { font-size: 0.7rem; font-weight: 500; }
    .dk-date-multi { font-size: 0.6rem; margin-top: 2px; color: #3b82f6; }

    /* Sponsor date badge */
    .dk-card--sponsor .dk-date-badge { background: #fed220; color: #111827; }
    .dk-card--sponsor .dk-date-multi { color: #111827; }
    .dk-card--sponsor:hover { border-color: #fed220; }
    .dk-card--sponsor:hover .dk-card-title { color: #b45309; }

    /* Card body */
    .dk-card-body { flex: 1; min-width: 0; }
    .dk-card-title {
      font-size: 1rem;
      font-weight: 600;
      color: #111827;
      margin-bottom: 4px;
      transition: color 0.15s;
    }

    /* Meta row */
    .dk-meta { display: flex; flex-wrap: wrap; gap: 8px; font-size: 0.8rem; color: #6b7280; margin-bottom: 8px; }
    .dk-meta-item { display: flex; align-items: center; gap: 3px; }
    .dk-online { color: #3178ff; font-weight: 500; }
    .dk-free { color: #059669; font-weight: 500; }

    /* Description */
    .dk-desc {
      font-size: 0.8rem;
      color: #6b7280;
      margin-bottom: 8px;
    }

    /* Topic tags */
    .dk-topics { display: flex; flex-wrap: wrap; gap: 4px; }
    .dk-category {
      display: inline-block;
      font-size: 0.7rem;
      background: #eef5ff;
      color: #3178ff;
      padding: 2px 8px;
      border-radius: 10px;
      font-weight: 500;
    }
    .dk-card--sponsor .dk-category { background: #fef9e7; color: #92400e; }

    /* Sponsor badge */
    .dk-sponsor-badge {
      position: absolute;
      top: 8px;
      right: 8px;
      background: #fed220;
      color: #111827;
      font-size: 0.65rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 6px;
      letter-spacing: 0.02em;
    }
    .dk-card--sponsor .dk-card-title { padding-right: 70px; }

    /* Load more */
    .dk-load-more {
      display: block;
      width: 100%;
      padding: 10px;
      margin-top: 16px;
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      font-size: 0.875rem;
      color: #374151;
      cursor: pointer;
      text-align: center;
      transition: background 0.15s;
    }
    .dk-load-more:hover { background: #f3f4f6; }

    /* Footer */
    .dk-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 20px;
      padding-top: 14px;
      border-top: 1px solid #e5e7eb;
      font-size: 0.8rem;
      flex-wrap: wrap;
      gap: 8px;
    }
    .dk-footer a { color: #3178ff; text-decoration: none; font-weight: 500; }
    .dk-footer a:hover { text-decoration: underline; }
    .dk-powered { color: #9ca3af; }

    /* Loading & error */
    .dk-loading { text-align: center; padding: 40px 0; color: #6b7280; font-size: 0.9rem; }
    .dk-spinner {
      display: inline-block;
      width: 24px; height: 24px;
      border: 3px solid #e5e7eb;
      border-top-color: #3178ff;
      border-radius: 50%;
      animation: dk-spin 0.7s linear infinite;
      margin-bottom: 10px;
    }
    @keyframes dk-spin { to { transform: rotate(360deg); } }
    .dk-error { text-align: center; padding: 30px; color: #dc2626; font-size: 0.875rem; }
    .dk-empty { text-align: center; padding: 30px; color: #6b7280; font-size: 0.875rem; }

    /* Responsive */
    @media (max-width: 600px) {
      .dk-filters { flex-direction: column; }
      .dk-select { width: 100%; min-width: 0; }
      .dk-card { flex-direction: column; }
      .dk-date-badge {
        flex-direction: row;
        gap: 6px;
        padding: 8px 14px;
        min-width: 0;
      }
      .dk-date-day { font-size: 1.1rem; }
      .dk-date-multi { margin-top: 0; }
      .dk-footer { flex-direction: column; align-items: flex-start; }
    }
  `;

  // === Helpers ===
  function extractTime(dateStr) {
    if (!dateStr || dateStr.indexOf('T') === -1) return null;
    var d = new Date(dateStr);
    var h = d.getHours(), m = d.getMinutes();
    if (h === 0 && m === 0) return null;
    return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;
  }

  function formatCost(cost) {
    if (cost === null || cost === undefined || cost === '') return null;
    if (cost === 0 || cost === '0' || String(cost).toLowerCase() === 'kostenlos' || String(cost).toLowerCase() === 'free') return 'Kostenlos';
    return typeof cost === 'number' ? cost + ' \u20AC' : cost;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function getMonthKey(date) {
    return date.getFullYear() + '-' + (date.getMonth() < 9 ? '0' : '') + (date.getMonth() + 1);
  }

  // === DigiKalEmbed Class ===
  function DigiKalEmbed(container) {
    this.container = container;
    this.count = parseInt(container.getAttribute('data-count'), 10) || 10;
    this.preTopic = container.getAttribute('data-topic') || '';
    this.preSponsor = container.getAttribute('data-sponsor') || '';
    this.showFilters = container.getAttribute('data-show-filters') !== 'false';

    this.allEvents = [];
    this.filteredEvents = [];
    this.visibleCount = this.count;
    this.selectedMonth = '';
    this.selectedTopic = this.preTopic;
    this.selectedSponsor = this.preSponsor;

    this.shadow = container.attachShadow({ mode: 'open' });
    var style = document.createElement('style');
    style.textContent = STYLES;
    this.shadow.appendChild(style);
    this.root = document.createElement('div');
    this.root.className = 'dk-container';
    this.shadow.appendChild(this.root);

    this.fetchEvents();
  }

  DigiKalEmbed.prototype.fetchEvents = function() {
    var self = this;
    this.root.innerHTML = '<div class="dk-loading"><div class="dk-spinner"></div><div>Events werden geladen\u2026</div></div>';

    var params = new URLSearchParams({
      filter: JSON.stringify({ review_status: { _eq: 'approved' } }),
      sort: 'start_date',
      limit: '-1'
    });

    fetch(API_URL + '?' + params.toString(), {
      headers: { Authorization: 'Bearer ' + API_TOKEN }
    })
    .then(function(res) {
      if (!res.ok) throw new Error('API error: ' + res.status);
      return res.json();
    })
    .then(function(json) {
      self.allEvents = json.data || [];
      self.filterEvents();
      self.render();
    })
    .catch(function(err) {
      console.error('DigiKal embed error:', err);
      self.root.innerHTML = '<div class="dk-error">Events konnten nicht geladen werden. Bitte sp\u00E4ter erneut versuchen.</div>';
    });
  };

  DigiKalEmbed.prototype.filterEvents = function() {
    var now = new Date();
    now.setHours(0, 0, 0, 0);
    var selMonth = this.selectedMonth;
    var selTopic = this.selectedTopic;
    var selSponsor = this.selectedSponsor;

    this.filteredEvents = this.allEvents.filter(function(ev) {
      var start = new Date(ev.start_date);
      if (start < now) return false;
      if (selMonth && getMonthKey(start) !== selMonth) return false;
      if (selTopic) {
        var topics = (ev.tag_groups && ev.tag_groups.topic) || [];
        if (topics.indexOf(selTopic) === -1) return false;
      }
      if (selSponsor) {
        var org = (ev.organizer || '').toLowerCase();
        if (org.indexOf(selSponsor.toLowerCase()) === -1) return false;
      }
      return true;
    });
  };

  DigiKalEmbed.prototype.getAvailableMonths = function() {
    var now = new Date();
    now.setHours(0, 0, 0, 0);
    var counts = {};
    var selTopic = this.selectedTopic;
    var selSponsor = this.selectedSponsor;

    this.allEvents.forEach(function(ev) {
      var start = new Date(ev.start_date);
      if (start < now) return;
      if (selTopic) {
        var topics = (ev.tag_groups && ev.tag_groups.topic) || [];
        if (topics.indexOf(selTopic) === -1) return;
      }
      if (selSponsor) {
        var org = (ev.organizer || '').toLowerCase();
        if (org.indexOf(selSponsor.toLowerCase()) === -1) return;
      }
      var key = getMonthKey(start);
      counts[key] = (counts[key] || 0) + 1;
    });

    return Object.keys(counts).sort().map(function(key) {
      var parts = key.split('-');
      var mi = parseInt(parts[1], 10) - 1;
      return { key: key, label: MONTH_NAMES_LONG[mi] + ' ' + parts[0], count: counts[key] };
    });
  };

  DigiKalEmbed.prototype.getAvailableTopics = function() {
    var now = new Date();
    now.setHours(0, 0, 0, 0);
    var counts = {};
    var selMonth = this.selectedMonth;
    var selSponsor = this.selectedSponsor;

    this.allEvents.forEach(function(ev) {
      var start = new Date(ev.start_date);
      if (start < now) return;
      if (selMonth && getMonthKey(start) !== selMonth) return;
      if (selSponsor) {
        var org = (ev.organizer || '').toLowerCase();
        if (org.indexOf(selSponsor.toLowerCase()) === -1) return;
      }
      var topics = (ev.tag_groups && ev.tag_groups.topic) || [];
      topics.forEach(function(t) {
        counts[t] = (counts[t] || 0) + 1;
      });
    });

    return Object.keys(counts).sort(function(a, b) {
      return a.localeCompare(b);
    }).map(function(key) {
      return { key: key, label: key, count: counts[key] };
    });
  };

  DigiKalEmbed.prototype.getAvailableSponsors = function() {
    var now = new Date();
    now.setHours(0, 0, 0, 0);
    var counts = {};
    var selMonth = this.selectedMonth;
    var selTopic = this.selectedTopic;

    this.allEvents.forEach(function(ev) {
      var start = new Date(ev.start_date);
      if (start < now) return;
      if (selMonth && getMonthKey(start) !== selMonth) return;
      if (selTopic) {
        var topics = (ev.tag_groups && ev.tag_groups.topic) || [];
        if (topics.indexOf(selTopic) === -1) return;
      }
      if (ev.organizer) {
        counts[ev.organizer] = (counts[ev.organizer] || 0) + 1;
      }
    });

    return Object.keys(counts).sort(function(a, b) {
      return a.localeCompare(b);
    }).map(function(key) {
      return { key: key, label: key, count: counts[key] };
    });
  };

  DigiKalEmbed.prototype.render = function() {
    var self = this;
    var html = '';

    // Header (event count only, no headline)
    html += '<div class="dk-header">';
    html += '<span class="dk-event-count">' + this.filteredEvents.length + ' Event' + (this.filteredEvents.length !== 1 ? 's' : '') + '</span>';
    html += '</div>';

    // Filters
    if (this.showFilters) {
      var months = this.getAvailableMonths();
      var topics = this.getAvailableTopics();
      var sponsors = this.getAvailableSponsors();

      html += '<div class="dk-filters">';

      // Month dropdown
      html += '<select class="dk-select" data-filter="month">';
      html += '<option value="">Alle Monate</option>';
      months.forEach(function(m) {
        html += '<option value="' + m.key + '"' + (self.selectedMonth === m.key ? ' selected' : '') + '>' + escapeHtml(m.label) + ' (' + m.count + ')</option>';
      });
      html += '</select>';

      // Topic dropdown (only if no pre-filter set)
      if (!this.preTopic) {
        html += '<select class="dk-select" data-filter="topic">';
        html += '<option value="">Alle Themen</option>';
        topics.forEach(function(t) {
          html += '<option value="' + escapeHtml(t.key) + '"' + (self.selectedTopic === t.key ? ' selected' : '') + '>' + escapeHtml(t.label) + ' (' + t.count + ')</option>';
        });
        html += '</select>';
      }

      // Sponsor/organizer dropdown (only if no pre-filter set)
      if (!this.preSponsor) {
        html += '<select class="dk-select" data-filter="sponsor">';
        html += '<option value="">Alle Veranstalter</option>';
        sponsors.forEach(function(s) {
          html += '<option value="' + escapeHtml(s.key) + '"' + (self.selectedSponsor === s.key ? ' selected' : '') + '>' + escapeHtml(s.label) + ' (' + s.count + ')</option>';
        });
        html += '</select>';
      }

      html += '</div>';
    }

    // Event cards
    if (this.filteredEvents.length === 0) {
      html += '<div class="dk-empty">Keine Veranstaltungen gefunden.</div>';
    } else {
      html += '<div class="dk-events">';
      var visible = this.filteredEvents.slice(0, this.visibleCount);
      visible.forEach(function(ev) {
        html += self.renderEventCard(ev);
      });
      html += '</div>';

      // Load more
      if (this.visibleCount < this.filteredEvents.length) {
        var remaining = this.filteredEvents.length - this.visibleCount;
        html += '<button class="dk-load-more">Weitere Events anzeigen (' + remaining + ' verbleibend)</button>';
      }
    }

    // Footer
    html += '<div class="dk-footer">';
    html += '<a href="' + DIGIKAL_URL + '" target="_blank" rel="noopener noreferrer">Alle Events auf digikal.org \u2192</a>';
    html += '<span class="dk-powered">Daten von <a href="' + DIGIKAL_URL + '" target="_blank" rel="noopener noreferrer">digikal.org</a></span>';
    html += '</div>';

    this.root.innerHTML = html;

    // Bind events
    var monthSelect = this.root.querySelector('[data-filter="month"]');
    if (monthSelect) {
      monthSelect.addEventListener('change', function() {
        self.selectedMonth = this.value;
        self.visibleCount = self.count;
        self.filterEvents();
        self.render();
      });
    }

    var topicSelect = this.root.querySelector('[data-filter="topic"]');
    if (topicSelect) {
      topicSelect.addEventListener('change', function() {
        self.selectedTopic = this.value;
        self.visibleCount = self.count;
        self.filterEvents();
        self.render();
      });
    }

    var sponsorSelect = this.root.querySelector('[data-filter="sponsor"]');
    if (sponsorSelect) {
      sponsorSelect.addEventListener('change', function() {
        self.selectedSponsor = this.value;
        self.visibleCount = self.count;
        self.filterEvents();
        self.render();
      });
    }

    var loadMoreBtn = this.root.querySelector('.dk-load-more');
    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', function() {
        self.visibleCount += self.count;
        self.render();
      });
    }
  };

  DigiKalEmbed.prototype.renderEventCard = function(ev) {
    var start = new Date(ev.start_date);
    var day = start.getDate();
    var month = MONTH_NAMES[start.getMonth()];
    var startTime = extractTime(ev.start_date);
    var endTime = extractTime(ev.end_date);
    var cost = formatCost(ev.cost);
    var topics = (ev.tag_groups && ev.tag_groups.topic) || [];
    var link = ev.website || ev.register_link || '';
    var isSponsor = !!getSponsorColor(ev.organizer);
    var cardClass = 'dk-card' + (isSponsor ? ' dk-card--sponsor' : '');

    // Multi-day?
    var multiDay = '';
    if (ev.end_date) {
      var end = new Date(ev.end_date);
      if (start.toDateString() !== end.toDateString()) {
        var days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
        multiDay = '<div class="dk-date-multi">+ ' + days + ' Tage</div>';
      }
    }

    // Whole card is a link if URL exists
    var html;
    if (link) {
      html = '<a class="' + cardClass + '" href="' + escapeHtml(link) + '" target="_blank" rel="noopener noreferrer">';
    } else {
      html = '<div class="' + cardClass + '">';
    }

    // Sponsor badge (top right)
    if (isSponsor) {
      html += '<span class="dk-sponsor-badge">D3</span>';
    }

    // Date badge
    html += '<div class="dk-date-badge">';
    html += '<div class="dk-date-day">' + day + '</div>';
    html += '<div class="dk-date-month">' + month + '</div>';
    html += multiDay;
    html += '</div>';

    // Body
    html += '<div class="dk-card-body">';

    // Title
    html += '<div class="dk-card-title">' + escapeHtml(ev.title) + '</div>';

    // Meta
    html += '<div class="dk-meta">';

    if (startTime) {
      html += '<span class="dk-meta-item">' + startTime;
      if (endTime) html += ' \u2013 ' + endTime;
      html += ' Uhr</span>';
    }

    if (ev.location) {
      html += '<span class="dk-meta-item">' + escapeHtml(ev.location) + '</span>';
    } else {
      html += '<span class="dk-meta-item dk-online">Online</span>';
    }

    if (cost) {
      var costClass = cost === 'Kostenlos' ? ' dk-free' : '';
      html += '<span class="dk-meta-item' + costClass + '">' + escapeHtml(cost) + '</span>';
    }

    if (ev.organizer) {
      html += '<span class="dk-meta-item">' + escapeHtml(ev.organizer) + '</span>';
    }

    html += '</div>';

    // Description (full, no truncation)
    if (ev.description) {
      html += '<div class="dk-desc">' + escapeHtml(ev.description) + '</div>';
    }

    // Topic tags
    if (topics.length > 0) {
      html += '<div class="dk-topics">';
      topics.forEach(function(t) {
        html += '<span class="dk-category">' + escapeHtml(t) + '</span>';
      });
      html += '</div>';
    }

    html += '</div>'; // card-body
    html += link ? '</a>' : '</div>';

    return html;
  };

  // === Bootstrap ===
  function init() {
    var container = document.getElementById('digikal-events');
    if (!container) return;
    new DigiKalEmbed(container);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
