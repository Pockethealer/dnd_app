import { loadEntry, loadEntryByName, submitEntry } from "../api/modelApi.js";
import { showFlashMessage } from "../dom/flashMessages.js";

export async function submitPage(form) {
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());
  const idInput = form.querySelector('input[name="id"]');
  const id = idInput ? idInput.value : null;
  const model = "page";
  // Convert empty parent_id to null explicitly (if needed)
  if (!data.parent_id) data.parent_id = null;

  // Wait if autosave is still running and ID is missing
  if (autosaveInProgress && !pageIdAssigned) {
    showFlashMessage("Please wait, saving page before submitting...", "info");
    await new Promise((resolve) => {
      const checkInterval = setInterval(() => {
        if (!autosaveInProgress && pageIdAssigned) {
          clearInterval(checkInterval);
          resolve();
        }
      }, 100);
    });
  }

  try {
    const result = await submitEntry(model, data, id);
    // redirect or update UI with result.slug
    showFlashMessage(id ? "Page updated!" : "Page created!", "success");
    window.location.href = `/wiki/${result.slug}`;
  } catch (err) {
    showFlashMessage(err.message, "error");
  }
}

let autosaveInProgress = false;
let pageIdAssigned = false;

export async function autosavePage(form) {
  autosaveInProgress = true;
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  const model = "page";
  const id = data.id || null;

  if (!data.title || (!data.content && !data.content_md)) {
    autosaveInProgress = false;
    return;
  }
  if (!data.parent_id) data.parent_id = null;

  try {
    const result = await submitEntry(model, data, id);
    // Optionally update the hidden ID field after first save
    if (!id && result && result.id) {
      form.querySelector('input[name="id"]').value = result.id;
    }
    pageIdAssigned = true;
    showFlashMessage(
      "Autosaved at " + new Date().toLocaleTimeString(),
      "success"
    );
  } catch (err) {
    showFlashMessage("Autosave failed:", err, "error");
  }
  autosaveInProgress = false;
  preview(form);
}
//autosave after typing stops
export function debounce(func, delay) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), delay);
  };
}

export async function preview(form) {
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  const name = data.title || null;
  const model = "page";

  const entry = await loadEntryByName(model, name);
  const previewHTML =
    entry.content || entry.title || entry.slug || "<i>No content available</i>";
  const previewBox = document.querySelector(".preview-box");
  if (previewBox) {
    try {
      previewBox.innerHTML = previewHTML;
    } catch (err) {
      console.error("Failed to update preview:", err);
    }
  }
}
