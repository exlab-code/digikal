<script>
  import { onMount } from 'svelte';
  import FoerderprogrammList from '../components/FoerderprogrammList.svelte';
  import FoerderprogrammFilter from '../components/FoerderprogrammFilter.svelte';
  import McpServerCard from '../components/McpServerCard.svelte';
  import FoerdermittelAbout from '../components/FoerdermittelAbout.svelte';
  import { initializeData } from '../stores/foerdermittelStore';
  import { activeAccordionId } from '../stores/accordionStore';

  onMount(() => {
    initializeData();
    if (window.innerWidth >= 768) {
      activeAccordionId.set('filter');
    }
  });
</script>

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
