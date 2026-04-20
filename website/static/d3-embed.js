(function() {
  'use strict';

  // === Config ===
  var API_URL = 'https://calapi.buerofalk.de/items/events';
  var API_TOKEN = 'IXya-sE0fEPTKsHDqYLy7acTyilIpUdC';
  var DIGIKAL_URL = 'https://www.digikal.org';
  var TAG_CLUSTERS_URL = DIGIKAL_URL + '/tag-clusters.json';

  // === Tag cluster state (populated from /tag-clusters.json on init) ===
  var CLUSTER_KEYS_SET = {};
  var MEMBER_TO_CLUSTER = {};
  var LOWER_DROP = {};
  var clustersLoadedPromise = null;

  function loadClusters() {
    if (clustersLoadedPromise) return clustersLoadedPromise;
    clustersLoadedPromise = fetch(TAG_CLUSTERS_URL)
      .then(function(res) {
        if (!res.ok) throw new Error('cluster fetch ' + res.status);
        return res.json();
      })
      .then(function(data) {
        (data.drop || []).forEach(function(t) { LOWER_DROP[t.toLowerCase()] = true; });
        (data.clusters || []).forEach(function(c) {
          CLUSTER_KEYS_SET[c.key] = true;
          (c.members || []).forEach(function(m) {
            MEMBER_TO_CLUSTER[m.toLowerCase()] = c.key;
          });
        });
      })
      .catch(function(err) {
        // Degrade gracefully: without a cluster map, tags pass through raw.
        console.warn('DigiKal embed: cluster map unavailable, showing raw tags', err);
      });
    return clustersLoadedPromise;
  }

  function clusterTag(raw) {
    if (!raw) return null;
    var key = String(raw).toLowerCase().trim();
    if (LOWER_DROP[key]) return null;
    return MEMBER_TO_CLUSTER[key] || raw;
  }

  function getDisplayTopics(ev) {
    var raw = (ev.tag_groups && ev.tag_groups.topic) || [];
    var seen = {};
    var out = [];
    for (var i = 0; i < raw.length; i++) {
      var c = clusterTag(raw[i]);
      if (!c || seen[c]) continue;
      seen[c] = true;
      out.push(c);
    }
    return out;
  }

  var MONTH_NAMES = ['Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
  var MONTH_NAMES_LONG = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];

  // Sponsor color overrides (organizer substring → accent color)
  var SPONSOR_COLORS = {
    'd3': '#fed220',
    'bürgermut': '#fed220'
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
  // Themed for so-geht-digital.de (D3): Montserrat inherited from host page,
  // near-black #232427 text, light-grey #eceef1 / #c5c8cf, yellow #fed220
  // reserved as accent for Bürgermut/d3 sponsor events.
  var STYLES = `
    :host {
      display: block;
      font-family: inherit;
      color: #232427;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; font-family: inherit; }

    .dk-container { max-width: 800px; margin: 0 auto; }

    /* Header */
    .dk-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
    .dk-event-count { font-size: 0.85rem; color: #53565d; }

    /* Filters — D3 outlined style: 2px border, 1.5rem radius */
    .dk-filters { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
    .dk-select {
      padding: 0.5rem 2.25rem 0.5rem 1rem;
      border: 2px solid #232427;
      border-radius: 1.5rem;
      font-size: 0.875rem;
      font-weight: 600;
      color: #232427;
      background: transparent url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23232427' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") no-repeat right 14px center;
      appearance: none;
      cursor: pointer;
      width: 170px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      transition: background-color 0.3s, color 0.3s;
    }
    .dk-select:hover { background: #232427 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") no-repeat right 14px center; color: #fff; }
    .dk-select:focus { outline: none; box-shadow: 0 0 0 3px rgba(35,36,39,0.2); }

    /* Event list */
    .dk-events { display: flex; flex-direction: column; gap: 14px; }

    /* Event card — clickable link */
    .dk-card {
      position: relative;
      display: flex;
      gap: 16px;
      align-items: flex-start;
      background: #fff;
      border: 1px solid #c5c8cf;
      border-radius: 1.5rem;
      padding: 16px;
      text-decoration: none;
      color: inherit;
      transition: box-shadow 0.2s, border-color 0.2s;
    }
    .dk-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-color: #232427; }
    .dk-card:hover .dk-card-title { color: #232427; }

    /* Date badge — light grey with black text (blends with D3 site) */
    .dk-date-badge {
      background: #eceef1;
      color: #232427;
      min-width: 56px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 8px 6px;
      border-radius: 1rem;
      text-align: center;
      flex-shrink: 0;
    }
    .dk-date-day { font-size: 1.25rem; font-weight: 700; line-height: 1.1; }
    .dk-date-month { font-size: 0.7rem; font-weight: 500; }
    .dk-date-multi { font-size: 0.6rem; margin-top: 2px; color: #53565d; }

    /* Sponsor card — D3 yellow accent for Bürgermut / d3 events */
    .dk-card--sponsor .dk-date-badge { background: #fed220; color: #232427; }
    .dk-card--sponsor .dk-date-multi { color: #232427; }
    .dk-card--sponsor:hover { border-color: #fed220; }
    .dk-card--sponsor:hover .dk-card-title { color: #232427; }

    /* Card body */
    .dk-card-body { flex: 1; min-width: 0; }
    .dk-card-title {
      font-size: 1rem;
      font-weight: 700;
      color: #232427;
      margin-bottom: 4px;
      transition: color 0.15s;
    }

    /* Meta row */
    .dk-meta { display: flex; flex-wrap: wrap; gap: 8px; font-size: 0.8rem; color: #53565d; margin-bottom: 8px; }
    .dk-meta-item { display: flex; align-items: center; gap: 3px; }
    .dk-online { color: #232427; font-weight: 600; }
    .dk-free { color: #232427; font-weight: 600; }

    /* Description */
    .dk-desc {
      font-size: 0.8rem;
      color: #53565d;
      margin-bottom: 8px;
    }

    /* Topic tags — neutral pills by default, yellow for sponsor cards */
    .dk-topics { display: flex; flex-wrap: wrap; gap: 4px; }
    .dk-category {
      display: inline-block;
      font-size: 0.7rem;
      background: #eceef1;
      color: #232427;
      padding: 3px 10px;
      border-radius: 9999px;
      font-weight: 600;
    }
    .dk-card--sponsor .dk-category { background: #fef3bf; color: #232427; }

    /* Sponsor badge */
    .dk-sponsor-badge {
      position: absolute;
      top: 10px;
      right: 10px;
      background: #fed220;
      color: #232427;
      font-size: 0.65rem;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 9999px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .dk-card--sponsor .dk-card-title { padding-right: 70px; }

    /* Load more — D3 outlined button: 2px border, 1.5rem radius, uppercase, fills on hover */
    .dk-load-more {
      display: block;
      width: 100%;
      padding: 0.75rem 1.5rem;
      margin-top: 1.5rem;
      background: transparent;
      border: 2px solid #232427;
      border-radius: 1.5rem;
      font-size: 0.875rem;
      font-weight: 600;
      color: #232427;
      cursor: pointer;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      line-height: 1.45;
      transition: background-color 0.3s, border-color 0.3s, color 0.3s;
    }
    .dk-load-more:hover,
    .dk-load-more:focus { background-color: #232427 !important; color: #fff !important; border-color: #232427 !important; }

    /* Footer */
    .dk-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 20px;
      padding-top: 14px;
      border-top: 1px solid #c5c8cf;
      font-size: 0.8rem;
      flex-wrap: wrap;
      gap: 8px;
    }
    .dk-footer a { color: #232427; text-decoration: none; font-weight: 600; border-bottom: 2px solid #fed220; }
    .dk-footer a:hover { background: #fed220; }
    .dk-powered { color: #93969e; }
    .dk-powered a { color: #232427; text-decoration: none; border-bottom: 1px solid #c5c8cf; }
    .dk-powered a:hover { border-bottom-color: #fed220; }

    /* Loading & error */
    .dk-loading { text-align: center; padding: 40px 0; color: #53565d; font-size: 0.9rem; }
    .dk-spinner {
      display: inline-block;
      width: 24px; height: 24px;
      border: 3px solid #eceef1;
      border-top-color: #fed220;
      border-radius: 50%;
      animation: dk-spin 0.7s linear infinite;
      margin-bottom: 10px;
    }
    @keyframes dk-spin { to { transform: rotate(360deg); } }
    .dk-error { text-align: center; padding: 30px; color: #232427; font-size: 0.875rem; }
    .dk-empty { text-align: center; padding: 30px; color: #53565d; font-size: 0.875rem; }

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

  // Default pre-selections (user-changeable, unlike data-topic/data-sponsor which lock & hide)
  var DEFAULT_TOPIC = 'KI';
  var DEFAULT_SPONSOR = 'Stiftung Bürgermut';

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
    this.selectedTopic = this.preTopic || DEFAULT_TOPIC;
    this.selectedSponsor = this.preSponsor || DEFAULT_SPONSOR;

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

    var eventsReq = fetch(API_URL + '?' + params.toString(), {
      headers: { Authorization: 'Bearer ' + API_TOKEN }
    }).then(function(res) {
      if (!res.ok) throw new Error('API error: ' + res.status);
      return res.json();
    });

    Promise.all([eventsReq, loadClusters()])
      .then(function(results) {
        self.allEvents = (results[0] && results[0].data) || [];
        self.normalizePreselections();
        self.filterEvents();
        self.render();
      })
      .catch(function(err) {
        console.error('DigiKal embed error:', err);
        self.root.innerHTML = '<div class="dk-error">Events konnten nicht geladen werden. Bitte sp\u00E4ter erneut versuchen.</div>';
      });
  };

  DigiKalEmbed.prototype.normalizePreselections = function() {
    // Map default/preset topic onto a cluster key (or raw tag) that actually exists in the data.
    if (this.selectedTopic) {
      var selectedCluster = clusterTag(this.selectedTopic);
      var found = false;
      if (selectedCluster) {
        for (var i = 0; i < this.allEvents.length; i++) {
          if (getDisplayTopics(this.allEvents[i]).indexOf(selectedCluster) !== -1) {
            found = true;
            break;
          }
        }
      }
      if (found && selectedCluster) this.selectedTopic = selectedCluster;
      else if (!this.preTopic) this.selectedTopic = '';
    }

    if (this.selectedSponsor) {
      var needleS = this.selectedSponsor.toLowerCase();
      var exactSponsor = null;
      this.allEvents.some(function(ev) {
        if (ev.organizer && ev.organizer.toLowerCase().indexOf(needleS) !== -1) {
          exactSponsor = ev.organizer;
          return true;
        }
        return false;
      });
      if (exactSponsor) this.selectedSponsor = exactSponsor;
      else if (!this.preSponsor) this.selectedSponsor = '';
    }
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
        if (getDisplayTopics(ev).indexOf(selTopic) === -1) return false;
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
        if (getDisplayTopics(ev).indexOf(selTopic) === -1) return;
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
      getDisplayTopics(ev).forEach(function(t) {
        counts[t] = (counts[t] || 0) + 1;
      });
    });

    // Sort by count desc, then alphabetically. Clusters always shown; unmapped
    // tags hidden below count=2 to keep the dropdown focused.
    var keys = [];
    for (var k in counts) {
      var isCluster = !!CLUSTER_KEYS_SET[k];
      if (isCluster || counts[k] >= 2) keys.push(k);
    }
    keys.sort(function(a, b) {
      return (counts[b] - counts[a]) || a.localeCompare(b);
    });
    return keys.map(function(key) {
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
        if (getDisplayTopics(ev).indexOf(selTopic) === -1) return;
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
    html += '<span class="dk-powered">Daten von <a href="' + DIGIKAL_URL + '" target="_blank" rel="noopener noreferrer">digikal.org</a></span>';
    html += '</div>';

    // Filters
    if (this.showFilters) {
      var months = this.getAvailableMonths();
      var topics = this.getAvailableTopics();
      var sponsors = this.getAvailableSponsors();

      html += '<div class="dk-filters">';

      // 1. Topic dropdown (only if no pre-filter lock)
      if (!this.preTopic) {
        html += '<select class="dk-select" data-filter="topic">';
        html += '<option value="">Alle Themen</option>';
        topics.forEach(function(t) {
          html += '<option value="' + escapeHtml(t.key) + '"' + (self.selectedTopic === t.key ? ' selected' : '') + '>' + escapeHtml(t.label) + ' (' + t.count + ')</option>';
        });
        html += '</select>';
      }

      // 2. Sponsor/organizer dropdown (only if no pre-filter lock)
      if (!this.preSponsor) {
        html += '<select class="dk-select" data-filter="sponsor">';
        html += '<option value="">Alle Veranstalter</option>';
        sponsors.forEach(function(s) {
          html += '<option value="' + escapeHtml(s.key) + '"' + (self.selectedSponsor === s.key ? ' selected' : '') + '>' + escapeHtml(s.label) + ' (' + s.count + ')</option>';
        });
        html += '</select>';
      }

      // 3. Month dropdown
      html += '<select class="dk-select" data-filter="month">';
      html += '<option value="">Alle Monate</option>';
      months.forEach(function(m) {
        html += '<option value="' + m.key + '"' + (self.selectedMonth === m.key ? ' selected' : '') + '>' + escapeHtml(m.label) + ' (' + m.count + ')</option>';
      });
      html += '</select>';

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
    var topics = getDisplayTopics(ev);
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
