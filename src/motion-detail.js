import { blockIfFileProtocol, showBootError } from "./dev-guard.js";
import { getMotion } from "./motions.js";
import { applySteerixLoaderStyle, mountSteerixLoader } from "./steerix-loader.js";

if (blockIfFileProtocol()) {
  throw new Error("file-protocol-blocked");
}

function syncSwatches(container, activeColor) {
  for (const swatch of container.querySelectorAll(".swatch[data-color]")) {
    swatch.setAttribute(
      "aria-pressed",
      String(swatch.dataset.color.toLowerCase() === activeColor.toLowerCase()),
    );
  }
}

function renderPreview(motion, container) {
  container.style.removeProperty("--media-zoom");
  container.innerHTML = "";

  if (motion.type === "live") {
    const host = document.createElement("div");
    host.className = "steerix-loader-host";
    host.style.width = "320px";
    host.style.height = "320px";
    container.appendChild(host);
    return mountSteerixLoader(host, {
      motion: motion.motion,
      color: motion.defaultColor,
      duration: motion.defaultDuration,
      label: motion.title,
    });
  }

  if (motion.type === "gif") {
    const img = document.createElement("img");
    img.src = motion.gif;
    img.alt = motion.title;
    img.decoding = "async";
    if (motion.zoom) container.style.setProperty("--media-zoom", String(motion.zoom));
    container.appendChild(img);
    return null;
  }

  return null;
}

function renderControls(motion, loader, panel) {
  if (!motion.editable || !loader) {
    const note = document.createElement("p");
    note.className = "panel-note";
    note.textContent = motion.description;
    panel.appendChild(note);
    return;
  }

  const note = document.createElement("p");
  note.className = "panel-note";
  note.innerHTML = motion.description;
  if (motion.webm) {
    note.innerHTML += ` <a href="${motion.webm}">원본 WebM 보기</a>`;
  }
  panel.appendChild(note);

  const colorRow = document.createElement("div");
  colorRow.className = "control-row";
  colorRow.innerHTML = `
    <label for="detail-color">
      Logo color
      <output id="detail-color-output">${motion.defaultColor}</output>
    </label>
    <input id="detail-color" type="color" value="${motion.defaultColor}" />
  `;
  panel.appendChild(colorRow);

  const swatches = document.createElement("div");
  swatches.className = "swatches";
  swatches.setAttribute("role", "group");
  swatches.setAttribute("aria-label", "Color presets");

  for (const color of motion.swatches) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "swatch";
    button.dataset.color = color;
    button.style.background = color;
    button.setAttribute("aria-label", color);
    swatches.appendChild(button);
  }

  panel.appendChild(swatches);

  const durationRow = document.createElement("div");
  durationRow.className = "control-row";
  durationRow.innerHTML = `
    <label for="detail-duration">
      Duration
      <output id="detail-duration-output">${motion.defaultDuration}s</output>
    </label>
    <input
      id="detail-duration"
      type="range"
      min="0.8"
      max="3"
      step="0.1"
      value="${motion.defaultDuration}"
    />
  `;
  panel.appendChild(durationRow);

  const colorInput = panel.querySelector("#detail-color");
  const durationInput = panel.querySelector("#detail-duration");
  const colorOutput = panel.querySelector("#detail-color-output");
  const durationOutput = panel.querySelector("#detail-duration-output");

  colorInput.addEventListener("input", () => {
    applySteerixLoaderStyle(loader, "color", colorInput.value);
    colorOutput.textContent = colorInput.value;
    syncSwatches(panel, colorInput.value);
  });

  durationInput.addEventListener("input", () => {
    applySteerixLoaderStyle(loader, "duration", durationInput.value);
    durationOutput.textContent = `${durationInput.value}s`;
  });

  for (const swatch of swatches.querySelectorAll(".swatch")) {
    swatch.addEventListener("click", () => {
      colorInput.value = swatch.dataset.color;
      applySteerixLoaderStyle(loader, "color", swatch.dataset.color);
      colorOutput.textContent = swatch.dataset.color;
      syncSwatches(panel, swatch.dataset.color);
    });
  }

  syncSwatches(panel, motion.defaultColor);
}

export function initMotionDetail() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  const motion = getMotion(id);

  const root = document.querySelector("[data-detail-root]");
  if (!motion) {
    document.title = "Motion not found · Steerix Motion Gallery";
    root.innerHTML = `
      <div class="not-found">
        <h1>Motion not found</h1>
        <p class="lede">요청한 모션을 찾을 수 없습니다.</p>
        <p><a href="./">갤러리로 돌아가기</a></p>
      </div>
    `;
    return;
  }

  document.title = `${motion.title} · Steerix Motion Gallery`;

  const preview = root.querySelector("[data-detail-preview]");
  const panel = root.querySelector("[data-detail-panel]");
  const title = root.querySelector("[data-detail-title]");
  const meta = root.querySelector("[data-detail-meta]");

  title.textContent = motion.title;
  meta.textContent = motion.meta;

  const loader = renderPreview(motion, preview);
  renderControls(motion, loader, panel);
}
