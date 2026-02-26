<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { getAllEvents } from '../services/directApi';

  // Debug variables to show date ranges
  let nextWeekStart = '';
  let nextWeekEnd = '';
  let loadingStatus = '';
  let eventsCount = 0;
  
  // Store for all events without filtering
  let allEvents = [];
  // Store for filtered events for next week
  let nextWeekEvents = [];
  // Store for the generated post text
  const postText = writable('');
  // Loading state
  let isLoading = true;
  // Error state
  let hasError = false;
  let errorMessage = '';

  // Set filter to upcoming on mount and load all events directly
  onMount(async () => {
    try {
      // Calculate next week date range for debugging and filtering
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const dayOfWeek = today.getDay();
      const diff = dayOfWeek === 0 ? 1 : 8 - dayOfWeek; // Adjust for Sunday
      const startOfNextWeek = new Date(today);
      startOfNextWeek.setDate(today.getDate() + diff);
      const endOfNextWeek = new Date(startOfNextWeek);
      endOfNextWeek.setDate(startOfNextWeek.getDate() + 6);
      
      nextWeekStart = startOfNextWeek.toLocaleDateString('de-DE');
      nextWeekEnd = endOfNextWeek.toLocaleDateString('de-DE');
      
      loadingStatus = 'Lade Veranstaltungen...';
      isLoading = true;
      
      // Load all approved events directly from API
      allEvents = await getAllEvents();
      console.log('Alle geladenen Veranstaltungen:', allEvents);
      
      // Filter events for next week manually
      nextWeekEvents = allEvents.filter(event => {
        if (!event.start_date) return false;
        
        const eventDate = new Date(event.start_date);
        return eventDate >= startOfNextWeek && eventDate <= endOfNextWeek;
      });
      
      eventsCount = nextWeekEvents.length;
      console.log('Veranstaltungen für nächste Woche:', nextWeekEvents);
      
      loadingStatus = 'Veranstaltungen geladen';
      isLoading = false;
      
      // Generate post text and image
      generatePostText();
      // Wait a tick for canvas to mount
      setTimeout(() => generateImage(), 50);
    } catch (error) {
      loadingStatus = `Fehler beim Laden: ${error.message}`;
      errorMessage = error.message;
      hasError = true;
      isLoading = false;
      console.error('Fehler beim Laden der Daten:', error);
    }
  });

  // Helper: format date as "Montag, 03.04.2025"
  function formatDateLong(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const options = { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric' };
    return date.toLocaleDateString('de-DE', options);
  }

  // Helper: format time as "HH:mm"
  function formatTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
  }

  // Weekday separator
  const weekdayMarker = '—';

  // Group events by weekday
  function groupEventsByWeekday(events) {
    const groups = {};
    for (const event of events) {
      if (!event.start_date) continue;
      const date = new Date(event.start_date);
      const weekday = date.toLocaleDateString('de-DE', { weekday: 'long' });
      if (!groups[weekday]) groups[weekday] = [];
      groups[weekday].push(event);
    }
    // Sort events within each weekday by start time
    for (const day in groups) {
      groups[day].sort((a, b) => new Date(a.start_date) - new Date(b.start_date));
    }
    return groups;
  }

  // Generate the LinkedIn post text
  function generatePostText() {
    if (!nextWeekEvents || nextWeekEvents.length === 0) {
      postText.set('Keine Veranstaltungen für die nächste Woche gefunden.');
      return;
    }

    const groups = groupEventsByWeekday(nextWeekEvents);

    let text = `Digitalisierung im Non-Profit-Bereich – ${nextWeekEvents.length} Interessante Veranstaltungen in der kommenden Woche!\n\n\n`;
    text += `Webinare, Workshops und Seminare für gemeinnützige Organisationen diese Woche auf digikal.org:\n\n\n`;

    // Sort weekdays in calendar order
    const weekdayOrder = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'];

    let firstDay = true;
    for (const day of weekdayOrder) {
      if (!groups[day]) continue;
      const firstEventDate = new Date(groups[day][0].start_date);
      const dateStr = firstEventDate.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' });

      if (!firstDay) text += '\n\n';
      text += `${day}, ${dateStr}\n---\n`;
      firstDay = false;

      for (let i = 0; i < groups[day].length; i++) {
        const event = groups[day][i];
        const timeStr = formatTime(event.start_date);
        const title = event.title || 'Kein Titel';
        const organizer = event.organizer || event.source || '';
        const location = event.location || 'Online';
        const link = event.website || event.register_link || '';

        // Cost info
        let costText = '';
        if (event.cost !== undefined && event.cost !== null && event.cost !== '') {
          if (event.cost === 0 || event.cost === '0' ||
              event.cost === 'kostenlos' || event.cost === 'Kostenlos' ||
              event.cost === 'free' || event.cost === 'Free') {
            costText = 'Kostenlos';
          } else {
            costText = typeof event.cost === 'number' ? `${event.cost} €` : event.cost;
          }
        }

        let details = `${timeStr} Uhr`;
        if (organizer) details += ` · ${organizer}`;
        details += ` · ${location}`;
        if (costText) details += ` · ${costText}`;

        text += `\n${title}\n`;
        text += `${details}\n`;
        if (link) text += `${link}\n`;

        if (i < groups[day].length - 1) text += '\n\n';
      }
    }

    text += `\n\n\n---\n\n\n`;
    text += `Alle Veranstaltungen, Kalender-Abo und Förderprogramme für Nonprofits:\n`;
    text += `https://digikal.org\n\n`;
    text += `#nonprofit #digitalisierung #ehrenamt #ngos #weiterbildung`;

    postText.set(text);
  }

  // --- Image generator ---
  let imageCanvas;
  let imageUrl = '';

  function getDateRange() {
    if (!nextWeekEvents || nextWeekEvents.length === 0) return { start: '', end: '' };
    const dates = nextWeekEvents.map(e => new Date(e.start_date));
    const min = new Date(Math.min(...dates));
    const max = new Date(Math.max(...dates));
    const fmt = d => `${d.getDate().toString().padStart(2, '0')}.${(d.getMonth() + 1).toString().padStart(2, '0')}.`;
    return { start: fmt(min), end: fmt(max), year: max.getFullYear() };
  }

  function generateImage() {
    const canvas = imageCanvas;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 1080;
    const R = 40;
    canvas.width = W;
    canvas.height = H;

    // White background with rounded corners
    ctx.fillStyle = '#ffffff';
    roundRect(ctx, 0, 0, W, H, R);
    ctx.fill();

    // Blue card inset
    const pad = 60;
    const cardR = 24;
    const grad = ctx.createLinearGradient(pad, pad, W - pad, H - pad);
    grad.addColorStop(0, '#2563eb');
    grad.addColorStop(1, '#3178ff');
    ctx.fillStyle = grad;
    roundRect(ctx, pad, pad, W - pad * 2, H - pad * 2, cardR);
    ctx.fill();

    // Subtle decorative circles
    ctx.save();
    roundRect(ctx, pad, pad, W - pad * 2, H - pad * 2, cardR);
    ctx.clip();
    ctx.globalAlpha = 0.06;
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(800, 180, 200, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(880, 850, 160, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    const x = pad + 60;

    // DigiKal logo text
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 80px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillText('DigiKal', x, 230);

    // digikal.org below logo
    ctx.font = '30px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.globalAlpha = 0.7;
    ctx.fillText('digikal.org', x, 280);
    ctx.globalAlpha = 1;

    // Divider line
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, 320);
    ctx.lineTo(x + 350, 320);
    ctx.stroke();

    // Subline
    ctx.font = '32px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.globalAlpha = 0.85;
    ctx.fillStyle = '#ffffff';
    ctx.fillText('Webinare, Workshops & Seminare', x, 400);
    ctx.fillText('für gemeinnützige Organisationen', x, 445);
    ctx.globalAlpha = 1;

    // Main date line
    const { start, end, year } = getDateRange();
    const dateLine = start && end ? `Events in der Woche` : 'Events der kommenden Woche';
    const dateLine2 = start && end ? `vom ${start} – ${end}${year}` : '';

    ctx.font = 'bold 52px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(dateLine, x, 580);
    if (dateLine2) {
      ctx.fillText(dateLine2, x, 645);
    }

    // Event count badge
    if (eventsCount > 0) {
      const countText = `${eventsCount} Veranstaltungen`;
      ctx.font = 'bold 34px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      const metrics = ctx.measureText(countText);
      const badgeW = metrics.width + 48;
      const badgeH = 56;
      const badgeX = x;
      const badgeY = 700;

      ctx.fillStyle = 'rgba(255,255,255,0.15)';
      roundRect(ctx, badgeX, badgeY, badgeW, badgeH, 28);
      ctx.fill();

      ctx.fillStyle = '#ffffff';
      ctx.fillText(countText, badgeX + 24, badgeY + 40);
    }

    imageUrl = canvas.toDataURL('image/png');
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  function downloadImage() {
    if (!imageUrl) return;
    const a = document.createElement('a');
    const { start, end } = getDateRange();
    a.download = `digikal-linkedin-${start.replace(/\./g, '')}${end.replace(/\./g, '')}.png`;
    a.href = imageUrl;
    a.click();
  }

  // Copy post text to clipboard
  async function copyToClipboard() {
    const text = await new Promise(resolve => {
      postText.subscribe(value => resolve(value))();
    });
    try {
      await navigator.clipboard.writeText(text);
      alert('LinkedIn-Post wurde in die Zwischenablage kopiert!');
    } catch (err) {
      alert('Fehler beim Kopieren in die Zwischenablage.');
    }
  }

  // Refresh data
  async function refreshData() {
    try {
      isLoading = true;
      loadingStatus = 'Lade Veranstaltungen...';
      hasError = false;
      
      // Load all approved events directly from API
      allEvents = await getAllEvents();
      
      // Filter events for next week manually
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const dayOfWeek = today.getDay();
      const diff = dayOfWeek === 0 ? 1 : 8 - dayOfWeek; // Adjust for Sunday
      const startOfNextWeek = new Date(today);
      startOfNextWeek.setDate(today.getDate() + diff);
      const endOfNextWeek = new Date(startOfNextWeek);
      endOfNextWeek.setDate(startOfNextWeek.getDate() + 6);
      
      nextWeekEvents = allEvents.filter(event => {
        if (!event.start_date) return false;
        
        const eventDate = new Date(event.start_date);
        return eventDate >= startOfNextWeek && eventDate <= endOfNextWeek;
      });
      
      eventsCount = nextWeekEvents.length;
      loadingStatus = 'Veranstaltungen geladen';
      isLoading = false;
      
      // Generate post text and image
      generatePostText();
      setTimeout(() => generateImage(), 50);
    } catch (error) {
      loadingStatus = `Fehler beim Laden: ${error.message}`;
      errorMessage = error.message;
      hasError = true;
      isLoading = false;
      console.error('Fehler beim Laden der Daten:', error);
    }
  }
</script>

<div class="max-w-4xl mx-auto my-12 p-10 bg-white rounded-xl shadow-lg">
  <div class="flex justify-between items-center mb-8">
    <h1 class="text-3xl font-bold text-gray-800 pb-4 border-b-2 border-gray-100">LinkedIn-Post Generator</h1>
    <div class="bg-gray-100 px-4 py-2 rounded-lg text-sm text-gray-600">
      <span>Zeitraum: {nextWeekStart} bis {nextWeekEnd}</span>
    </div>
  </div>
  
  {#if isLoading}
    <div class="flex flex-col items-center justify-center py-12">
      <div class="w-10 h-10 border-4 border-gray-100 border-t-primary-600 rounded-full animate-spin mb-4"></div>
      <div class="text-primary-600 font-medium">{loadingStatus}</div>
    </div>
  {:else if hasError}
    <div class="bg-red-50 text-red-700 p-6 rounded-lg mb-6">
      <div class="font-semibold mb-2">Fehler beim Laden der Daten</div>
      <div>{errorMessage}</div>
      <button 
        class="mt-4 inline-flex items-center px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors gap-2 border border-gray-200"
        on:click={refreshData}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 2v6h-6"></path>
          <path d="M3 12a9 9 0 0 1 15-6.7L21 8"></path>
          <path d="M3 22v-6h6"></path>
          <path d="M21 12a9 9 0 0 1-15 6.7L3 16"></path>
        </svg>
        Erneut versuchen
      </button>
    </div>
  {:else}
    <textarea
      bind:value={$postText}
      class="w-full h-96 font-mono text-base p-6 border border-gray-200 rounded-lg resize-y mb-6 shadow-inner bg-gray-50 text-gray-800"
    ></textarea>
    
    <div class="flex gap-4 mb-6">
      <button 
        class="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors gap-2"
        on:click={copyToClipboard}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
        In Zwischenablage kopieren
      </button>
      
      <button 
        class="inline-flex items-center px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors gap-2 border border-gray-200"
        on:click={refreshData}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 2v6h-6"></path>
          <path d="M3 12a9 9 0 0 1 15-6.7L21 8"></path>
          <path d="M3 22v-6h6"></path>
          <path d="M21 12a9 9 0 0 1-15 6.7L3 16"></path>
        </svg>
        Aktualisieren
      </button>
      
      <div class="inline-flex items-center bg-blue-50 text-blue-800 px-4 py-2 rounded-full text-sm font-medium ml-auto">
        {eventsCount} Veranstaltungen gefunden
      </div>
    </div>
  {/if}
  
  {#if !isLoading && !hasError}
    <div class="mt-10 pt-8 border-t-2 border-gray-100">
      <h2 class="text-2xl font-bold text-gray-800 mb-6">Post-Bild</h2>

      <canvas bind:this={imageCanvas} style="display:none;"></canvas>

      {#if imageUrl}
        <div class="mb-6 rounded-lg overflow-hidden shadow-md border border-gray-200">
          <img src={imageUrl} alt="LinkedIn Post Bild" class="w-full" />
        </div>

        <div class="flex gap-4">
          <button
            class="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors gap-2"
            on:click={downloadImage}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Bild herunterladen
          </button>

          <button
            class="inline-flex items-center px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors gap-2 border border-gray-200"
            on:click={generateImage}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 2v6h-6"></path>
              <path d="M3 12a9 9 0 0 1 15-6.7L21 8"></path>
              <path d="M3 22v-6h6"></path>
              <path d="M21 12a9 9 0 0 1-15 6.7L3 16"></path>
            </svg>
            Neu generieren
          </button>
        </div>
      {:else}
        <p class="text-gray-500 text-sm">Bild wird generiert...</p>
      {/if}
    </div>
  {/if}
</div>
