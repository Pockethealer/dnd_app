// main.js
import { handleModelChange, loadAndShowForm } from "./handlers/pageHandlers.js";
import { handleFormSubmit } from "./handlers/formHandlers.js";
import { showFlashMessage } from "./dom/flashMessages.js";
import {
  showTooltip,
  cancelHide,
  hideTooltipDelayed,
  getTooltipContainer,
} from "./components/tooltip.js";
import { submitPage, debounce, autosavePage } from "./components/pageEditor.js";
import { deleteEntry } from "./api/modelApi.js";
import { gallery } from "./dom/gallery.js";
import { attachPullButton, loadPullHistory } from "./handlers/handle_pull.js";

document.addEventListener("DOMContentLoaded", () => {
  //entry management
  const pageTypeSelect = document.getElementById("pageType");
  const createButton = document.getElementById("createNewButton");
  const editEntrySelect = document.getElementById("editEntrySelect");
  const form = document.getElementById("dynamicForm");
  const formContainer = document.getElementById("dynamicForm");
  const resetButton = document.getElementById("resetFormButton");
  //sidebar
  const sidebar = document.getElementById("sidebar");
  const sideBarToggleBtn = document.getElementById("sidebar-toggle");
  //page creation
  const savePageButton = document.getElementById("save-btn");
  const pageEditorForm = document.getElementById("page-editor");

  /*--------------------------------------side bar--------------------------------------------------*/
  if (sideBarToggleBtn) {
    sideBarToggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  //side menu toggle
  document.querySelectorAll(".side-toggle").forEach((toggleEl) => {
    toggleEl.addEventListener("click", () => {
      const submenu = toggleEl.parentElement.querySelector(".submenu");
      if (submenu) {
        const isVisible = submenu.style.display === "block";
        submenu.style.display = isVisible ? "none" : "block";
        toggleEl.innerHTML = isVisible ? "&#9654;" : "&#9660;";
      }
    });
  });
  /*--------------------------------------tooltips--------------------------------------------------*/
  //Tooltip

  const tooltipContainer = getTooltipContainer();
  if (window.matchMedia("(hover: hover)").matches) {
    document.body.addEventListener(
      "pointerenter",
      async (e) => {
        const target = e.target.closest("a[data-model][data-name]");
        if (!target) return;

        cancelHide();
        await showTooltip(target.dataset.model, target.dataset.name, e);
      },
      true
    );

    document.body.addEventListener(
      "pointerleave",
      (e) => {
        const related = e.relatedTarget;
        const target = e.target.closest("a[data-model][data-name]");

        // Only hide if mouse really left both link and tooltip
        if (!target) return;

        if (
          related !== tooltipContainer &&
          !tooltipContainer.contains(related)
        ) {
          hideTooltipDelayed();
        }
      },
      true
    );

    tooltipContainer.addEventListener("pointerenter", cancelHide);
    tooltipContainer.addEventListener("pointerleave", (e) => {
      const related = e.relatedTarget;
      // Only hide if leaving tooltip to somewhere other than the link
      if (
        related === null ||
        !related.closest ||
        !related.closest("a[data-model][data-name]")
      ) {
        hideTooltipDelayed();
      }
    });
  } else {
    /* ---------------- MOBILE (touch tap) ---------------- */
    let activeTarget = null;
    document.body.addEventListener(
      "click",
      async (e) => {
        const target = e.target.closest("a[data-model][data-name]");
        const insideTooltip = tooltipContainer.contains(e.target);

        if (target) {
          e.preventDefault();
          if (activeTarget === target) {
            tooltipContainer.style.display = "none";
            activeTarget = null;
          } else {
            await showTooltip(target.dataset.model, target.dataset.name, e);
            activeTarget = target; // <---- This was missing
          }
          return;
        }

        if (!insideTooltip) {
          tooltipContainer.style.display = "none";
          activeTarget = null;
        }
      },
      true
    );
  }
  //making links uninteractive
  document.body.addEventListener("click", (e) => {
    const target = e.target.closest('a[href="#"]');
    if (target) {
      e.preventDefault(); // prevent navigation or jump
    }
  });
  /*--------------------------------------manage entries--------------------------------------------------*/
  if (createButton) {
    createButton.addEventListener("click", async (e) => {
      e.preventDefault();
      const model = pageTypeSelect.value;
      if (!model)
        return showFlashMessage("Please select an entry type!", "error");
      await loadAndShowForm(model, null, formContainer);
    });
  }
  if (pageTypeSelect) {
    pageTypeSelect.addEventListener("change", async () => {
      await handleModelChange(pageTypeSelect.value, {
        editEntrySelect,
        formContainer,
      });
    });
  }
  if (editEntrySelect) {
    editEntrySelect.addEventListener("change", async () => {
      await loadAndShowForm(
        pageTypeSelect.value,
        editEntrySelect.value,
        formContainer
      );
    });
  }

  // Dynamic form delegation
  if (formContainer) {
    formContainer.addEventListener("submit", async (e) => {
      if (e.target && e.target.matches("form#dynamicForm")) {
        await handleFormSubmit(e, e.target, () => {
          e.target.reset();
          handleModelChange(pageTypeSelect.value, {
            editEntrySelect,
            formContainer,
          });
        });
      }
    });

    resetButton.addEventListener("click", () => {
      form.innerHTML = "";
      form.style.display = "none";
      pageTypeSelect.selectedIndex = 0;
      editEntrySelect.innerHTML =
        '<option value="" disabled selected>Select entry</option>';
      editEntrySelect.disabled = true;
      document.getElementById("entryList").innerHTML =
        "<p>Nothing to show.</p>";
    });
  }

  /*--------------------------------------edit page--------------------------------------------------*/
  const pageForm = document.getElementById("page-editor");
  const deletePageBtn = document.getElementById("delete-page-btn");
  if (pageForm) {
    pageForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      submitPage(pageForm);
    });
    //autosave
    const debouncedSave = debounce(() => autosavePage(pageForm), 3000); // 3s delay
    pageForm.addEventListener("input", debouncedSave);
  }
  if (pageForm && deletePageBtn) {
    deletePageBtn.addEventListener("click", async () => {
      if (!confirm("Are you sure you want to delete this page?")) return;

      const pageId = pageForm.querySelector("input[name='id']").value;
      try {
        const res = await deleteEntry("page", pageId);

        const result = await res.json();

        if (result.success) {
          showFlashMessage("Page deleted successfully!", "success");
          window.location.href = "/wiki";
        } else {
          throw new Error(result.message || "Failed to delete page.");
        }
      } catch (err) {
        showFlashMessage(err.message, "error");
      }
    });
  }

  const toggleCheckbox = document.getElementById("toggle-editor");
  const mdContainer = document.getElementById("markdown-container");
  const htmlContainer = document.getElementById("html-container");
  if (toggleCheckbox) {
    toggleCheckbox.addEventListener("change", () => {
      if (toggleCheckbox.checked) {
        mdContainer.style.display = "none";
        htmlContainer.style.display = "block";
      } else {
        mdContainer.style.display = "block";
        htmlContainer.style.display = "none";
      }
    });
  }
  /*--------------------------------------navbar--------------------------------------------------*/

  const toggleButton = document.querySelector(".navbar-toggle");
  const navbarLeft = document.querySelector(".navbar-left");
  const navbarRight = document.querySelector(".navbar-right");
  if (toggleButton) {
    toggleButton.addEventListener(
      "click",
      () => {
        navbarLeft.classList.toggle("active");
        navbarRight.classList.toggle("active");
      },
      false
    );
  }
  /*--------------------------------------pulls--------------------------------------------------*/
  loadPullHistory();
  const pullButton = document.getElementById("pull-btn-1");
  const pullButton10 = document.getElementById("pull-btn-10");
  if (pullButton) {
    attachPullButton(pullButton, 1);
  }
  if (pullButton10) {
    attachPullButton(pullButton10, 10);
  }
});
/*--------------------------------------Galery--------------------------------------------------*/
const modal = document.getElementById("modal");
const modalContent = document.getElementById("modal-content");
if (modal && modalContent) {
  gallery(modal, modalContent);
}
