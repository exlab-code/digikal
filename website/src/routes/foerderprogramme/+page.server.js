export async function load({ fetch }) {
	const res = await fetch('/foerdermittel.json');
	const foerdermittel = await res.json();
	return { foerdermittel };
}
