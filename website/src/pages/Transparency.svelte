<script>
  // Transparency page
</script>

<div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
  <h1 class="text-3xl font-bold text-gray-900 mb-2">&Uuml;ber DigiKal</h1>
  <p class="text-gray-500 mb-10">Woher die Daten kommen, was im Hintergrund passiert und wo der Code liegt.</p>

  <!-- What is DigiKal -->
  <section class="mb-10">
    <h2 class="text-xl font-semibold text-gray-800 mb-3">Was ist DigiKal?</h2>
    <p class="text-gray-600 leading-relaxed">
      DigiKal sammelt automatisch Digitalisierungsveranstaltungen und F&ouml;rderprogramme f&uuml;r gemeinn&uuml;tzige Organisationen in Deutschland. Alles Open Source, alles aus &ouml;ffentlich zug&auml;nglichen Quellen. Ein Projekt von Julius Falk / <a href="https://ex-lab.de" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:underline">ex:lab</a>.
    </p>
  </section>

  <!-- Veranstaltungskalender -->
  <section class="mb-10">
    <h2 class="text-xl font-semibold text-gray-800 mb-3">Veranstaltungskalender</h2>
    <p class="text-gray-600 mb-4">
      Python-Scraper lesen regelm&auml;&szlig;ig 12 Websites aus, eine KI kategorisiert die Events nach Thema, Format und Zielgruppe, und &uuml;ber eine Moderationsoberfl&auml;che (Directus) wird alles nochmal gepr&uuml;ft bevor es hier landet. Updates mehrmals t&auml;glich.
    </p>

    <div class="bg-gray-50 rounded-lg p-5">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">Quellen</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-sm text-gray-600">
        <span>Stifter-helfen.de / Haus des Stiftens</span>
        <span>Deutsche Stiftung f&uuml;r Engagement und Ehrenamt</span>
        <span>Aktion Zivilcourage</span>
        <span>Bitkom Akademie</span>
        <span>Open Transfer</span>
        <span>Skala Campus</span>
        <span>Fraunhofer IAO</span>
        <span>Stiftung Datenschutz</span>
        <span>Wegweiser B&uuml;rgergesellschaft</span>
        <span>Parit&auml;tischer Wohlfahrtsverband</span>
        <span>Initiative D21</span>
        <span>Deutscher Fundraising Verband</span>
      </div>
    </div>
  </section>

  <!-- Förderdatenbank -->
  <section class="mb-10">
    <h2 class="text-xl font-semibold text-gray-800 mb-3">F&ouml;rderdatenbank</h2>
    <p class="text-gray-600 mb-4">
      &Uuml;ber 3.000 F&ouml;rderprogramme aus zwei &ouml;ffentlichen Quellen. Die Rohdaten werden per LLM (Claude / GPT) angereichert &mdash; Kategorien, Zielgruppen, Fristen, Bundesland &mdash; und in einer SQLite-Datenbank mit Volltextsuche gespeichert. Ein MCP-Server macht die Daten f&uuml;r KI-Tools wie Claude, Copilot und Cursor zug&auml;nglich. Update alle ~2 Tage.
    </p>

    <div class="bg-gray-50 rounded-lg p-5">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">Datenquellen</h3>
      <div class="space-y-2 text-sm text-gray-600">
        <div>
          <span class="font-medium text-gray-700">F&ouml;rderdatenbank des Bundes</span> (foerderdatenbank.de)<br>
          <span class="text-gray-500">Rohdaten via <a href="https://correlaid.org" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:underline">CorrelAid e.V.</a> Open-Data-Dump</span>
        </div>
        <div>
          <span class="font-medium text-gray-700">DSEE F&ouml;rderdatenbank</span> (foerderdatenbank.d-s-e-e.de)<br>
          <span class="text-gray-500">Deutsche Stiftung f&uuml;r Engagement und Ehrenamt, &ouml;ffentliche Daten</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Tech & Code -->
  <section class="mb-10">
    <h2 class="text-xl font-semibold text-gray-800 mb-3">Code & Technik</h2>
    <p class="text-gray-600 mb-4">Alles quelloffen auf GitHub. Zwei Repos:</p>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
      <a href="https://github.com/exlab-code/digikal" target="_blank" rel="noopener noreferrer" class="block bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
        <p class="font-semibold text-gray-800 text-sm mb-1">exlab-code/digikal</p>
        <p class="text-xs text-gray-500 mb-2">Website, Event-Scraper, Moderation</p>
        <div class="flex flex-wrap gap-1">
          <span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">Svelte</span>
          <span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">Tailwind</span>
          <span class="text-xs px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded-full">Python</span>
        </div>
      </a>
      <a href="https://github.com/exlab-code/foerdermittel-mcp" target="_blank" rel="noopener noreferrer" class="block bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
        <p class="font-semibold text-gray-800 text-sm mb-1">exlab-code/foerdermittel-mcp</p>
        <p class="text-xs text-gray-500 mb-2">MCP-Server, Enrichment, REST-API</p>
        <div class="flex flex-wrap gap-1">
          <span class="text-xs px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded-full">Python</span>
          <span class="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full">FastAPI</span>
          <span class="text-xs px-2 py-0.5 bg-gray-200 text-gray-700 rounded-full">SQLite</span>
          <span class="text-xs px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full">MCP</span>
        </div>
      </a>
    </div>

    <!-- Architecture -->
    <div class="bg-gray-900 text-gray-300 rounded-lg p-4 overflow-x-auto font-mono text-xs sm:text-sm">
      <pre class="whitespace-pre">Veranstaltungen                    F&ouml;rderprogramme
──────────────                    ───────────────

12 Websites                      foerderdatenbank.de
     |                            foerderdatenbank.d-s-e-e.de
     v                                    |
Python Scraper                            v
     |                            Parquet-Download + DSEE-Scraper
     v                                    |
KI-Kategorisierung                        v
     |                            LLM-Anreicherung (Claude/GPT)
     v                                    |
Directus CMS                              v
(Moderation)                      SQLite + FTS5
     |                                    |
     v                            +-------+-------+
Kalender-API                      |               |
     |                        MCP Server      REST API
     v                            |               |
+----+----+                       v               v
|         |                   Claude, Copilot  Diese Website
Website  iCal-Abo             Cursor, GPTs     (Svelte SPA)</pre>
    </div>
  </section>

  <!-- Contact -->
  <section class="border-t border-gray-200 pt-8">
    <h2 class="text-xl font-semibold text-gray-800 mb-3">Kontakt</h2>
    <p class="text-gray-600 mb-4">
      Feedback, Quellenvorschl&auml;ge, Bugs oder einfach Hallo sagen:
    </p>
    <div class="flex flex-wrap gap-3">
      <a href="mailto:julius@ex-lab.de" class="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors text-sm">
        julius@ex-lab.de
      </a>
      <a href="https://github.com/exlab-code/digikal/issues" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors text-sm">
        GitHub Issue
      </a>
    </div>
  </section>
</div>
