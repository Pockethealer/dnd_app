export function gallery(modal, modalContent) {
  document.querySelectorAll(".gallery-item").forEach((item) => {
    item.addEventListener("click", () => {
      const src = item.dataset.src;
      if (src.match(/\.(png|jpg|jpeg|gif|webp|ico)$/i)) {
        modalContent.innerHTML = `<img src="${src}">`;
      } else if (src.match(/\.mp4$/i)) {
        modalContent.innerHTML = `<video src="${src}" controls autoplay></video>`;
      } else if (src.match(/\.pdf$/i)) {
        return;
      } else {
        modalContent.innerHTML = `<a href="${src}" target="_blank">Open File</a>`;
      }
      modal.style.display = "flex";
    });
  });

  modal.addEventListener("click", () => {
    modal.style.display = "none";
    modalContent.innerHTML = "";
  });
}
