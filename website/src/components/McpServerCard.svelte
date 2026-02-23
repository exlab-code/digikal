<script>
  let copySuccess = false;
  let copyTimeout;

  const mcpUrl = 'https://foerdermittel-mcp.buerofalk.de';

  function copyToClipboard() {
    navigator.clipboard.writeText(mcpUrl)
      .then(() => {
        copySuccess = true;
        if (copyTimeout) clearTimeout(copyTimeout);
        copyTimeout = setTimeout(() => { copySuccess = false; }, 3000);
      })
      .catch(() => {
        window.open(mcpUrl, '_blank');
      });
  }
</script>

<div class="bg-white rounded-lg shadow p-4">
  <h3 class="text-lg font-bold mb-2">MCP Server</h3>
  <p class="text-sm text-gray-600 mb-3">Durchsuche die Förderdatenbank direkt in Claude, Copilot, Cursor oder anderen MCP-fähigen Tools.</p>
  <button
    on:click={copyToClipboard}
    class="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
    </svg>
    {copySuccess ? 'URL kopiert!' : 'Server-URL kopieren'}
  </button>
  <a
    href="https://chatgpt.com/g/g-699b3c9b37b88191b1e2b8c0a2e35b7f-fordermittel-scout"
    target="_blank"
    rel="noopener noreferrer"
    class="w-full flex items-center justify-center gap-2 px-4 py-2 mt-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
    Fördermittel-Scout (GPT)
  </a>
</div>
