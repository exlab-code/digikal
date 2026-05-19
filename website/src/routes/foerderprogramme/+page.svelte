<script>
	import { onMount } from 'svelte';
	import FoerderprogrammList from '$lib/components/FoerderprogrammList.svelte';
	import FoerderprogrammFilter from '$lib/components/FoerderprogrammFilter.svelte';
	import McpServerCard from '$lib/components/McpServerCard.svelte';
	import FoerdermittelAbout from '$lib/components/FoerdermittelAbout.svelte';
	import { foerdermittel } from '$lib/stores/foerdermittelStore';
	import { activeAccordionId } from '$lib/stores/accordionStore';

	export let data;

	// Initialize store from server-loaded data
	foerdermittel.set(data.foerdermittel);

	onMount(() => {
		if (window.innerWidth >= 768) {
			activeAccordionId.set('filter');
		}
	});
</script>

<svelte:head>
	<title>Förderprogramme für Nonprofits – DigiKal</title>
	<meta name="description" content="Über 3.000 Förderprogramme für gemeinnützige Organisationen in Deutschland. Finde passende Förderungen nach Thema, Region und Fördersumme." />
	<link rel="canonical" href="https://www.digikal.org/foerderprogramme" />

	<meta property="og:type" content="website" />
	<meta property="og:title" content="Förderprogramme für Nonprofits – DigiKal" />
	<meta property="og:description" content="Über 3.000 Förderprogramme für gemeinnützige Organisationen in Deutschland." />
	<meta property="og:url" content="https://www.digikal.org/foerderprogramme" />
	<meta property="og:locale" content="de_DE" />
	<meta property="og:site_name" content="DigiKal" />

	{@html `<script type="application/ld+json">${JSON.stringify({
		"@context": "https://schema.org",
		"@type": "Dataset",
		"name": "DigiKal Förderdatenbank",
		"description": "Strukturierte Datenbank mit über 3.000 Förderprogrammen für gemeinnützige Organisationen in Deutschland. Filterbar nach Thema, Region und Fördersumme.",
		"url": "https://www.digikal.org/foerderprogramme",
		"inLanguage": "de",
		"keywords": ["Förderprogramme", "Nonprofit", "Gemeinnützige Organisationen", "Förderung", "Deutschland", "Digitalisierung"],
		"creator": {
			"@type": "Organization",
			"name": "ex:lab",
			"url": "https://ex-lab.de"
		},
		"isAccessibleForFree": true,
		"license": "https://github.com/exlab-code/digikal",
		"distribution": [
			{
				"@type": "DataDownload",
				"encodingFormat": "application/json",
				"contentUrl": "https://www.digikal.org/foerdermittel.json"
			}
		]
	})}</script>`}

	{@html `<script type="application/ld+json">${JSON.stringify({
		"@context": "https://schema.org",
		"@type": "ItemList",
		"name": "Förderprogramme für Nonprofits",
		"description": "Übersicht aktueller Förderprogramme für gemeinnützige Organisationen in Deutschland.",
		"numberOfItems": data.foerdermittel.length,
		"itemListElement": data.foerdermittel.slice(0, 20).map((program, i) => ({
			"@type": "ListItem",
			"position": i + 1,
			"item": {
				"@type": "Grant",
				"name": program.title,
				"description": program.description || undefined,
				"url": program.source_url || undefined,
				"funder": program.funding_organization ? { "@type": "Organization", "name": program.funding_organization } : undefined
			}
		}))
	})}</script>`}
</svelte:head>

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<h1 class="sr-only">Förderprogramme für gemeinnützige Organisationen in Deutschland</h1>

	<div class="grid grid-cols-1 lg:grid-cols-[2fr_5fr] gap-8">
		<aside class="space-y-6" aria-labelledby="foerder-aside-heading">
			<h2 id="foerder-aside-heading" class="sr-only">MCP-Server, Filter und Hintergrund</h2>
			<McpServerCard />
			<FoerderprogrammFilter defaultOpen={true} />
			<FoerdermittelAbout defaultOpen={false} />
		</aside>

		<div aria-labelledby="foerder-list-heading">
			<h2 id="foerder-list-heading" class="sr-only">Aktuelle Förderprogramme</h2>
			<FoerderprogrammList />
		</div>
	</div>
</main>
