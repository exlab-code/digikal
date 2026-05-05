export const csr = false;

const DIRECTUS_URL = 'https://calapi.buerofalk.de';

const SOURCES = [
	// HTML scrapers via event_scraper.py (sources.json)
	{ name: 'Stifter-helfen.de', url: 'https://www.hausdesstiftens.org/non-profits/wissen/webinare/', type: 'Scraper' },
	{ name: 'Deutsche Stiftung für Engagament und Ehrenamt', url: 'https://www.deutsche-stiftung-engagement-und-ehrenamt.de/veranstaltungen/liste/', type: 'Scraper' },
	{ name: 'Aktion Zivilcourage Weiterbildungsforum Ehrenamt', url: 'https://eveeno.com/138543290', type: 'Scraper' },
	{ name: 'Open Transfer', url: 'https://opentransfer.de/event/', type: 'Scraper' },
	{ name: 'Skala Campus', url: 'https://www.skala-campus.org/termine/', type: 'Scraper' },
	{ name: 'Fraunhofer IAO', url: 'https://www.iao.fraunhofer.de/de/veranstaltungen.html', type: 'Scraper' },
	{ name: 'Stiftung Datenschutz', url: 'https://stiftungdatenschutz.org/ehrenamt/webinare', type: 'Scraper' },
	{ name: 'Wegweiser Bürgergesellschaft', url: 'https://www.buergergesellschaft.de/mitteilen/nuetzliches/veranstaltungskalender', type: 'Scraper' },
	{ name: 'Paritätischer Wohlfahrtsverband', url: 'https://www.der-paritaetische.de/veranstaltungen/', type: 'Scraper' },
	{ name: 'Initiative D21', url: 'https://initiatived21.de/veranstaltungen', type: 'Scraper' },
	{ name: 'Deutscher Fundraising Verband', url: 'https://www.dfrv.de/veranstaltungen/', type: 'Scraper' },
	// Individual Python scrapers
	{ name: 'SIGU-Plattform', url: 'https://sigu-plattform.de/', type: 'Scraper' },
	{ name: 'KGSt', url: 'https://www.kgst.de/veranstaltungskalender', type: 'Scraper' },
	{ name: 'NEGZ', url: 'https://negz.org/aktuelle-veranstaltungen/', type: 'Scraper' },
	{ name: 'Paritätische Akademie Berlin', url: 'https://akademie.org/themen/digitalisierung/', type: 'Scraper' },
	{ name: 'HIIG', url: 'https://www.hiig.de/events/', type: 'Scraper' },
	{ name: 'vediso', url: 'https://vediso.de/event?date=scheduled', type: 'Scraper' },
	// ICS calendar feeds
	{ name: 'CorrelAid', url: 'https://correlaid.org/veranstaltungen/', type: 'ICS' },
	{ name: 'Civic Data Community', url: 'https://community.civic-data.de/', type: 'ICS' },
	{ name: 'D3 / so-geht-digital', url: 'https://so-geht-digital.de/termine/', type: 'ICS' },
	// Paused
	{ name: 'socialnet Kalender', url: 'https://www.socialnet.de/kalender/', type: 'Scraper', paused: true },
];

export async function load() {
	let statsBySource = {};

	try {
		const params = new URLSearchParams({
			'groupBy[]': 'source',
			'aggregate[count]': 'id',
			'aggregate[max]': 'date_created',
			'filter': JSON.stringify({ review_status: { _eq: 'approved' } }),
			'limit': '-1'
		});

		const res = await fetch(`${DIRECTUS_URL}/items/events?${params}`);
		if (res.ok) {
			const json = await res.json();
			for (const row of json.data) {
				statsBySource[row.source] = {
					count: row.count?.id ?? 0,
					lastAdded: row.max?.date_created ?? null
				};
			}
		}
	} catch {
		// Non-critical: page still renders without live stats
	}

	const sources = SOURCES.map((s) => ({
		...s,
		count: statsBySource[s.name]?.count ?? null,
		lastAdded: statsBySource[s.name]?.lastAdded ?? null
	}));

	return { sources };
}
