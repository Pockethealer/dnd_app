let currentPage = 1;
let allLogs = [];
let maxPage = 1;

export async function initPullHistory(pageSize = 20) {
  const resp = await fetch(`/pull-history/2000`, { method: "GET" });
  allLogs = await resp.json();
  maxPage = Math.ceil(allLogs.length / pageSize);
  loadPullHistory();
  pullPagination();
}

export async function loadPullHistory(page = 1, no = 20) {
  const startIndex = (page - 1) * no;
  const endIndex = page * no;
  const pageLogs = allLogs.slice(startIndex, endIndex);
  const historyContainer = document.getElementById("pull-history-list");
  if (historyContainer) {
    historyContainer.innerHTML = "";
    pageLogs.forEach((item) => {
      const logDiv = document.createElement("div");
      logDiv.className = `pull-history-item ${item.rarity}`;
      logDiv.innerHTML = `<strong>${item.name}</strong>— ${item.pulled_at}`;
      // prepend so latest is on top
      historyContainer.append(logDiv);
    });
  }
}
export async function pullPagination() {
  const prevBtn = document.getElementById("prev-page-btn");
  const nextBtn = document.getElementById("next-page-btn");
  if (prevBtn || nextBtn) {
    if (currentPage <= 1) {
      prevBtn.disabled = true;
    }
    if (currentPage >= maxPage) {
      nextBtn.disabled = true;
    }
  }
  if (prevBtn) {
    prevBtn.addEventListener("click", async () => {
      if (currentPage > 1) {
        currentPage--;
        await loadPullHistory(currentPage);
        if (currentPage <= 1) {
          prevBtn.disabled = true;
        }
        nextBtn.disabled = false;
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", async () => {
      currentPage++;
      prevBtn.disabled = false;
      if (currentPage >= maxPage) {
        nextBtn.disabled = true;
      }
      await loadPullHistory(currentPage);
    });
  }
}

export async function attachPullButton(pullButton, count = 1) {
  pullButton.addEventListener("click", async function (e) {
    e.preventDefault();
    const response = await fetch(`/pull/${count}`, { method: "POST" });
    const data = await response.json();
    if (data.pulled_items) {
      const container = document.querySelector(".pulled-item");
      container.innerHTML = ""; // clear previous

      const queue = [...data.pulled_items];
      const foreground = document.querySelector(".pulled-item"); // enlarged item container
      const skipButton = document.querySelector("#skip-button"); // create a skip button in HTML
      const skipAllButton = document.querySelector("#skip-all-button");
      const background = document.querySelector(".pull-page");
      // Initial display
      showNextItem(queue, skipButton, skipAllButton, foreground, background);

      // Skip button event
      skipButton.onclick = () =>
        showNextItem(queue, skipButton, skipAllButton, foreground, background);
      skipAllButton.onclick = () =>
        skipAll(queue, skipButton, skipAllButton, foreground, background);
      // Update pull history
      loadPullHistory();

      // Update token count dynamically
      updateTokens(data);
    }
  });
}

function updateTokens(data) {
  document.querySelector(".tokens").textContent = `Tokens: ${data.tokens}`;
  document.querySelector(".pity").textContent = `Pity: ${data.pity}`;
  document.querySelector(
    ".small_pity"
  ).textContent = `Small pity: ${data.smallPity}`;
  const pullButton = document.getElementById("pull-btn-1");
  const pullButton10 = document.getElementById("pull-btn-10");
  if (data.tokens <= 0) {
    pullButton.classList.add("disabled");
    pullButton.disabled = true;
  }
  if (data.tokens <= 9) {
    pullButton10.classList.add("disabled");
    pullButton10.disabled = true;
  }
}

let currentIndex = 0;

function showNextItem(
  queue,
  skipButton,
  skipAllButton,
  foreground,
  background
) {
  if (currentIndex == queue.length && queue.length > 1) {
    skipAll(queue, skipButton, skipAllButton, foreground, background);
    return;
  }
  if (currentIndex >= queue.length) {
    foreground.style.display = "none";
    skipButton.style.display = "none";
    skipAllButton.style.display = "none";
    background.style.display = "block";
    currentIndex = 0;
    return;
  }
  if (foreground.classList.contains("skip-all-mode")) {
    foreground.classList.remove("skip-all-mode");
  }

  const item = queue[currentIndex];

  // Show fullscreen container
  foreground.style.display = "flex";
  skipButton.style.display = "inline-block";
  skipAllButton.style.display = "inline-block";
  if (queue.length == 1) {
    skipAllButton.style.display = "none";
  }
  foreground.innerHTML = "";

  //Hide background elements:
  background.style.display = "none";

  // Foreground display (enlarged)
  const itemDiv = document.createElement("div");
  itemDiv.className = `pulled-item-display ${item.rarity} enlarged`;
  itemDiv.innerHTML = `
        <img src="/media/${item.image}" alt="${item.name}" />
        <p><strong>${item.name}</strong></p>
        <p>${item.description}</p>
      `;
  foreground.appendChild(itemDiv);

  // Flash animation
  itemDiv.classList.add("flash");
  setTimeout(() => itemDiv.classList.remove("flash"), 500);

  currentIndex++;
}
// Show all remaining items at once
// Show all remaining items at once with enhanced grid display
function skipAll(queue, skipButton, skipAllButton, foreground, background) {
  // Clear any existing content and reset background
  foreground.innerHTML = "";
  foreground.style.display = "flex";

  // Add skip-all-mode class to enable grid layout
  foreground.classList.add("skip-all-mode");

  // Reset background to default (fixes the color bug)
  foreground.style.background =
    "linear-gradient(135deg, rgba(0, 0, 0, 0.95), rgba(20, 20, 40, 0.95))";

  // Create and append all remaining items
  for (let i = 0; i < queue.length; i++) {
    const item = queue[i];
    const itemDiv = document.createElement("div");
    itemDiv.className = `pulled-item-display ${item.rarity}`;

    // Enhanced HTML structure for better display
    itemDiv.innerHTML = `
      <img src="/media/${item.image}" alt="${item.name}" />
      <p><strong>${item.name}</strong></p>
      <p>${item.description}</p>
    `;

    // Add entrance animation with staggered delay
    itemDiv.style.opacity = "0";
    itemDiv.style.transform = "translateY(30px) scale(0.8)";
    itemDiv.style.transition =
      "all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)";

    foreground.appendChild(itemDiv);

    // Trigger entrance animation with delay
    setTimeout(() => {
      itemDiv.style.opacity = "1";
      itemDiv.style.transform = "translateY(0) scale(1)";
    }, i * 100); // Staggered animation
  }
  // Update state
  currentIndex = queue.length + 1; // mark all as shown
  skipAllButton.style.display = "none";
  skipButton.style.display = "inline-block";
}
