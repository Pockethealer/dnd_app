export function createElement(tag, options = {}, children = []) {
  const el = document.createElement(tag);
  Object.entries(options).forEach(([key, value]) => {
    if (key === 'className') el.className = value;
    else if (key === 'textContent') el.textContent = value;
    else if (key === 'innerHTML') el.innerHTML = value;
    else if (key === 'attributes') {
      Object.entries(value).forEach(([attr, val]) => el.setAttribute(attr, val));
    } else {
      el[key] = value;
    }
  });
  children.forEach(child => el.appendChild(child));
  return el;
}

export function formatKey(key) {
  // Step 1: Replace underscores with spaces (for snake_case)
  let result = key.replace(/_/g, ' ');
  // Step 2: Add spaces before uppercase letters (for camelCase)
  result = result.replace(/([A-Z])/g, ' $1');
  // Step 3: Capitalize the first letter of the result and lowercase the rest of each word
  result = result.toLowerCase().replace(/\b\w/g, char => char.toUpperCase());
  // Step 4: Trim any extra spaces
  return result.trim();
}

export function formatDateTimeLocal(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  if (isNaN(date)) return ""; // invalid date fallback

  // Pad helper for two digits
  const pad = (n) => (n < 10 ? "0" + n : n);

  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());

  return `${year}-${month}-${day}T${hours}:${minutes}`;
}