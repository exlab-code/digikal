import { writable, derived } from 'svelte/store';
import { getDisplayTopics, CLUSTER_KEYS } from '$lib/tagClusters.js';

const CLUSTER_KEY_SET = new Set(CLUSTER_KEYS);

// Writable stores — populated from +page.server.js data
export const events = writable([]);
export const calendarUrls = writable({ ical: '' });
export const filters = writable({
	category: '',
	tags: [],
	onlineOnly: false,
	selectedMonth: null
});
export const isLoading = writable(false);
export const error = writable(null);

// Derived store for filtered events
export const filteredEvents = derived([events, filters], ([$events, $filters]) => {
	return $events.filter((event) => {
		if (!event.start_date) return false;

		const now = new Date();
		const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		const eventDate = new Date(event.start_date);
		const eventDay = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate());

		if (eventDay < today) return false;

		// Filter by tags (AND logic). Cluster keys / unmapped topic tags match via
		// the central cluster map against tag_groups.topic; other tags still match
		// the flat event.tags array.
		if ($filters.tags && $filters.tags.length > 0) {
			const eventTagsLower = Array.isArray(event.tags)
				? event.tags.map((t) => t.toLowerCase())
				: [];
			const displayTopics = getDisplayTopics(event);
			for (const filterTag of $filters.tags) {
				const isTopicFilter =
					CLUSTER_KEY_SET.has(filterTag) || displayTopics.includes(filterTag);
				const topicMatch = isTopicFilter && displayTopics.includes(filterTag);
				const flatMatch = eventTagsLower.includes(filterTag.toLowerCase());
				if (!topicMatch && !flatMatch) return false;
			}
		}

		// Filter by online only
		if ($filters.onlineOnly) {
			const hasOnlineTag =
				event.tags && Array.isArray(event.tags) && event.tags.some((tag) => tag === 'Online');
			const isOnlineLocation =
				!event.location ||
				event.location.toLowerCase().includes('online') ||
				event.location.toLowerCase().includes('virtuell') ||
				event.location.toLowerCase().includes('webinar') ||
				event.location.toLowerCase().includes('zoom') ||
				event.location.toLowerCase().includes('teams');
			if (!hasOnlineTag && !isOnlineLocation) return false;
		}

		// Filter by selected month
		if ($filters.selectedMonth) {
			const eventMonth = `${eventDate.getFullYear()}-${String(eventDate.getMonth() + 1).padStart(2, '0')}`;
			if (eventMonth !== $filters.selectedMonth) return false;
		}

		return true;
	});
});

// Update filters
export function updateFilters(newFilters) {
	if (newFilters.hasOwnProperty('category')) {
		delete newFilters.category;
	}
	filters.update((f) => {
		if (newFilters.hasOwnProperty('tags')) {
			return { ...f, ...newFilters, category: '' };
		}
		return { ...f, ...newFilters };
	});
}

// Available months from future events
const MONTH_NAMES_DE = [
	'Jan',
	'Feb',
	'Mrz',
	'Apr',
	'Mai',
	'Jun',
	'Jul',
	'Aug',
	'Sep',
	'Okt',
	'Nov',
	'Dez'
];

export const availableMonths = derived(events, ($events) => {
	const now = new Date();
	const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
	const monthMap = new Map();

	for (const event of $events) {
		if (!event.start_date) continue;
		const d = new Date(event.start_date);
		const eventDay = new Date(d.getFullYear(), d.getMonth(), d.getDate());
		if (eventDay < today) continue;

		const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
		if (monthMap.has(key)) {
			monthMap.get(key).count++;
		} else {
			monthMap.set(key, {
				key,
				label: `${MONTH_NAMES_DE[d.getMonth()]} ${d.getFullYear()}`,
				count: 1
			});
		}
	}

	return Array.from(monthMap.values()).sort((a, b) => a.key.localeCompare(b.key));
});

export const topTags = derived(events, ($events) => {
	const tagCounts = {};

	for (const event of $events) {
		if (event.tags && Array.isArray(event.tags)) {
			for (const tag of event.tags) {
				tagCounts[tag] = (tagCounts[tag] || 0) + 1;
			}
		}
	}

	return Object.entries(tagCounts)
		.sort((a, b) => b[1] - a[1])
		.slice(0, 9)
		.map(([tag]) => tag);
});
