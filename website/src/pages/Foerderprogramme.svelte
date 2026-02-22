<script>
  import { onMount } from 'svelte';
  import FoerderprogrammList from '../components/FoerderprogrammList.svelte';
  import FoerderprogrammFilter from '../components/FoerderprogrammFilter.svelte';
  import McpServerCard from '../components/McpServerCard.svelte';
  import FoerdermittelAbout from '../components/FoerdermittelAbout.svelte';
  import { initializeData } from '../stores/foerdermittelStore';

  onMount(() => {
    initializeData();
  });
</script>

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
    <aside class="lg:col-span-1 space-y-6">
      <McpServerCard />
      <FoerderprogrammFilter defaultOpen={true} />
      <FoerdermittelAbout defaultOpen={false} />
    </aside>

    <div class="lg:col-span-3">
      <FoerderprogrammList />
    </div>
  </div>
</main>
