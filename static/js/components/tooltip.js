import { loadEntry, loadEntryByName } from "../api/modelApi.js";
import { formatKey } from "../dom/domUtils.js";

const MAX_RELATED = 3;

// Assuming loadEntry(model, id) is imported or available

const tooltipContainer = document.getElementById("tooltip-container");

////////////////////////////////////////////////////////////////////////
export async function showTooltip(model, name, event) {
  try {
    const data = await loadEntryByName(model, name);
    if (!data) {
      tooltipContainer.textContent = "No data found";
      return;
    }

    // Build tooltip content
    tooltipContainer.innerHTML = formatTooltipContent(data);

    // Show tooltip temporarily to measure it
    tooltipContainer.style.display = "block";
    tooltipContainer.classList.add("show");

    const spacing = 8; // distance from the element
    const padding = 8; // viewport padding
    const rect = event.target.getBoundingClientRect();
    const tooltipRect = tooltipContainer.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Position: lower right corner of the target element + spacing
    let top = rect.bottom + spacing + window.scrollY;
    let left = rect.right + spacing + window.scrollX;

    // Keep tooltip inside viewport right edge
    if (left + tooltipRect.width > window.scrollX + viewportWidth - padding) {
      left = window.scrollX + viewportWidth - tooltipRect.width - padding;
    }
    // Keep tooltip inside viewport bottom edge
    if (top + tooltipRect.height > window.scrollY + viewportHeight - padding) {
      top = rect.top - tooltipRect.height - spacing + window.scrollY;
    }

    // Apply the position
    tooltipContainer.style.top = `${top}px`;
    tooltipContainer.style.left = `${left}px`;
  } catch (err) {
    tooltipContainer.textContent = "Failed to load data";
    console.error("Tooltip fetch failed:", err);
  }
}

function formatTooltipContent(data) {
  const ignoredFields = ["_id", "id", "created_at", "updated_at"]; // optional
  let html = '<div style="max-width: 300px;">';

  for (const [key, value] of Object.entries(data)) {
    if (ignoredFields.includes(key)) continue;

    let displayValue = "";

    if (
      typeof value === "string" ||
      typeof value === "number" ||
      typeof value === "boolean"
    ) {
      const valStr = String(value);

      // Assume any string ending with an image extension is an image path
      if (/\.(jpe?g|png|gif|bmp|webp|ico)$/i.test(valStr)) {
        // Prepend /media/ to the path
        const imageUrl = `/media/${valStr.replace(/^\/+/, "")}`;
        displayValue = `<img src="${imageUrl}" alt="${key}" style="max-width: 100%; max-height: 150px; border-radius: 6px;" />`;
      } else {
        displayValue = valStr;
      }
    } else if (Array.isArray(value)) {
      if (value.length === 0) {
        displayValue = "(none)";
      } else if (typeof value[0] === "object" && value[0] !== null) {
        // Array of objects (related entries)
        const limited = value.slice(0, MAX_RELATED);
        // Try to use a meaningful property: name, label, title, or fallback to JSON string
        const entries = limited.map((obj) => {
          return obj.name || obj.label || obj.title || JSON.stringify(obj);
        });
        displayValue = entries.join(", ");
        if (value.length > MAX_RELATED) displayValue += ", ...";
      } else {
        // Array of primitive types
        displayValue = value.join(", ");
      }
    } else if (typeof value === "object" && value !== null) {
      // Single nested object: try to pick meaningful fields instead of full JSON
      if (value.name || value.label || value.title) {
        displayValue = value.name || value.label || value.title;
      } else {
        displayValue = JSON.stringify(value, null, 2);
      }
    }

    html += `<strong>${formatKey(key)}:</strong> ${displayValue}<br>`;
  }

  html += "</div>";
  return html;
}

//////////////////////////////////////////////////////////////////////////
export function hideTooltip() {
  tooltipContainer.classList.remove("show");
  tooltipContainer.style.display = "none";
  tooltipContainer.innerHTML = "";
}

let tooltipTimeout;

export function hideTooltipDelayed() {
  clearTimeout(tooltipTimeout);
  tooltipTimeout = setTimeout(() => {
    hideTooltip();
  }, 500);
}

export function cancelHide() {
  clearTimeout(tooltipTimeout);
}

export function getTooltipContainer() {
  return tooltipContainer;
}
