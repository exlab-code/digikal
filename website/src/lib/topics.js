/**
 * Topic definitions for SEO landing pages at /themen/[topic].
 * `eventTags` are now cluster keys from $lib/tagClusters.js so the pages
 * surface every event whose raw topic tag maps into the cluster.
 * `foerdermittelTags` keep their free-text semantics (Förderprogramme tags
 * are not yet clustered).
 */
export const TOPICS = {
	ki: {
		title: 'KI für Nonprofits',
		metaTitle: 'KI & Künstliche Intelligenz für gemeinnützige Organisationen – DigiKal',
		description:
			'Veranstaltungen und Förderprogramme zu Künstlicher Intelligenz für gemeinnützige Organisationen in Deutschland.',
		eventTags: ['KI'],
		foerdermittelTags: ['Künstliche Intelligenz', 'KI', 'Digitalisierung']
	},
	datenschutz: {
		title: 'Datenschutz & Sicherheit',
		metaTitle: 'Datenschutz & IT-Sicherheit für Nonprofits – DigiKal',
		description:
			'Veranstaltungen und Förderprogramme zu Datenschutz und IT-Sicherheit für gemeinnützige Organisationen.',
		eventTags: ['Datenschutz & Recht', 'IT-Sicherheit'],
		foerdermittelTags: ['Datenschutz', 'IT-Sicherheit', 'Cybersicherheit']
	},
	'digitale-transformation': {
		title: 'Digitale Transformation',
		metaTitle: 'Digitale Transformation für gemeinnützige Organisationen – DigiKal',
		description:
			'Veranstaltungen und Förderprogramme zur digitalen Transformation für gemeinnützige Organisationen.',
		eventTags: ['Strategie & Führung', 'Prozesse & Automatisierung'],
		foerdermittelTags: ['Digitale Transformation', 'Digitalisierung']
	},
	'it-sicherheit': {
		title: 'IT-Sicherheit',
		metaTitle: 'IT-Sicherheit & Cybersicherheit für gemeinnützige Organisationen – DigiKal',
		description:
			'Veranstaltungen und Förderprogramme zu IT-Sicherheit und Cybersicherheit für gemeinnützige Organisationen in Deutschland.',
		eventTags: ['IT-Sicherheit'],
		foerdermittelTags: ['IT-Sicherheit', 'Cybersicherheit', 'Informationssicherheit']
	},
	'social-media': {
		title: 'Social Media',
		metaTitle: 'Social Media & Digitale Kommunikation für Nonprofits – DigiKal',
		description:
			'Veranstaltungen und Förderprogramme zu Social Media und digitaler Kommunikation für gemeinnützige Organisationen.',
		eventTags: ['Social Media & Kommunikation'],
		foerdermittelTags: ['Social Media', 'Digitale Kommunikation', 'Öffentlichkeitsarbeit']
	}
};
