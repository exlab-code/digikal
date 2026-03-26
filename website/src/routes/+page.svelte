<script>
	import { onMount } from 'svelte';
	import EventList from '$lib/components/EventList.svelte';
	import EventFilter from '$lib/components/EventFilter.svelte';
	import NewsletterSignup from '$lib/components/NewsletterSignup.svelte';
	import { events, calendarUrls } from '$lib/stores/eventStore';

	export let data;

	// Initialize stores from prerendered data (for SEO / initial paint)
	events.set(data.events);
	calendarUrls.set(data.calendarUrls);

	// Re-fetch fresh events on the client so visitors always see the latest data
	onMount(async () => {
		try {
			const params = new URLSearchParams({
				filter: JSON.stringify({ review_status: { _eq: 'approved' } }),
				sort: 'start_date',
				limit: '-1'
			});
			const res = await fetch(`https://calapi.buerofalk.de/items/events?${params}`);
			if (res.ok) {
				const json = await res.json();
				events.set(json.data || []);
			}
		} catch (e) {
			// Keep prerendered data on failure
		}
	});
</script>

<svelte:head>
	<title>DigiKal – Digitalisierungsveranstaltungen für Nonprofits</title>
	<meta name="description" content="Veranstaltungskalender und Förderprogramme für gemeinnützige Organisationen in Deutschland. Finde Webinare, Workshops und Förderungen zu Digitalisierung, Fundraising und mehr." />

	<meta property="og:type" content="website" />
	<meta property="og:title" content="DigiKal – Digitalisierungsveranstaltungen für Nonprofits" />
	<meta property="og:description" content="Veranstaltungskalender und Förderprogramme für gemeinnützige Organisationen in Deutschland." />
	<meta property="og:url" content="https://digikal.org/" />
	<meta property="og:locale" content="de_DE" />
	<meta property="og:site_name" content="DigiKal" />

	<link rel="canonical" href="https://digikal.org/" />

	{@html `<script type="application/ld+json">${JSON.stringify({
		"@context": "https://schema.org",
		"@type": "WebSite",
		"name": "DigiKal",
		"url": "https://digikal.org/",
		"description": "Veranstaltungskalender und Förderprogramme für gemeinnützige Organisationen in Deutschland.",
		"inLanguage": "de",
		"publisher": {
			"@type": "Organization",
			"name": "ex:lab"
		}
	})}</script>`}
</svelte:head>

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
		<aside class="lg:col-span-1 space-y-6">
			<NewsletterSignup />
			<EventFilter defaultOpen={true} />
		</aside>

		<div class="lg:col-span-3">
			<EventList />
		</div>
	</div>
</main>
