<script>
  import { onMount } from 'svelte';
  import FoerderprogrammList from '../components/FoerderprogrammList.svelte';
  import FoerderprogrammFilter from '../components/FoerderprogrammFilter.svelte';
  import AboutSection from '../components/AboutSection.svelte';
  import { initializeData } from '../stores/foerdermittelStore';
  import { activeAccordionId } from '../stores/accordionStore';

  onMount(() => {
    // Initialize all data when component mounts
    initializeData();

    // Set default open accordion on desktop
    if (window.innerWidth >= 768) {
      activeAccordionId.set('filter');
    } else {
      activeAccordionId.set(null);
    }
  });
</script>

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Prototype banner -->
  <div class="bg-yellow-50 border border-yellow-300 rounded-md px-4 py-3 mb-6 flex items-center gap-3 text-yellow-800">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="flex-shrink-0 text-yellow-600">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="8" x2="12" y2="12"></line>
      <line x1="12" y1="16" x2="12.01" y2="16"></line>
    </svg>
    <p><span class="font-medium">Prototyp:</span> Diese Liste ist unvollständig und dient nur zu Demonstrationszwecken.</p>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
    <aside class="lg:col-span-1 space-y-6">
      <FoerderprogrammFilter defaultOpen={true} />

      <AboutSection defaultOpen={false} />
    </aside>

    <div class="lg:col-span-3">
      <FoerderprogrammList />
    </div>
  </div>
</main>
