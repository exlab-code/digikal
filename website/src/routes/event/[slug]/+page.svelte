<script>
	import EventCard from '$lib/components/EventCard.svelte';
	import { getEventTags, isEventPast, isEventArchived, eventPath } from '$lib/eventHelpers.js';

	export let data;

	$: event = data.event;
	$: similar = data.similar;
	$: canonicalUrl = `https://www.digikal.org${data.canonicalPath}`;
	$: tags = getEventTags(event);
	$: past = isEventPast(event);
	$: archived = isEventArchived(event, 90);
	$: registerUrl = event.website || event.register_link || null;

	$: locationLabel = event.location && event.location !== 'Online' ? event.location : 'Online';
	$: isOnline = !event.location || event.location === 'Online';

	function formatDate(iso) {
		if (!iso) return '';
		return new Intl.DateTimeFormat('de-DE', {
			weekday: 'long',
			day: '2-digit',
			month: 'long',
			year: 'numeric'
		}).format(new Date(iso));
	}

	function formatTime(iso) {
		if (!iso || !iso.includes('T')) return null;
		const d = new Date(iso);
		const h = d.getHours();
		const m = d.getMinutes();
		if (h === 0 && m === 0) return null;
		return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
	}

	function trackOutbound() {
		if (typeof umami !== 'undefined' && registerUrl) {
			umami.track('event-detail-click', {
				title: event.title,
				url: registerUrl
			});
		}
	}

	$: startTime = formatTime(event.start_date);
	$: endTime = formatTime(event.end_date);

	$: metaTitle = `${event.title} – DigiKal`;
	$: metaDescription = (event.description || `Veranstaltung am ${formatDate(event.start_date)}: ${event.title}.`).slice(0, 158);

	$: jsonLdEvent = {
		'@context': 'https://schema.org',
		'@type': 'Event',
		name: event.title,
		description: event.description || undefined,
		startDate: event.start_date,
		endDate: event.end_date || undefined,
		eventStatus: past ? 'https://schema.org/EventCompleted' : 'https://schema.org/EventScheduled',
		eventAttendanceMode: isOnline
			? 'https://schema.org/OnlineEventAttendanceMode'
			: 'https://schema.org/OfflineEventAttendanceMode',
		location: isOnline
			? { '@type': 'VirtualLocation', url: registerUrl || canonicalUrl }
			: { '@type': 'Place', name: event.location },
		organizer: event.organizer ? { '@type': 'Organization', name: event.organizer } : undefined,
		offers: registerUrl
			? {
					'@type': 'Offer',
					price:
						!event.cost || event.cost === 'Kostenlos' || event.cost === '0' ? '0' : event.cost,
					priceCurrency: 'EUR',
					availability: past ? 'https://schema.org/SoldOut' : 'https://schema.org/InStock',
					url: registerUrl
				}
			: undefined,
		url: canonicalUrl,
		isAccessibleForFree:
			!event.cost ||
			event.cost === 'Kostenlos' ||
			event.cost === '0' ||
			event.cost === 0
	};

	$: jsonLdBreadcrumb = {
		'@context': 'https://schema.org',
		'@type': 'BreadcrumbList',
		itemListElement: [
			{ '@type': 'ListItem', position: 1, name: 'Start', item: 'https://www.digikal.org/' },
			{ '@type': 'ListItem', position: 2, name: 'Veranstaltungen', item: 'https://www.digikal.org/' },
			{ '@type': 'ListItem', position: 3, name: event.title, item: canonicalUrl }
		]
	};

	function costLabel(cost) {
		if (cost === undefined || cost === null || cost === '') return null;
		if (cost === 0 || cost === '0' || cost === 'Kostenlos' || cost === 'kostenlos') return 'Kostenlos';
		return typeof cost === 'number' ? `${cost} €` : cost;
	}

	$: cost = costLabel(event.cost);
</script>

<svelte:head>
	<title>{metaTitle}</title>
	<meta name="description" content={metaDescription} />
	<link rel="canonical" href={canonicalUrl} />
	{#if archived}
		<meta name="robots" content="noindex, follow" />
	{/if}

	<meta property="og:type" content="event" />
	<meta property="og:title" content={metaTitle} />
	<meta property="og:description" content={metaDescription} />
	<meta property="og:url" content={canonicalUrl} />
	<meta property="og:locale" content="de_DE" />
	<meta property="og:site_name" content="DigiKal" />

	{@html `<script type="application/ld+json">${JSON.stringify(jsonLdEvent)}</script>`}
	{@html `<script type="application/ld+json">${JSON.stringify(jsonLdBreadcrumb)}</script>`}
</svelte:head>

<div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<nav aria-label="Brotkrumen" class="text-sm text-gray-500 mb-6">
		<a href="/" class="hover:text-primary-600 hover:underline">Start</a>
		<span class="px-1.5">›</span>
		<a href="/" class="hover:text-primary-600 hover:underline">Veranstaltungen</a>
	</nav>

	<article>
		<h1 class="text-3xl font-bold text-gray-900 mb-2">{event.title}</h1>
		<p class="text-gray-500 mb-10">
			<time datetime={event.start_date}>{formatDate(event.start_date)}</time>
			{#if event.end_date && new Date(event.end_date).toDateString() !== new Date(event.start_date).toDateString()}
				– <time datetime={event.end_date}>{formatDate(event.end_date)}</time>
			{/if}
			{#if startTime}
				· <time datetime={event.start_date}>{startTime}</time>{#if endTime}–<time datetime={event.end_date}>{endTime}</time>{/if} Uhr
			{/if}
			· {locationLabel}
		</p>

		{#if past}
			<div class="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-5 mb-10 text-sm">
				Diese Veranstaltung ist bereits beendet.
				{#if similar.length > 0}
					Schau dir <a href="#aehnliche" class="font-medium hover:underline">ähnliche kommende Veranstaltungen</a> weiter unten an.
				{:else}
					<a href="/" class="font-medium hover:underline">Aktuelle Veranstaltungen ansehen</a>.
				{/if}
			</div>
		{/if}

		<section class="mb-10">
			<h2 class="text-xl font-semibold text-gray-800 mb-3">Details</h2>
			<div class="bg-gray-50 rounded-lg p-5 text-sm text-gray-600 leading-relaxed">
				<div class="grid grid-cols-1 sm:grid-cols-[120px_1fr] gap-y-2 gap-x-4">
					<span class="font-medium text-gray-700">Datum</span>
					<span>
						<time datetime={event.start_date}>{formatDate(event.start_date)}</time>
						{#if event.end_date && new Date(event.end_date).toDateString() !== new Date(event.start_date).toDateString()}
							– <time datetime={event.end_date}>{formatDate(event.end_date)}</time>
						{/if}
					</span>

					{#if startTime}
						<span class="font-medium text-gray-700">Uhrzeit</span>
						<span>
							<time datetime={event.start_date}>{startTime}</time>{#if endTime}
								– <time datetime={event.end_date}>{endTime}</time>
							{/if} Uhr
						</span>
					{/if}

					<span class="font-medium text-gray-700">Ort</span>
					<span>{locationLabel}</span>

					{#if cost}
						<span class="font-medium text-gray-700">Kosten</span>
						<span>{cost}</span>
					{/if}

					{#if event.organizer}
						<span class="font-medium text-gray-700">Veranstalter</span>
						<span>{event.organizer}</span>
					{/if}
				</div>
			</div>
		</section>

		{#if event.description}
			<section class="mb-10">
				<h2 class="text-xl font-semibold text-gray-800 mb-3">Beschreibung</h2>
				<p class="text-gray-600 leading-relaxed whitespace-pre-line">{event.description}</p>
			</section>
		{/if}

		{#if tags.length > 0}
			<section class="mb-10">
				<h2 class="text-xl font-semibold text-gray-800 mb-3">Themen</h2>
				<ul class="flex flex-wrap gap-2 list-none p-0 m-0">
					{#each tags.slice(0, 10) as tag}
						<li>
							<span class="inline-block bg-gray-100 text-gray-700 text-sm rounded-full px-3 py-1">{tag}</span>
						</li>
					{/each}
				</ul>
			</section>
		{/if}

		{#if registerUrl && !past}
			<section class="mb-10">
				<a
					href={registerUrl}
					target="_blank"
					rel="noopener noreferrer"
					on:click={trackOutbound}
					class="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-semibold px-5 py-3 rounded-lg transition-colors no-underline"
				>
					Zur Anmeldung beim Veranstalter
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
						<path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
						<path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
					</svg>
				</a>
				<p class="text-xs text-gray-500 mt-2">
					Die Anmeldung erfolgt direkt beim Veranstalter. DigiKal ist nicht Veranstalter, sondern aggregiert nur.
				</p>
			</section>
		{/if}
	</article>

	{#if similar.length > 0}
		<section id="aehnliche" class="mb-10">
			<h2 class="text-xl font-semibold text-gray-800 mb-3">Ähnliche Veranstaltungen</h2>
			<ul role="list" class="space-y-4 list-none p-0 m-0">
				{#each similar as e (e.id)}
					<li><EventCard event={e} /></li>
				{/each}
			</ul>
		</section>
	{/if}

	<p class="text-sm">
		<a href="/" class="text-primary-600 hover:underline">← Alle Veranstaltungen</a>
	</p>
</div>
