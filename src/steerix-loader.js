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

const template = document.createElement("template");

template.innerHTML = `
  <style>
    :host {
      --steerix-size: 160px;
      --steerix-color: #ffffff;
      --steerix-duration: 1.8s;

      display: inline-block;
      width: var(--steerix-size);
      aspect-ratio: 1;
      color: var(--steerix-color);
      contain: layout paint style;
      vertical-align: middle;
    }

    .stage {
      position: relative;
      width: 100%;
      height: 100%;
      isolation: isolate;
    }

    .assembly,
    .piece {
      position: absolute;
      inset: 0;
      will-change: transform;
      animation-duration: var(--steerix-duration);
      animation-iteration-count: infinite;
    }

    .assembly {
      transform-origin: 50% 50%;
      animation-name: motion-2-turn;
      animation-timing-function: cubic-bezier(0.65, 0, 0.35, 1);
    }

    .piece--left {
      animation-name: motion-2-left;
      animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    }

    .piece--right {
      animation-name: motion-2-right;
      animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    }

    :host([motion="1"]) .assembly {
      animation-name: none;
    }

    :host([motion="1"]) .piece--left {
      animation-name: motion-1-left;
    }

    :host([motion="1"]) .piece--right {
      animation-name: motion-1-right;
    }

    svg {
      position: absolute;
      inset: 0;
      display: block;
      width: 100%;
      height: 100%;
      overflow: visible;
      shape-rendering: geometricPrecision;
    }

    path {
      fill: currentColor;
      vector-effect: non-scaling-stroke;
    }

    @keyframes motion-1-left {
      0%, 100% {
        transform: translate(0, 0);
      }

      50% {
        transform: translate(1.875%, 2.5%);
      }
    }

    @keyframes motion-1-right {
      0%, 100% {
        transform: translate(0, 0);
      }

      50% {
        transform: translate(-1.875%, -2.5%);
      }
    }

    @keyframes motion-2-left {
      0%, 100% {
        transform: translateX(0);
      }

      26%, 72% {
        transform: translateX(4.375%);
      }
    }

    @keyframes motion-2-right {
      0%, 100% {
        transform: translateX(0);
      }

      26%, 72% {
        transform: translateX(-4.375%);
      }
    }

    @keyframes motion-2-turn {
      0%, 26% {
        transform: rotate(0deg);
      }

      72%, 100% {
        transform: rotate(360deg);
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .assembly,
      .piece {
        animation: none;
        transform: none;
      }
    }
  </style>

  <span class="stage" part="stage" aria-hidden="true">
    <span class="assembly" part="assembly">
      <span class="piece piece--left" part="left-half">
        <svg viewBox="0 0 160 160" focusable="false">
          <path d="${LEFT_HALF_PATH}" />
        </svg>
      </span>

      <span class="piece piece--right" part="right-half">
        <svg viewBox="0 0 160 160" focusable="false">
          <path d="${LEFT_HALF_PATH}" transform="rotate(180 80 80)" />
        </svg>
      </span>
    </span>
  </span>
`;

export class SteerixLoader extends HTMLElement {
  static observedAttributes = ["label"];

  constructor() {
    super();
    this.attachShadow({ mode: "open" }).append(template.content.cloneNode(true));
  }

  connectedCallback() {
    this.#syncAccessibility();
  }

  attributeChangedCallback() {
    this.#syncAccessibility();
  }

  #syncAccessibility() {
    const label = this.getAttribute("label")?.trim();

    if (label) {
      this.setAttribute("role", "status");
      this.setAttribute("aria-label", label);
    } else {
      this.removeAttribute("role");
      this.removeAttribute("aria-label");
    }
  }
}

if (!customElements.get("steerix-loader")) {
  customElements.define("steerix-loader", SteerixLoader);
}

export { LEFT_HALF_PATH };
