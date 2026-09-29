import { blockIfFileProtocol, showBootError } from "./dev-guard.js";
import { MOTION_LIST } from "./motions.js";
import { mountSteerixLoader } from "./steerix-loader.js";

if (blockIfFileProtocol()) {
  throw new Error("file-protocol-blocked");
}

function renderCard(motion) {
  const article = document.createElement("article");
  const link = document.createElement("a");
  link.className = "card-link";
  link.href = `./motion.html?id=${motion.id}`;
  link.dataset.editable = String(motion.editable);

  const viewport = document.createElement("div");
  viewport.className = "viewport";
  if (motion.zoom) viewport.style.setProperty("--media-zoom", String(motion.zoom));

  if (motion.type === "live") {
    const host = document.createElement("div");
    host.className = "steerix-loader-host";
    host.style.width = "220px";
    host.style.height = "220px";
    mountSteerixLoader(host, {
      motion: motion.motion,
      color: motion.defaultColor,
      duration: motion.defaultDuration,
      label: motion.title,
    });
    viewport.appendChild(host);
  } else if (motion.type === "gif") {
    const img = document.createElement("img");
    img.src = motion.gif;
    img.alt = motion.title;
    img.decoding = "async";
    viewport.appendChild(img);
  }

  const copy = document.createElement("div");
  copy.className = "copy";
  copy.innerHTML = `
    <h2>${motion.title}</h2>
    <p class="meta">${motion.meta}</p>
  `;

  link.append(viewport, copy);
  article.appendChild(link);
  return article;
}

const gallery = document.querySelector("[data-gallery]");

if (!gallery) {
  showBootError("갤러리 컨테이너를 찾을 수 없습니다.");
} else {
  try {
    for (const motion of MOTION_LIST) {
      gallery.appendChild(renderCard(motion));
    }
  } catch (error) {
    console.error(error);
    showBootError("모션 카드를 렌더링하는 중 오류가 발생했습니다. 브라우저 콘솔을 확인해주세요.");
  }
}
