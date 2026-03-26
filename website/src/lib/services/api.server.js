// Server-side only Directus API client
// This file is only used during build (prerendering) — the token never reaches the browser.

const DIRECTUS_URL = process.env.DIRECTUS_API_URL || 'https://calapi.buerofalk.de';
const DIRECTUS_TOKEN = process.env.DIRECTUS_API_TOKEN || '';

/**
 * Fetch all approved events from Directus
 */
export async function getEvents() {
	const filterObj = { review_status: { _eq: 'approved' } };

	const params = new URLSearchParams({
		filter: JSON.stringify(filterObj),
		sort: 'start_date',
		limit: '-1'
	});

	const response = await fetch(`${DIRECTUS_URL}/items/events?${params}`, {
		headers: DIRECTUS_TOKEN ? { Authorization: `Bearer ${DIRECTUS_TOKEN}` } : {}
	});

	if (!response.ok) {
		throw new Error(`Directus API error: ${response.status}`);
	}

	const data = await response.json();
	return data.data;
}

/**
 * Get calendar subscription URLs
 */
export function getCalendarUrls() {
	return {
		nextcloud:
			'https://cloud.buerofalk.de/remote.php/dav/public-calendars/P3JABC3Rt87rzR9T?export',
		ical: '/calendar.ics'
	};
}
