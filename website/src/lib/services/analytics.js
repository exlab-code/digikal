/**
 * Analytics service for tracking user interactions
 * Uses Umami analytics (client-side only)
 */
import { browser } from '$app/environment';

export function trackEvent(eventName, props = {}) {
	if (!browser) return;
	if (typeof umami !== 'undefined') {
		umami.track(eventName, props);
	}
}

export function trackPageView(url, props = {}) {
	if (!browser) return;
	if (typeof umami !== 'undefined') {
		umami.track((p) => ({ ...p, url }));
	}
}
