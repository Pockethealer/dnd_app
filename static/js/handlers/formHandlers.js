// formHandlers.js
import { submitEntry, deleteEntry } from "../api/modelApi.js";
import { showFlashMessage } from "../dom/flashMessages.js";

export async function handleFormSubmit(e, form, onSuccess) {
  e.preventDefault();
  const formData = new FormData(form);
  //TODO
  //const data = Object.fromEntries(formData.entries());
  const data = {};

  // for normal fields:
  for (const [key, value] of formData.entries()) {
    if (key.endsWith("[]")) {
      const actualKey = key.slice(0, -2);
      if (!data[actualKey]) data[actualKey] = [];
      data[actualKey].push(value); // convert to int if number
    } else {
      data[key] = value;
    }
  }
  const checkboxes = form.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(cb => {
    if (!(cb.name in data)) {
      // Checkbox was not checked, so set default value
      data[cb.name] = false;
    } else {
      // Convert value to boolean if it was checked
      data[cb.name] = true;
    }
  });
  const model = data.page_type;
  const id = data.id;

  try {
    await submitEntry(model, data, id);
    showFlashMessage(id ? "Entry updated!" : "Entry created!", "success");
    onSuccess();
  } catch (err) {
    showFlashMessage(err.message, "error");
  }
}

export async function handleDelete(model, id, onSuccess) {
  if (!confirm("Are you sure you want to delete this entry?")) return;
  try {
    const res = await deleteEntry(model, id);
    if (res.ok) {
      showFlashMessage("Entry deleted successfully!", "success");
      onSuccess();
    } else {
      const err = await res.json();
      showFlashMessage(err.error || "Failed to delete.", "error");
    }
  } catch (err) {
    showFlashMessage("Error deleting entry.", "error");
  }
}
