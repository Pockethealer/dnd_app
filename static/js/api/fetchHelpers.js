export async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error((await res.json()).error || 'Fetch error');
  return res.json();
}
