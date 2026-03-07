<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  let isScrolled = false;
  let isMenuOpen = false;

  const themen = [
    { slug: 'digitale-transformation', label: 'Digitale Transformation' },
    { slug: 'ki', label: 'KI' },
    { slug: 'it-sicherheit', label: 'IT-Sicherheit' },
    { slug: 'social-media', label: 'Social Media' },
    { slug: 'datenschutz', label: 'Datenschutz' }
  ];

  onMount(() => {
    const handleScroll = () => {
      isScrolled = window.scrollY > 10;
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

  $: currentPath = $page.url.pathname;
  $: isThemenActive = currentPath.startsWith('/themen');
</script>

<header class="{isScrolled ? 'shadow-md' : ''} sticky top-0 z-50 bg-white py-3 transition-shadow duration-300">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
    <div class="flex items-center">
      <a
        href="/"
        class="flex items-center gap-3 text-gray-800 font-semibold text-xl"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="text-primary-600" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <span>DigiKal</span>
      </a>
    </div>

    <nav class="{isMenuOpen ? 'translate-y-0 opacity-100 visible' : '-translate-y-full opacity-0 invisible md:opacity-100 md:visible md:translate-y-0'}
              fixed md:relative top-16 md:top-0 left-0 right-0 md:left-auto md:right-auto
              bg-white md:bg-transparent shadow-md md:shadow-none p-4 md:p-0
              transition-all duration-300 md:transition-none">
      <ul class="flex flex-col md:flex-row gap-4 md:gap-6">
        <li>
          <a
            href="/"
            on:click={() => isMenuOpen = false}
            class="block md:inline-block px-2 py-2 md:py-1 text-gray-700 font-medium hover:text-primary-600 relative
                  {currentPath === '/' ? 'text-primary-600' : ''}
                  after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-primary-600 after:w-full
                  {currentPath === '/' ? 'after:block' : 'after:hidden'}"
          >
            Veranstaltungen
          </a>
        </li>
        <li>
          <a
            href="/foerderprogramme"
            on:click={() => isMenuOpen = false}
            class="block md:inline-block px-2 py-2 md:py-1 text-gray-700 font-medium hover:text-primary-600 relative
                  {currentPath === '/foerderprogramme' ? 'text-primary-600' : ''}
                  after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-primary-600 after:w-full
                  {currentPath === '/foerderprogramme' ? 'after:block' : 'after:hidden'}"
          >
            Förderprogramme
          </a>
        </li>
        <li class="relative">
          <details class="themen-details">
            <summary
              class="list-none cursor-pointer flex items-center gap-1 px-2 py-2 md:py-1 text-gray-700 font-medium hover:text-primary-600 relative
                    {isThemenActive ? 'text-primary-600' : ''}
                    after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-primary-600 after:w-full
                    {isThemenActive ? 'after:block' : 'after:hidden'}"
            >
              Themen
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="themen-chevron">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </summary>
            <ul class="md:absolute md:top-full md:left-0 md:mt-1 md:bg-white md:shadow-lg md:rounded-lg md:border md:border-gray-100 md:py-1 md:min-w-[200px] pl-4 md:pl-0 mt-1 md:mt-2">
              {#each themen as t}
                <li>
                  <a
                    href="/themen/{t.slug}"
                    data-sveltekit-reload
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary-600
                          {currentPath === `/themen/${t.slug}` ? 'text-primary-600 bg-gray-50' : ''}"
                  >
                    {t.label}
                  </a>
                </li>
              {/each}
            </ul>
          </details>
        </li>
        <li>
          <a
            href="/about"
            data-sveltekit-reload
            on:click={() => isMenuOpen = false}
            class="block md:inline-block px-2 py-2 md:py-1 text-gray-700 font-medium hover:text-primary-600 relative
                  {currentPath === '/about' ? 'text-primary-600' : ''}
                  after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-primary-600 after:w-full
                  {currentPath === '/about' ? 'after:block' : 'after:hidden'}"
          >
            Über DigiKal
          </a>
        </li>
      </ul>
    </nav>

    <button class="md:hidden p-2 text-gray-700 hover:text-primary-600" on:click={toggleMenu} aria-label="Toggle menu">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>
  </div>
</header>
