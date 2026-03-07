<script>
	import '../app.css';
	import Header from '$lib/components/Header.svelte';
</script>

<Header />

<div class="min-h-[calc(100vh-120px)]">
	<slot />
</div>

<footer class="bg-gray-800 text-white py-6 mt-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
		<p class="text-gray-300 text-sm">
			&copy; {new Date().getFullYear()} DigiKal &mdash; Julius Falk / <a href="https://ex-lab.de" target="_blank" rel="noopener noreferrer" class="hover:text-white underline">ex:lab</a>
		</p>
		<a href="/about" class="text-sm text-gray-400 hover:text-white">Über DigiKal</a>
	</div>
</footer>
