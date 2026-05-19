export const prerender = true;

const SITE = 'https://www.digikal.org';

/**
 * @typedef {{ loc: string, changefreq: string, priority: string }} SitemapEntry
 */

/** @type {SitemapEntry[]} */
const urls = [
	{ loc: '/', changefreq: 'daily', priority: '1.0' },
	{ loc: '/foerderprogramme', changefreq: 'weekly', priority: '0.8' },
	{ loc: '/themen/ki', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/themen/datenschutz', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/themen/digitale-transformation', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/themen/it-sicherheit', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/themen/social-media', changefreq: 'weekly', priority: '0.7' },
	{ loc: '/about', changefreq: 'monthly', priority: '0.5' },
	{ loc: '/linkedin-generator', changefreq: 'monthly', priority: '0.4' }
];

export async function GET() {
	const lastmod = new Date().toISOString().split('T')[0];

	const body =
		`<?xml version="1.0" encoding="UTF-8"?>\n` +
		`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
		urls
			.map(
				(u) =>
					`  <url>\n` +
					`    <loc>${SITE}${u.loc}</loc>\n` +
					`    <lastmod>${lastmod}</lastmod>\n` +
					`    <changefreq>${u.changefreq}</changefreq>\n` +
					`    <priority>${u.priority}</priority>\n` +
					`  </url>`
			)
			.join('\n') +
		`\n</urlset>\n`;

	return new Response(body, {
		headers: { 'Content-Type': 'application/xml; charset=utf-8' }
	});
}
