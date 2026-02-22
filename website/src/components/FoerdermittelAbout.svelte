<script>
  import Accordion from './Accordion.svelte';
</script>

<div class="bg-white rounded-lg shadow">
  <Accordion
    title="Über die Förderdatenbank"
    defaultOpen={false}
    mobileOnly={true}
    id="foerdermittel-about"
  >
    <p class="text-sm text-gray-600 mb-3">Diese Datenbank aggregiert Förderprogramme für gemeinnützige Organisationen in Deutschland aus verschiedenen Quellen. Die Daten werden regelmäßig aktualisiert.</p>

    <h4 class="text-sm font-semibold text-gray-700 mb-2">Quellen</h4>
    <ul class="text-sm text-gray-600 space-y-1">
      <li><a href="https://www.foerderdatenbank.de" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Förderdatenbank des Bundes</a></li>
      <li><a href="https://foerderdatenbank.d-s-e-e.de" target="_blank" rel="noopener" class="text-blue-600 hover:underline">DSEE Förderdatenbank</a></li>
    </ul>
  </Accordion>
</div>
