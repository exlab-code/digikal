<script>
  import { calendarUrls } from '$lib/stores/eventStore';
  import Accordion from './Accordion.svelte';
  import { trackEvent } from '$lib/services/analytics';

  let email = '';
  let honeypot = '';
  let status = 'idle'; // idle | submitting | success | error
  let errorMsg = '';
  let copySuccess = false;
  let copyTimeout;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email) return;
    // Honeypot: bots fill hidden fields, humans don't
    if (honeypot) {
      status = 'success';
      return;
    }
    status = 'submitting';
    errorMsg = '';
    try {
      const resp = await fetch('https://listmonk.buerofalk.de/api/public/subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          list_uuids: ['c8997035-384b-4a40-aa92-939e978ad46f'],
        }),
      });
      if (resp.ok) {
        status = 'success';
        email = '';
        trackEvent('newsletter_signup');
      } else {
        const data = await resp.json().catch(() => null);
        errorMsg = data?.message || 'Anmeldung fehlgeschlagen. Bitte versuche es erneut.';
        status = 'error';
      }
    } catch {
      errorMsg = 'Netzwerkfehler. Bitte prüfe deine Internetverbindung.';
      status = 'error';
    }
  }

  function copyToClipboard(url) {
    navigator.clipboard.writeText(url)
      .then(() => {
        copySuccess = true;
        if (copyTimeout) clearTimeout(copyTimeout);
        copyTimeout = setTimeout(() => { copySuccess = false; }, 3000);
        trackEvent('calendar_subscription_copy', { url });
      })
      .catch(() => {
        alert('Fehler beim Kopieren. Bitte manuell kopieren.');
      });
  }
</script>

<div class="bg-white rounded-lg shadow">
  <Accordion
    title="Abonnieren"
    defaultOpen={true}
    mobileOnly={true}
    id="newsletter"
  >
    {#if status === 'success'}
      <p class="text-sm text-green-700">Danke! Bitte pr&uuml;fe dein Postfach und best&auml;tige deine Anmeldung.</p>
    {:else}
      <p class="text-gray-600 mb-3 text-sm">Monatliche Übersicht der wichtigsten Veranstaltungen per E-Mail.</p>

      {#if status === 'error'}
        <p class="text-sm text-red-600 mb-2">{errorMsg}</p>
      {/if}

      <form on:submit={handleSubmit} class="flex flex-col gap-2">
        <!-- Honeypot: invisible to humans, bots fill it -->
        <input type="text" name="website_url" bind:value={honeypot} style="position:absolute;left:-9999px;opacity:0;height:0;width:0;" tabindex="-1" autocomplete="off" />
        <input
          type="email"
          bind:value={email}
          placeholder="E-Mail-Adresse"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={status === 'submitting'}
          class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status === 'submitting' ? 'Wird gesendet...' : 'Per E-Mail abonnieren'}
        </button>
      </form>
    {/if}

    {#if $calendarUrls.ical}
      <hr class="my-3 border-gray-200" />
      <button
        on:click={() => copyToClipboard('https://digikal.org/calendar.ics')}
        class="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        {copySuccess ? 'URL kopiert!' : '.ics abonnieren'}
      </button>
    {/if}
  </Accordion>
</div>
