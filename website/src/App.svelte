<script>
  import { onMount } from 'svelte';
  import Header from './components/Header.svelte';
  import Home from './pages/Home.svelte';
  import Foerderprogramme from './pages/Foerderprogramme.svelte';
  import LinkedInGenerator from './pages/LinkedInGenerator.svelte';
  import Transparency from './pages/Transparency.svelte';
  import { trackPageView } from './services/analytics';

  // Simple routing
  let currentRoute = 'home';

  onMount(() => {
    // Set initial route based on URL
    handleRouteChange();

    // Track initial page view
    trackPageView(window.location.pathname);

    // Listen for URL changes
    window.addEventListener('popstate', () => {
      handleRouteChange();
      trackPageView(window.location.pathname);
    });

    return () => {
      window.removeEventListener('popstate', handleRouteChange);
    };
  });

  // Get base path from the URL (for GitHub Pages subdirectory support)
  const basePath = window.location.pathname.split('/')[1] === 'digikal' ? '/digikal' : '';

  function handleRouteChange() {
    const path = window.location.pathname;
    const pathWithoutBase = path.replace(basePath, '') || '/';

    if (pathWithoutBase === '/about') {
      currentRoute = 'about';
    } else if (pathWithoutBase === '/foerderprogramme') {
      currentRoute = 'foerderprogramme';
    } else if (pathWithoutBase === '/linkedin-generator') {
      currentRoute = 'linkedin-generator';
    } else {
      currentRoute = 'home';
    }
  }

  function navigateTo(route, event) {
    if (event) {
      event.preventDefault();
    }

    const fullRoute = basePath + route;
    window.history.pushState({}, '', fullRoute);
    handleRouteChange();

    // Track page view on navigation
    trackPageView(fullRoute);
  }
</script>

<svelte:head>
  <link rel="stylesheet" href="global.css">
  <link rel="stylesheet" href="custom.css">
</svelte:head>

<Header {navigateTo} {currentRoute} />

<div class="min-h-[calc(100vh-120px)]">
  {#if currentRoute === 'home'}
    <Home />
  {:else if currentRoute === 'about'}
    <Transparency />
  {:else if currentRoute === 'foerderprogramme'}
    <Foerderprogramme />
  {:else if currentRoute === 'linkedin-generator'}
    <LinkedInGenerator />
  {/if}
</div>

<footer class="bg-gray-800 text-white py-6 mt-8">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
    <p class="text-gray-300 text-sm">
      &copy; {new Date().getFullYear()} DigiKal &mdash; Julius Falk / <a href="https://ex-lab.de" target="_blank" rel="noopener noreferrer" class="hover:text-white underline">ex:lab</a>
    </p>
    <a href="/about" on:click|preventDefault={(e) => { navigateTo('/about', e); window.scrollTo(0, 0); }} class="text-sm text-gray-400 hover:text-white">&Uuml;ber DigiKal</a>
  </div>
</footer>
