<script>
  import { calendarUrls } from '$lib/stores/eventStore';
  import Accordion from './Accordion.svelte';
  import { trackEvent } from '$lib/services/analytics';
  
  let copySuccess = false;
  let copyTimeout;
  let isSubscriptionOpen = false;
  
  function copyToClipboard(url) {
    navigator.clipboard.writeText(url)
      .then(() => {
        copySuccess = true;
        
        // Clear any existing timeout
        if (copyTimeout) clearTimeout(copyTimeout);
        
        // Reset after 3 seconds
        copyTimeout = setTimeout(() => {
          copySuccess = false;
        }, 3000);
        
        // Track calendar subscription copy event
        trackEvent('calendar_subscription_copy', { url });
      })
      .catch(err => {
        console.error('Fehler beim Kopieren in die Zwischenablage:', err);
        alert('Fehler beim Kopieren in die Zwischenablage. Bitte manuell kopieren.');
      });
  }
</script>

<div class="bg-white rounded-lg shadow">
  <Accordion 
    title="Kalender abonnieren" 
    defaultOpen={false} 
    mobileOnly={true}
    id="calendar"
    on:toggle={({ detail }) => isSubscriptionOpen = detail.isOpen}
  >
    <p class="text-gray-600 mb-4 text-sm">Füge diese Veranstaltungen zu deinem persönlichen Kalender hinzu:</p>
  
  <div class="flex flex-col gap-3">
    {#if $calendarUrls.ical}
      <button
        on:click={() => copyToClipboard('https://digikal.org/calendar.ics')}
        class="flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        {copySuccess ? 'URL kopiert!' : 'Kalender-URL kopieren'}
      </button>
      <a
        href={$calendarUrls.ical}
        download="digikal-events.ics"
        class="flex items-center justify-center gap-2 px-4 py-3 bg-gray-100 text-gray-700 font-medium rounded-md hover:bg-gray-200 transition-colors text-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        .ics herunterladen
      </a>
    {/if}
  </div>
  </Accordion>
</div>
