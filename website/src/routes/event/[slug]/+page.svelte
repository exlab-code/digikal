<script>
	import EventCard from '$lib/components/EventCard.svelte';
	import { getEventTags, isEventPast, isEventArchived, eventPath } from '$lib/eventHelpers.js';
	import { getCategoryName } from '$lib/categoryMappings';

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
		organizer: event.organizer
			? { '@type': 'Organization', name: event.organizer }
			: undefined,
		offers: registerUrl
			? {
					'@type': 'Offer',
					price:
						!event.cost || event.cost === 'Kostenlos' || event.cost === '0'
							? '0'
							: event.cost,
					priceCurrency: 'EUR',
					availability: past
						? 'https://schema.org/SoldOut'
						: 'https://schema.org/InStock',
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
			{
				'@type': 'ListItem',
				position: 2,
				name: 'Veranstaltungen',
				item: 'https://www.digikal.org/'
			},
			{ '@type': 'ListItem', position: 3, name: event.title, item: canonicalUrl }
		]
	};
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

<main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumbs -->
	<nav aria-label="Brotkrumen" class="text-sm text-gray-500 mb-6">
		<ol class="flex flex-wrap items-center gap-1 list-none p-0">
			<li><a href="/" class="hover:text-primary-600 hover:underline">Start</a></li>
			<li aria-hidden="true" class="px-1">›</li>
			<li><a href="/" class="hover:text-primary-600 hover:underline">Veranstaltungen</a></li>
			<li aria-hidden="true" class="px-1">›</li>
			<li aria-current="page" class="text-gray-700 truncate max-w-xs">{event.title}</li>
		</ol>
	</nav>

	<article>
		{#if past}
			<div class="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-lg mb-6 text-sm">
				Diese Veranstaltung ist bereits beendet.
				{#if similar.length > 0}
					Schau dir <a href="#aehnliche" class="underline font-medium">ähnliche kommende Veranstaltungen</a> weiter unten an.
				{:else}
					<a href="/" class="underline font-medium">Aktuelle Veranstaltungen ansehen</a>.
				{/if}
			</div>
		{/if}

		<header class="mb-6">
			<h1 class="text-3xl sm:text-4xl font-bold text-gray-900 leading-tight mb-3">
				{event.title}
			</h1>

			<dl class="grid sm:grid-cols-2 gap-3 text-sm mt-4">
				<div>
					<dt class="text-gray-500 uppercase tracking-wide text-xs font-medium">Datum</dt>
					<dd class="text-gray-900">
						<time datetime={event.start_date}>{formatDate(event.start_date)}</time>
						{#if event.end_date && new Date(event.end_date).toDateString() !== new Date(event.start_date).toDateString()}
							– <time datetime={event.end_date}>{formatDate(event.end_date)}</time>
						{/if}
					</dd>
				</div>

				{#if startTime}
					<div>
						<dt class="text-gray-500 uppercase tracking-wide text-xs font-medium">Uhrzeit</dt>
						<dd class="text-gray-900">
							<time datetime={event.start_date}>{startTime}</time>
							{#if endTime}– <time datetime={event.end_date}>{endTime}</time>{/if} Uhr
						</dd>
					</div>
				{/if}

				<div>
					<dt class="text-gray-500 uppercase tracking-wide text-xs font-medium">Ort</dt>
					<dd class="text-gray-900">{locationLabel}</dd>
				</div>

				{#if event.cost !== undefined && event.cost !== null && event.cost !== ''}
					<div>
						<dt class="text-gray-500 uppercase tracking-wide text-xs font-medium">Kosten</dt>
						<dd class="text-gray-900">
							{#if event.cost === 0 || event.cost === '0' || event.cost === 'Kostenlos' || event.cost === 'kostenlos'}
								Kostenlos
							{:else}
								{typeof event.cost === 'number' ? `${event.cost} €` : event.cost}
							{/if}
						</dd>
					</div>
				{/if}

				{#if event.organizer}
					<div class="sm:col-span-2">
						<dt class="text-gray-500 uppercase tracking-wide text-xs font-medium">Veranstalter</dt>
						<dd class="text-gray-900">{event.organizer}</dd>
					</div>
				{/if}
			</dl>
		</header>

		{#if event.description}
			<section class="prose prose-sm max-w-none text-gray-700 leading-relaxed mb-8">
				<p>{event.description}</p>
			</section>
		{/if}

		{#if tags.length > 0}
			<section class="mb-8" aria-labelledby="tags-heading">
				<h2 id="tags-heading" class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">Themen</h2>
				<ul class="flex flex-wrap gap-2 list-none p-0">
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
					class="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors no-underline"
				>
					Zur Anmeldung beim Veranstalter
					<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path>
					</svg>
				</a>
				<p class="text-xs text-gray-500 mt-2">
					Die Anmeldung erfolgt direkt beim Veranstalter — DigiKal aggregiert nur und ist nicht Veranstalter.
				</p>
			</section>
		{/if}
	</article>

	{#if similar.length > 0}
		<aside id="aehnliche" aria-labelledby="similar-heading" class="border-t border-gray-200 pt-8">
			<h2 id="similar-heading" class="text-xl font-semibold text-gray-900 mb-4">
				Ähnliche Veranstaltungen
			</h2>
			<ul role="list" class="space-y-4 list-none p-0 m-0">
				{#each similar as e (e.id)}
					<li>
						<EventCard event={e} />
					</li>
				{/each}
			</ul>
		</aside>
	{/if}

	<nav class="mt-12 pt-6 border-t border-gray-200 text-sm">
		<a href="/" class="text-primary-600 hover:underline">← Alle Veranstaltungen</a>
	</nav>
</main>
