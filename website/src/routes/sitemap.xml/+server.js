import { getEvents } from '$lib/services/api.server.js';
import { eventPath, isEventArchived } from '$lib/eventHelpers.js';

export const prerender = true;

const SITE = 'https://www.digikal.org';

const staticUrls = [
	{ loc: '/', changefreq: 'daily', priority: '1.0' },
	{ loc: '/foerderprogramme', changefreq: 'weekly', priority: '0.8' },
	{ loc: '/themen/ki', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/themen/datenschutz', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/themen/digitale-transformation', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/themen/it-sicherheit', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/themen/social-media', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/about', changefreq: 'monthly', priority: '0.5' }
];

/**
 * @param {string} loc
 * @param {string} lastmod
 * @param {string} changefreq
 * @param {string} priority
 */
function urlEntry(loc, lastmod, changefreq, priority) {
	return (
		`  <url>\n` +
		`    <loc>${SITE}${loc}</loc>\n` +
		`    <lastmod>${lastmod}</lastmod>\n` +
		`    <changefreq>${changefreq}</changefreq>\n` +
		`    <priority>${priority}</priority>\n` +
		`  </url>`
	);
}

export async function GET() {
	const today = new Date().toISOString().split('T')[0];

	let eventEntries = '';
	try {
		const events = await getEvents();
		eventEntries = events
			.filter((e) => !isEventArchived(e, 90))
			.map((e) => {
				const lastmod = (e.updated_at || e.date_updated || e.start_date || new Date().toISOString())
					.split('T')[0];
				return urlEntry(eventPath(e), lastmod, 'weekly', '0.6');
			})
			.join('\n');
	} catch (err) {
		console.error('Sitemap: failed to fetch events', err);
	}

	const body =
		`<?xml version="1.0" encoding="UTF-8"?>\n` +
		`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
		staticUrls.map((u) => urlEntry(u.loc, today, u.changefreq, u.priority)).join('\n') +
		(eventEntries ? '\n' + eventEntries : '') +
		`\n</urlset>\n`;

	return new Response(body, {
		headers: { 'Content-Type': 'application/xml; charset=utf-8' }
	});
}
