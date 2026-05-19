/**
 * Slugify a string for URLs: lowercase, ASCII-fold German chars, hyphenate.
 * @param {string} text
 * @returns {string}
 */
export function slugify(text) {
	if (!text) return '';
	return text
		.toLowerCase()
		.replace(/ä/g, 'ae')
		.replace(/ö/g, 'oe')
		.replace(/ü/g, 'ue')
		.replace(/ß/g, 'ss')
		.normalize('NFD')
		.replace(/[̀-ͯ]/g, '')
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-+|-+$/g, '')
		.slice(0, 80);
}

/**
 * Build the canonical URL path for an event.
 * Pattern: /event/{id}-{slug}
 * @param {{ id: string|number, title: string }} event
 * @returns {string}
 */
export function eventPath(event) {
	return `/event/${event.id}-${slugify(event.title)}`;
}

/**
 * Extract all tags from an event's tag_groups (object or JSON string).
 * @param {{ tag_groups?: unknown, tags?: string[] }} event
 * @returns {string[]}
 */
export function getEventTags(event) {
	if (Array.isArray(event.tags) && event.tags.length > 0) return event.tags;
	if (!event.tag_groups) return [];
	const tg =
		typeof event.tag_groups === 'string'
			? safeJsonParse(event.tag_groups)
			: event.tag_groups;
	if (!tg) return [];
	return Object.values(tg).flat().filter(Boolean);
}

/**
 * @param {string} s
 * @returns {unknown}
 */
function safeJsonParse(s) {
	try {
		return JSON.parse(s);
	} catch {
		return null;
	}
}

/**
 * Jaccard similarity between two tag arrays.
 * @param {string[]} a
 * @param {string[]} b
 * @returns {number} 0..1
 */
function jaccard(a, b) {
	if (!a.length || !b.length) return 0;
	const setA = new Set(a.map((x) => x.toLowerCase()));
	const setB = new Set(b.map((x) => x.toLowerCase()));
	let intersection = 0;
	for (const x of setA) if (setB.has(x)) intersection++;
	const union = setA.size + setB.size - intersection;
	return union === 0 ? 0 : intersection / union;
}

/**
 * Return the top-N most similar events. Upcoming events preferred; falls back to past.
 * @param {object} target  The event to find peers for.
 * @param {object[]} pool  All events.
 * @param {number} limit
 * @returns {object[]}
 */
export function findSimilarEvents(target, pool, limit = 5) {
	const targetTags = getEventTags(target);
	if (!targetTags.length || !pool.length) return [];

	const now = Date.now();
	const startOfDay = new Date(new Date(now).setHours(0, 0, 0, 0)).getTime();

	const scored = pool
		.filter((e) => e.id !== target.id)
		.map((e) => ({
			event: e,
			score: jaccard(targetTags, getEventTags(e)),
			isUpcoming: e.start_date && new Date(e.start_date).getTime() >= startOfDay,
			startMs: e.start_date ? new Date(e.start_date).getTime() : Infinity
		}))
		.filter((x) => x.score > 0);

	const upcoming = scored
		.filter((x) => x.isUpcoming)
		.sort((a, b) => b.score - a.score || a.startMs - b.startMs);

	if (upcoming.length >= limit) return upcoming.slice(0, limit).map((x) => x.event);

	const past = scored
		.filter((x) => !x.isUpcoming)
		.sort((a, b) => b.score - a.score || b.startMs - a.startMs);

	return [...upcoming, ...past].slice(0, limit).map((x) => x.event);
}

/**
 * Has the event already ended?
 * @param {{ end_date?: string, start_date?: string }} event
 * @returns {boolean}
 */
export function isEventPast(event) {
	const ref = event.end_date || event.start_date;
	if (!ref) return false;
	return new Date(ref).getTime() < Date.now();
}

/**
 * Was the event more than `days` ago? Used to flip to noindex.
 * @param {object} event
 * @param {number} days
 */
export function isEventArchived(event, days = 90) {
	const ref = event.end_date || event.start_date;
	if (!ref) return false;
	const ageMs = Date.now() - new Date(ref).getTime();
	return ageMs > days * 86400000;
}
