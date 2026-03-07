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
	<link rel="canonical" href="https://digikal.org/foerderprogramme" />
</svelte:head>

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="grid grid-cols-1 lg:grid-cols-[2fr_5fr] gap-8">
		<aside class="space-y-6">
			<McpServerCard />
			<FoerderprogrammFilter defaultOpen={true} />
			<FoerdermittelAbout defaultOpen={false} />
		</aside>

		<div>
			<FoerderprogrammList />
		</div>
	</div>
</main>
