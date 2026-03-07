<script>
	import { trackEvent } from '$lib/services/analytics';

	export let data;
	const { topic, topicConfig, events, foerdermittel } = data;

	let email = '';
	let honeypot = '';
	let nlStatus = 'idle';
	let nlError = '';

	async function handleNewsletterSubmit(e) {
		e.preventDefault();
		if (!email) return;
		if (honeypot) { nlStatus = 'success'; return; }
		nlStatus = 'submitting';
		nlError = '';
		try {
			const resp = await fetch('https://listmonk.buerofalk.de/api/public/subscription', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, list_uuids: ['c8997035-384b-4a40-aa92-939e978ad46f'] }),
			});
			if (resp.ok) {
				nlStatus = 'success';
				email = '';
				trackEvent('newsletter_signup');
			} else {
				const data = await resp.json().catch(() => null);
				nlError = data?.message || 'Anmeldung fehlgeschlagen. Bitte versuche es erneut.';
				nlStatus = 'error';
			}
		} catch {
			nlError = 'Netzwerkfehler. Bitte prüfe deine Internetverbindung.';
			nlStatus = 'error';
		}
	}

	const formatGroups = [
		{ key: 'Fortbildung', label: 'Fortbildungen', match: ['Fortbildung', 'Schulung', 'Seminar', 'Kurs'] },
		{ key: 'Workshop', label: 'Workshops', match: ['Workshop'] },
		{ key: 'Webinar', label: 'Webinare', match: ['Webinar', 'Online'] }
	];

	function getEventFormat(event) {
		if (!event.tag_groups) return null;
		const tg = typeof event.tag_groups === 'string' ? JSON.parse(event.tag_groups) : event.tag_groups;
		return tg.format || [];
	}

	function groupEvents(events) {
		const grouped = {};
		const ungrouped = [];

		for (const group of formatGroups) {
			grouped[group.key] = [];
		}

		for (const event of events) {
			const formats = getEventFormat(event);
			let placed = false;

			for (const group of formatGroups) {
				if (formats && formats.some(f => group.match.some(m => f.toLowerCase().includes(m.toLowerCase())))) {
					grouped[group.key].push(event);
					placed = true;
					break;
				}
			}

			if (!placed) {
				ungrouped.push(event);
			}
		}

		return { grouped, ungrouped };
	}

	const { grouped, ungrouped } = groupEvents(events);

	function formatDate(dateString) {
		if (!dateString) return '';
		const date = new Date(dateString);
		return new Intl.DateTimeFormat('de-DE', { day: '2-digit', month: 'long', year: 'numeric' }).format(date);
	}

	function extractTime(dateString) {
		if (!dateString || !dateString.includes('T')) return null;
		const d = new Date(dateString);
		const h = d.getHours(), m = d.getMinutes();
		if (h === 0 && m === 0) return null;
		return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
	}

	function getDeadlineText(program) {
		if (program.deadline_type === 'laufend') return 'Laufend';
		if (program.deadline_type === 'jaehrlich') return 'Jährlich';
		if (program.application_deadline) {
			return new Intl.DateTimeFormat('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(program.application_deadline));
		}
		return '';
	}

	function formatFundingAmount(program) {
		const fmt = (n) => new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format(n) + ' €';
		if (program.funding_amount_min && program.funding_amount_max) return `${fmt(program.funding_amount_min)} – ${fmt(program.funding_amount_max)}`;
		if (program.funding_amount_min) return `ab ${fmt(program.funding_amount_min)}`;
		if (program.funding_amount_max) return `bis ${fmt(program.funding_amount_max)}`;
		return '';
	}
</script>

<svelte:head>
	<title>{topicConfig.metaTitle}</title>
	<meta name="description" content={topicConfig.description} />
	<meta property="og:title" content={topicConfig.metaTitle} />
	<meta property="og:description" content={topicConfig.description} />
	<meta property="og:url" content="https://digikal.org/themen/{topic}" />
	<meta property="og:locale" content="de_DE" />
	<meta property="og:site_name" content="DigiKal" />
	<link rel="canonical" href="https://digikal.org/themen/{topic}" />

	{@html `<script type="application/ld+json">${JSON.stringify({
		"@context": "https://schema.org",
		"@type": "ItemList",
		"name": topicConfig.title + " – Veranstaltungen",
		"description": topicConfig.description,
		"numberOfItems": events.length,
		"itemListElement": events.map((event, i) => ({
			"@type": "ListItem",
			"position": i + 1,
			"item": {
				"@type": "Event",
				"name": event.title,
				"startDate": event.start_date,
				"location": { "@type": "Place", "name": event.location || "Online" },
				"organizer": { "@type": "Organization", "name": event.organizer || "" }
			}
		}))
	})}</script>`}
</svelte:head>

<main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<h1 class="text-3xl font-bold text-gray-900 mb-2">{topicConfig.title}</h1>
	<p class="text-gray-500 mb-10">{topicConfig.description}</p>

	<!-- Events grouped by format -->
	{#if events.length > 0}
		{#each formatGroups as group}
			{#if grouped[group.key].length > 0}
				<section class="mb-12">
					<h2 class="text-xl font-semibold text-gray-800 mb-5">{group.label}</h2>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-5">
						{#each grouped[group.key] as event}
							<a
								href={event.website || '#'}
								target={event.website ? '_blank' : undefined}
								rel={event.website ? 'noopener noreferrer' : undefined}
								class="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg hover:border-primary-300 transition-all group"
							>
								<div class="flex items-start gap-4">
									<div class="bg-primary-50 text-primary-700 px-3 py-2 rounded-lg text-center min-w-[3.5rem] flex-shrink-0">
										<div class="text-xl font-bold leading-tight">{new Date(event.start_date).getDate()}</div>
										<div class="text-xs font-medium">{new Date(event.start_date).toLocaleString('de-DE', { month: 'short' })}</div>
									</div>
									<div class="flex-grow min-w-0">
										<h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors leading-snug mb-1">{event.title}</h3>
										<div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-gray-500 mb-2">
											{#if extractTime(event.start_date)}
												<span>{extractTime(event.start_date)} Uhr</span>
											{/if}
											<span>{event.location || 'Online'}</span>
										</div>
										{#if event.organizer}
											<p class="text-xs text-gray-400 mb-2">{event.organizer}</p>
										{/if}
										{#if event.description}
											<div class="mt-1 text-sm text-gray-600 mehr-lesen">
												<p class="desc-preview line-clamp-2">{event.description}</p>
												<details>
													<summary class="cursor-pointer text-primary-600 hover:underline text-xs font-medium list-none mt-1">Mehr lesen</summary>
													<p class="mt-1">{event.description}</p>
												</details>
											</div>
										{/if}
									</div>
								</div>
							</a>
						{/each}
					</div>
				</section>
			{/if}
		{/each}

		<!-- Ungrouped events (Sonstige) -->
		{#if ungrouped.length > 0}
			<section class="mb-12">
				<h2 class="text-xl font-semibold text-gray-800 mb-5">Weitere Veranstaltungen</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-5">
					{#each ungrouped as event}
						<a
							href={event.website || '#'}
							target={event.website ? '_blank' : undefined}
							rel={event.website ? 'noopener noreferrer' : undefined}
							class="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg hover:border-primary-300 transition-all group"
						>
							<div class="flex items-start gap-4">
								<div class="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-center min-w-[3.5rem] flex-shrink-0">
									<div class="text-xl font-bold leading-tight">{new Date(event.start_date).getDate()}</div>
									<div class="text-xs font-medium">{new Date(event.start_date).toLocaleString('de-DE', { month: 'short' })}</div>
								</div>
								<div class="flex-grow min-w-0">
									<h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors leading-snug mb-1">{event.title}</h3>
									<div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-gray-500 mb-2">
										{#if extractTime(event.start_date)}
											<span>{extractTime(event.start_date)} Uhr</span>
										{/if}
										<span>{event.location || 'Online'}</span>
									</div>
									{#if event.organizer}
										<p class="text-xs text-gray-400 mb-2">{event.organizer}</p>
									{/if}
									{#if event.description}
										<p class="text-sm text-gray-600 ">{event.description}</p>
									{/if}
								</div>
							</div>
						</a>
					{/each}
				</div>
			</section>
		{/if}

		<a href="/" class="inline-block text-primary-600 hover:underline font-medium">
			Alle Veranstaltungen anzeigen &rarr;
		</a>
	{/if}

	<!-- Newsletter Signup -->
	<section class="bg-primary-50 rounded-xl p-8 mt-12 mb-12">
		<div class="max-w-md mx-auto text-center">
			<h2 class="text-xl font-semibold text-gray-800 mb-2">Newsletter abonnieren</h2>
			<p class="text-gray-600 mb-4 text-sm">Monatliche Übersicht der wichtigsten Veranstaltungen per E-Mail.</p>

			{#if nlStatus === 'success'}
				<p class="text-sm text-green-700">Danke! Bitte prüfe dein Postfach und bestätige deine Anmeldung.</p>
			{:else}
				{#if nlStatus === 'error'}
					<p class="text-sm text-red-600 mb-2">{nlError}</p>
				{/if}
				<form on:submit={handleNewsletterSubmit} class="flex flex-col sm:flex-row gap-2">
					<input type="text" name="website_url" bind:value={honeypot} style="position:absolute;left:-9999px;opacity:0;height:0;width:0;" tabindex="-1" autocomplete="off" />
					<input
						type="email"
						bind:value={email}
						placeholder="E-Mail-Adresse"
						required
						class="flex-grow px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
					/>
					<button
						type="submit"
						disabled={nlStatus === 'submitting'}
						class="px-5 py-2.5 bg-primary-600 text-white text-sm font-semibold rounded-lg hover:bg-primary-700 transition-colors whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{nlStatus === 'submitting' ? 'Wird gesendet...' : 'Abonnieren'}
					</button>
				</form>
			{/if}
		</div>
	</section>

	<!-- Förderprogramme Section -->
	{#if foerdermittel.length > 0}
		<section class="mt-16 mb-12">
			<h2 class="text-xl font-semibold text-gray-800 mb-5">Förderprogramme</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-5">
				{#each foerdermittel as program}
					<a
						href={program.primary_url || program.website || program.source_url || '#'}
						target={program.primary_url || program.website || program.source_url ? '_blank' : undefined}
						rel={program.primary_url || program.website || program.source_url ? 'noopener noreferrer' : undefined}
						class="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg hover:border-primary-300 transition-all group"
					>
						<h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors leading-snug mb-2">{program.title}</h3>
						<div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-gray-500 mb-2">
							{#if formatFundingAmount(program)}
								<span>{formatFundingAmount(program)}</span>
							{/if}
							{#if getDeadlineText(program)}
								<span>Frist: {getDeadlineText(program)}</span>
							{/if}
						</div>
						{#if program.funding_organization}
							<p class="text-xs text-gray-400 mb-2">{program.funding_organization}</p>
						{/if}
						{#if program.description}
							<div class="mt-1 text-sm text-gray-600 mehr-lesen">
								<p class="desc-preview line-clamp-2">{program.description}</p>
								<details>
									<summary class="cursor-pointer text-primary-600 hover:underline text-xs font-medium list-none mt-1">Mehr lesen</summary>
									<p class="mt-1">{program.description}</p>
								</details>
							</div>
						{/if}
					</a>
				{/each}
			</div>
			<a href="/foerderprogramme" class="inline-block mt-6 text-primary-600 hover:underline font-medium">
				Alle Förderprogramme anzeigen &rarr;
			</a>
		</section>
	{/if}

</main>
