// modelApi.js
import { fetchJSON } from "./fetchHelpers.js";

export function loadFields(model) {
  return fetchJSON(`/get-fields/${model}`);
}

export function loadEntry(model, id) {
  return fetchJSON(`/get-entry/${model}/${id}`);
}

export function loadEntries(model) {
  return fetchJSON(`/get-entries/${model}`);
}

export function submitEntry(model, data, id = null) {
  const url = id ? `/edit-entry/${model}/${id}` : "/submit-page";
  return fetchJSON(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function deleteEntry(model, id) {
  return fetch(`/delete-entry/${model}/${id}`, { method: "DELETE" });
}

export function getPageTree() {
  return fetchJSON(`/api/pages/tree`);
}

export function loadEntryByName(model, name) {
  return fetchJSON(`/get-entry-by-name/${model}/${name}`);
}
