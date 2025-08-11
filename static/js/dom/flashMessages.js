// flashMessages.js, some error here TODO

export function showFlashMessage(message, type = 'success', duration = 4000) {
  const container = document.getElementById('flash-container');
  if (!container) return;
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('flash-message');

  // Determine style classes
  const isError = type === 'error';
  const classMap = {
    error: 'flash-error',
    success: 'flash-success',
    info: 'flash-info',
    warning: 'flash-warning',
  };

  // Support both flash-* and Bootstrap-like alert-*
  const className = classMap[type];
  msgDiv.classList.add(className);

  // Message text
  const msgText = document.createElement('span');
  msgText.textContent = message;
  msgDiv.appendChild(msgText);

  // Close button
  const closeBtn = document.createElement('button');
  closeBtn.classList.add('close-btn');
  closeBtn.innerHTML = '&times;';
  closeBtn.setAttribute('aria-label', 'Close');
  closeBtn.onclick = () => fadeOutAndRemove(msgDiv);
  msgDiv.appendChild(closeBtn);

  // Append to container
  container.appendChild(msgDiv);

  // Auto-dismiss
  setTimeout(() => fadeOutAndRemove(msgDiv), duration);
}

function fadeOutAndRemove(element) {
  element.style.animation = 'slideUpFadeOut 0.4s forwards';
  element.addEventListener('animationend', () => {
    if (element.parentNode) {
      element.parentNode.removeChild(element);
    }
  });
}
