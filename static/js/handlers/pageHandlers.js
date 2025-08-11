// pageHandlers.js
import { loadFields, loadEntry, loadEntries } from '../api/modelApi.js';
import { buildForm } from '../components/formBuilder.js';
import { handleDelete } from './formHandlers.js';
import { renderEntryCards } from '../components/entryCards.js';

export async function handleModelChange(model, elements) {
  const { editEntrySelect, formContainer } = elements;

  editEntrySelect.disabled = true;
  editEntrySelect.innerHTML = '<option>Loading...</option>';

  try {
    const entries = await loadEntries(model);
    editEntrySelect.innerHTML = '<option value="" disabled selected>Select entry</option>';
    entries.forEach(entry => {
      const option = document.createElement('option');
      option.value = entry.id;
      option.textContent = entry.label;
      editEntrySelect.appendChild(option);
    });
    editEntrySelect.disabled = false;
    loadAndShowForm(model, null, formContainer)
    await renderEntryCards(model, (id) => loadAndShowForm(model, id, formContainer));
  } catch (err) {
    console.error(err);
  }
}

export async function loadAndShowForm(model, id, formContainer) {
  try {
    const fields = await loadFields(model);
    const data = id ? await loadEntry(model, id) : { page_type: model };
    if (id) data.id = id;

    buildForm(fields, data, model, () => handleDelete(model, id, () => handleModelChange(model, { editEntrySelect, formContainer })));
  } catch (err) {
    console.error('Form loading failed:', err);
    formContainer.innerHTML = '<p class="text-danger">Failed to load form.</p>';
  }
}