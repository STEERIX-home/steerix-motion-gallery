const LEFT_HALF_PATH = [
  "M 38 42",
  "H 52",
  "L 80 80",
  "H 66",
  "L 73 89",
  "L 59 110",
  "H 44",
  "L 62 85",
  "H 25",
  "L 30 75",
  "H 62",
  "Z",
].join(" ");

function buildMarkup({ motion = "2", color = "#ffffff", duration = 1.8, label = "" } = {}) {
  const safeMotion = motion === "1" ? "1" : "2";
  const aria = label
    ? `role="status" aria-label="${label.replace(/"/g, "&quot;")}"`
    : 'aria-hidden="true"';

  return `
    <div class="steerix-loader" data-motion="${safeMotion}" ${aria}
      style="--steerix-color:${color};--steerix-duration:${duration}s">
      <div class="steerix-loader__stage">
        <div class="steerix-loader__assembly">
          <div class="steerix-loader__piece steerix-loader__piece--left">
            <svg viewBox="0 0 160 160" focusable="false" aria-hidden="true">
              <path d="${LEFT_HALF_PATH}" fill="${color}" />
            </svg>
          </div>
          <div class="steerix-loader__piece steerix-loader__piece--right">
            <svg viewBox="0 0 160 160" focusable="false" aria-hidden="true">
              <path d="${LEFT_HALF_PATH}" transform="rotate(180 80 80)" fill="${color}" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function mountSteerixLoader(container, options = {}) {
  container.innerHTML = buildMarkup(options);
  return container.querySelector(".steerix-loader");
}

export function applySteerixLoaderStyle(loader, prop, value) {
  if (!loader) return;

  if (prop === "color") {
    loader.style.setProperty("--steerix-color", value);
    for (const path of loader.querySelectorAll("path")) {
      path.setAttribute("fill", value);
    }
    return;
  }

  if (prop === "duration") {
    loader.style.setProperty("--steerix-duration", `${value}s`);
  }
}

export { LEFT_HALF_PATH, buildMarkup };
