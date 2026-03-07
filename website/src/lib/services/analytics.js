/**
 * Analytics service for tracking user interactions
 * Uses Umami analytics (client-side only)
 */
import { browser } from '$app/environment';

const eventQueue = [];
let umamiLoaded = false;

function sendEvent(eventName, props) {
	if (umamiLoaded && typeof umami !== 'undefined') {
		umami.track(eventName, props);
	} else {
		eventQueue.push({ eventName, props });
	}
}

function flushQueue() {
	while (eventQueue.length > 0) {
		const { eventName, props } = eventQueue.shift();
		if (typeof umami !== 'undefined') {
			umami.track(eventName, props);
		}
	}
}

if (browser) {
	window.addEventListener('umami:loaded', () => {
		umamiLoaded = true;
		flushQueue();
	});
}

export function trackEvent(eventName, props = {}) {
	if (!browser) return;
	sendEvent(eventName, props);
}

export function trackPageView(url, props = {}) {
	if (!browser) return;
	if (umamiLoaded && typeof umami !== 'undefined') {
		umami.trackView(url, props);
	} else {
		eventQueue.push({ eventName: 'page_view', props: { url, ...props } });
	}
}
