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

  <!-- Impressum -->
  <section class="border-t border-gray-200 pt-8 mt-10">
    <h2 class="text-xl font-semibold text-gray-800 mb-3">Impressum</h2>
    <div class="text-gray-600 text-sm leading-relaxed space-y-2">
      <p>Angaben gem&auml;&szlig; &sect; 5 TMG</p>
      <p>
        Julius Falk<br>
        ex:lab<br>
        Gubener Stra&szlig;e 43<br>
        10243 Berlin
      </p>
      <p>
        <span class="font-medium text-gray-700">Kontakt:</span><br>
        E-Mail: <a href="mailto:julius@ex-lab.de" class="text-primary-600 hover:underline">julius@ex-lab.de</a>
      </p>
      <p>
        <span class="font-medium text-gray-700">Verantwortlich f&uuml;r den Inhalt nach &sect; 55 Abs. 2 RStV:</span><br>
        Julius Falk
      </p>
      <div class="mt-4">
        <p class="font-medium text-gray-700 mb-1">Haftungsausschluss</p>
        <p>
          Die Inhalte dieser Website werden mit gr&ouml;&szlig;tm&ouml;glicher Sorgfalt erstellt. F&uuml;r die Richtigkeit, Vollst&auml;ndigkeit und Aktualit&auml;t der Inhalte &uuml;bernehmen wir jedoch keine Gew&auml;hr. Als Diensteanbieter sind wir gem&auml;&szlig; &sect; 7 Abs.&thinsp;1 TMG f&uuml;r eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach &sect;&sect; 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, &uuml;bermittelte oder gespeicherte fremde Informationen zu &uuml;berwachen. Bei Bekanntwerden von Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.
        </p>
      </div>
    </div>
  </section>

  <!-- Datenschutz -->
  <section class="border-t border-gray-200 pt-8 mt-10 mb-10">
    <h2 class="text-xl font-semibold text-gray-800 mb-3">Datenschutzerkl&auml;rung</h2>
    <div class="text-gray-600 text-sm leading-relaxed space-y-4">

      <div>
        <h3 class="font-medium text-gray-700 mb-1">1. Verantwortlicher</h3>
        <p>
          Verantwortlicher im Sinne der DSGVO ist Julius Falk, erreichbar unter
          <a href="mailto:julius@ex-lab.de" class="text-primary-600 hover:underline">julius@ex-lab.de</a>.
        </p>
      </div>

      <div>
        <h3 class="font-medium text-gray-700 mb-1">2. Hosting</h3>
        <p>
          Diese Website wird &uuml;ber GitHub Pages (GitHub Inc., USA) ausgeliefert und &uuml;ber GitHub Actions gebaut. GitHub kann beim Abruf der Seiten Zugriffsdaten (z.&thinsp;B. IP-Adresse, Zeitpunkt, abgerufene Seite) in Server-Logfiles speichern. Weitere Informationen:
          <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#data-collection" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:underline">GitHub Pages Privacy</a>.
          Die Nutzung erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an einer zuverl&auml;ssigen Bereitstellung der Website).
        </p>
      </div>

      <div>
        <h3 class="font-medium text-gray-700 mb-1">3. Webanalyse (Umami)</h3>
        <p>
          Wir nutzen <a href="https://umami.is" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:underline">Umami</a>, eine datenschutzfreundliche, selbst gehostete Webanalyse-Software auf einem Hetzner-Server in N&uuml;rnberg (Deutschland). Umami speichert keine Cookies, erhebt keine personenbezogenen Daten und erstellt keine ger&auml;te&uuml;bergreifenden Profile. Es werden ausschlie&szlig;lich anonymisierte Seitenaufrufe und Events erfasst. Alle Daten verbleiben auf dem deutschen Server. Die Verarbeitung erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.
        </p>
      </div>

      <div>
        <h3 class="font-medium text-gray-700 mb-1">4. API-Zugriffe</h3>
        <p>
          Die Website ruft Veranstaltungsdaten von einem selbst gehosteten Directus-Server (calapi.buerofalk.de) auf einem Hetzner-Server in N&uuml;rnberg (Deutschland) ab. Dabei wird Ihre IP-Adresse technisch bedingt an den Server &uuml;bermittelt. Es werden keine personenbezogenen Daten gespeichert oder ausgewertet. Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO.
        </p>
      </div>

      <div>
        <h3 class="font-medium text-gray-700 mb-1">5. Kalender-Abo (Nextcloud)</h3>
        <p>
          Das Kalender-Abo (iCal/CalDAV) wird &uuml;ber eine selbst gehostete Nextcloud-Instanz auf einem Hetzner-Server in N&uuml;rnberg (Deutschland) bereitgestellt. Beim Abruf des Kalenders wird Ihre IP-Adresse technisch bedingt an den Server &uuml;bermittelt. Es werden keine personenbezogenen Daten gespeichert oder ausgewertet. Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO.
        </p>
      </div>

      <div>
        <h3 class="font-medium text-gray-700 mb-1">6. Newsletter</h3>
        <p>
          F&uuml;r den Newsletter-Versand nutzen wir Listmonk, selbst gehostet auf einem Hetzner-Server in N&uuml;rnberg (Deutschland). Bei der Anmeldung wird ausschlie&szlig;lich Ihre E-Mail-Adresse gespeichert. Die Verarbeitung erfolgt auf Grundlage Ihrer Einwilligung (Art. 6 Abs. 1 lit. a DSGVO). Sie k&ouml;nnen sich jederzeit &uuml;ber den Abmeldelink in jeder E-Mail abmelden.
        </p>
      </div>

      <div>
        <h3 class="font-medium text-gray-700 mb-1">7. Externe Links</h3>
        <p>
          Diese Website enth&auml;lt Links zu externen Veranstaltungsseiten und Organisationen. F&uuml;r deren Datenschutzpraktiken sind wir nicht verantwortlich.
        </p>
      </div>

      <div>
        <h3 class="font-medium text-gray-700 mb-1">8. Ihre Rechte</h3>
        <p>
          Sie haben das Recht auf Auskunft (&sect; 15 DSGVO), Berichtigung (&sect; 16 DSGVO), L&ouml;schung (&sect; 17 DSGVO), Einschr&auml;nkung der Verarbeitung (&sect; 18 DSGVO), Daten&uuml;bertragbarkeit (&sect; 20 DSGVO) und Widerspruch (&sect; 21 DSGVO). Wenden Sie sich dazu an
          <a href="mailto:julius@ex-lab.de" class="text-primary-600 hover:underline">julius@ex-lab.de</a>.
          Zudem steht Ihnen ein Beschwerderecht bei einer Datenschutz-Aufsichtsbeh&ouml;rde zu.
        </p>
      </div>

    </div>
  </section>
</div>
