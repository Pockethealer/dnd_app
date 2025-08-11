import { loadEntries } from "../api/modelApi.js";
import { createElement } from "../dom/domUtils.js";

export async function renderEntryCards(model, onClick) {
  const entryList = document.getElementById("entryList");
  entryList.innerHTML = "<p>Loading entries...</p>";

  try {
    const entries = await loadEntries(model);
    entryList.innerHTML = "";

    entries.forEach((entry) => {
      const card = createElement("div", {
        className: "entry-card",
        textContent: entry.label,
      });
      card.dataset.id = entry.id;
      card.addEventListener("click", () => onClick(entry.id));
      entryList.appendChild(card);
    });
  } catch (err) {
    entryList.innerHTML = "<p>Error loading entries.</p>";
    console.error(err);
  }
}
