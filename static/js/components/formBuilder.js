import { formatDateTimeLocal, formatKey } from "../dom/domUtils.js";
// formBuilder.js
import { createElement } from "../dom/domUtils.js";

export function buildForm(fields, data = {}, model, onDeleteClick = null) {
  const form = document.getElementById("dynamicForm");
  form.innerHTML = ""; // Clear current form fields

  fields.forEach((field) => {
    const wrapper = createElement("div", { className: "mb-3" });

    const label = createElement("label", {
      className: "form-label",
      textContent: formatKey(field.name),
      attributes: { for: `field-${field.name}` },
    });

    let input;

    if (field.type === "relationship" && field.relationship_type === "many") {
      // Render multiple checkboxes
      input = createElement("div", { className: "checkbox-group" });

      const selectedIds = data[field.name]
        ? data[field.name].map((item) => item.id)
        : [];

      const noneCheckboxId = `field-${field.name}-none`;

      const noneCheckboxWrapper = createElement("div", {
        className: "form-check",
      });
      const noneCheckbox = createElement("input", {
        type: "checkbox",
        className: "form-check-input",
        id: noneCheckboxId,
        name: `${field.name}[]`, // same name as others
        value: 0, // or "" or "none"
        checked: selectedIds.length === 0, // checked if nothing else selected
      });
      const noneLabel = createElement("label", {
        className: "form-check-label",
        for: noneCheckboxId,
        textContent: "-- None --",
      });

      noneCheckboxWrapper.appendChild(noneCheckbox);
      noneCheckboxWrapper.appendChild(noneLabel);
      input.appendChild(noneCheckboxWrapper);
      (field.choices || []).forEach((choice) => {
        const checkboxId = `field-${field.name}-${choice.id}`;

        const checkboxWrapper = createElement("div", {
          className: "form-check",
        });

        const checkbox = createElement("input", {
          type: "checkbox",
          className: "form-check-input",
          id: checkboxId,
          name: `${field.name}[]`,
          value: choice.id,
          checked: selectedIds.includes(choice.id),
        });

        const checkboxLabel = createElement("label", {
          className: "form-check-label",
          for: checkboxId,
          //textContent: choice.label,
        });

        // Create the <a> element for the label link
        const labelLink = createElement("a", {
          href: "#",
          className: "link",
          textContent: choice.label,
        });

        // Add custom data attributes (assuming you have these info)
        labelLink.setAttribute(
          "data-name",
          choice.label.toLowerCase().replace(/\s+/g, "-").trim()
        ); // example slugify
        labelLink.setAttribute(
          "data-model",
          field.name.toLowerCase().slice(0, -1)
        );
        checkboxLabel.appendChild(labelLink);
        checkboxWrapper.appendChild(checkbox);
        checkboxWrapper.appendChild(checkboxLabel);
        input.appendChild(checkboxWrapper);
      });
    } else {
      switch (field.type) {
        case "boolean":
          input = createElement("input", {
            type: "checkbox",
            checked: !!data[field.name],
          });
          break;

        case "integer":
        case "float":
          input = createElement("input", {
            type: "number",
            step: field.type === "float" ? "any" : "1",
            value: data[field.name] ?? "",
          });
          break;

        case "datetime":
          input = createElement("input", {
            type: "datetime-local",
            value: formatDateTimeLocal(data[field.name]) ?? "",
          });
          break;

        case "textlong":
          input = createElement("textarea", {
            value: data[field.name] ?? "",
          });
          break;

        case "enum":
        case "foreignkey":
          input = createElement("select");
          input.appendChild(
            createElement("option", {
              value: "",
              textContent: "-- None --",
            })
          );

          (field.choices || []).forEach((choice) => {
            const isEnum = field.type === "enum";
            const optionValue = isEnum ? choice : choice.id;
            const optionLabel = isEnum ? choice : choice.label;

            input.appendChild(
              createElement("option", {
                value: optionValue,
                textContent: optionLabel,
                selected: data[field.name] === optionValue,
              })
            );
          });
          break;

        default:
          input = createElement("input", {
            type: "text",
            value: data[field.name] ?? "",
          });
      }
    }

    input.name = field.name;
    input.id = `checkbox-group-${field.name}`;
    input.className =
      input.tagName === "SELECT" || input.tagName === "TEXTAREA"
        ? "form-select"
        : "form-control";

    if (
      !field.nullable &&
      !(field.type === "relationship" && field.relationship_type === "many")
    ) {
      input.required = true;
    }
    if (field.name == "slug") input.readOnly = true;

    wrapper.appendChild(label);
    wrapper.appendChild(input);
    form.appendChild(wrapper);
    setupNoneCheckboxLogic(field.name);
  });

  // Hidden page_type field
  form.appendChild(
    createElement("input", {
      type: "hidden",
      name: "page_type",
      value: data.page_type || model,
    })
  );

  // Hidden ID field (if editing)
  if (data.id) {
    form.appendChild(
      createElement("input", {
        type: "hidden",
        name: "id",
        value: data.id,
      })
    );
  }

  // Submit button
  form.appendChild(
    createElement("button", {
      type: "submit",
      className: "btn btn-success me-2",
      textContent: data.id ? "Save Changes" : "Create",
    })
  );

  // Optional delete button
  if (data.id) {
    const deleteBtn = createElement("button", {
      type: "button",
      className: "btn btn-danger",
      textContent: "Delete",
    });

    deleteBtn.addEventListener("click", onDeleteClick);
    form.appendChild(deleteBtn);
  }

  // Show form
  form.style.display = "block";
}

export function setupNoneCheckboxLogic(fieldName) {
  const input = document.getElementById(`checkbox-group-${fieldName}`);
  const noneCheckbox = document.getElementById(`field-${fieldName}-none`); // fix ID here

  if (!input || !noneCheckbox) return;

  noneCheckbox.addEventListener("change", () => {
    if (noneCheckbox.checked) {
      input.querySelectorAll(`input[name="${fieldName}[]"]`).forEach((cb) => {
        if (cb !== noneCheckbox) cb.checked = false;
      });
    }
  });

  input.querySelectorAll(`input[name="${fieldName}[]"]`).forEach((cb) => {
    if (cb !== noneCheckbox) {
      cb.addEventListener("change", () => {
        if (cb.checked) noneCheckbox.checked = false;
      });
    }
  });
}
