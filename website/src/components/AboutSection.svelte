<script>
  import Accordion from './Accordion.svelte';
  
  let isAboutOpen = false;
</script>

<div class="bg-white rounded-lg shadow">
  <Accordion 
    title="Über diesen Kalender" 
    defaultOpen={false} 
    mobileOnly={true}
    id="about"
    on:toggle={({ detail }) => isAboutOpen = detail.isOpen}
  >
    <p class="text-sm text-gray-600 mb-3">Dieser Kalender sammelt Digitalisierungsveranstaltungen, die speziell für gemeinnützige Organisationen relevant sind. Die Veranstaltungen decken Themen wie digitales Fundraising, Website-Entwicklung, Datenmanagement und mehr ab.</p>
    <p class="text-sm text-gray-600 mb-3">Alle Veranstaltungen werden von unserem Team geprüft und freigegeben, um sicherzustellen, dass sie für den gemeinnützigen Sektor wertvoll sind.</p>

    <h4 class="text-sm font-semibold text-gray-700 mb-2">Quellen</h4>
    <ul class="text-sm text-gray-600 space-y-1">
      <li><a href="https://www.hausdesstiftens.org/non-profits/wissen/webinare/" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Stifter-helfen.de</a></li>
      <li><a href="https://www.deutsche-stiftung-engagement-und-ehrenamt.de/veranstaltungen/liste/" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Deutsche Stiftung für Engagement und Ehrenamt</a></li>
      <li><a href="https://eveeno.com/138543290" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Aktion Zivilcourage</a></li>
      <li><a href="https://smart-service-bw.de/veranstaltungen/" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Smart Services BW</a></li>
      <li><a href="https://bitkom-akademie.de/seminare" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Bitkom Akademie</a></li>
      <li><a href="https://opentransfer.de/event/" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Open Transfer</a></li>
      <li><a href="https://www.skala-campus.org/termine/" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Skala Campus</a></li>
      <li><a href="https://www.iao.fraunhofer.de/de/veranstaltungen.html" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Fraunhofer IAO</a></li>
      <li><a href="https://stiftungdatenschutz.org/ehrenamt/webinare" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Stiftung Datenschutz</a></li>
      <li><a href="https://www.buergergesellschaft.de/mitteilen/nuetzliches/veranstaltungskalender" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Wegweiser Bürgergesellschaft</a></li>
      <li><a href="https://www.der-paritaetische.de/veranstaltungen/" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Paritätischer Wohlfahrtsverband</a></li>
      <li><a href="https://initiatived21.de/veranstaltungen" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Initiative D21</a></li>
      <li><a href="https://www.dfrv.de/veranstaltungen/" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Deutscher Fundraising Verband</a></li>
    </ul>
  </Accordion>
</div>
