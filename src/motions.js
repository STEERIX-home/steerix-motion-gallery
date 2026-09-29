export const MOTIONS = {
  "motion-1": {
    id: "motion-1",
    title: "Motion 1 · Diagonal slide",
    meta: "live · 320×320 · 60fps · 1.8s",
    editable: true,
    type: "live",
    motion: "1",
    defaultColor: "#ffffff",
    defaultDuration: 1.8,
    swatches: ["#ffffff", "#55f18d", "#78ffa8", "#ff6b9d"],
    description:
      "두 조각이 대각선 방향으로 미끄러졌다 돌아오는 Motion 1입니다. steerix-loader Web Component로 실시간 렌더링됩니다.",
  },
  "motion-2": {
    id: "motion-2",
    title: "Motion 2 · Dock & rotate",
    meta: "live · 320×320 · 60fps · 1.8s",
    editable: true,
    type: "live",
    motion: "2",
    defaultColor: "#ffffff",
    defaultDuration: 1.8,
    swatches: ["#ffffff", "#55f18d", "#ffd166", "#4cc9f0"],
    description:
      "두 조각이 수평으로 맞물린 뒤 360° 회전합니다. --steerix-color와 --steerix-duration을 조정할 수 있습니다.",
  },
  "motion-2-random": {
    id: "motion-2-random",
    title: "Motion 2 · Random colors",
    meta: "GIF · 1920×1080 · 60fps · 1.8s",
    editable: false,
    type: "gif",
    gif: "assets/gifs/steerix-loader-motion-2-fullhd-random-60fps.gif",
    zoom: 2.15,
    description:
      "프레임마다 색이 바뀌는 Full HD GIF입니다. 픽셀 단위로 사전 렌더링되어 있어 런타임 색상 속성이 없습니다.",
  },
  "motion-2-code-rain": {
    id: "motion-2-code-rain",
    title: "Motion 2 · Code rain",
    meta: "GIF · 1920×1080 · 60fps · 1.8s",
    editable: false,
    type: "gif",
    gif: "assets/gifs/steerix-loader-motion-2-fullhd-code-rain-60fps.gif",
    zoom: 2.15,
    description:
      "코드 레인 배경이 포함된 Full HD GIF입니다. 로고 색상·배경 효과는 렌더 파이프라인에 고정되어 있어 수정할 수 없습니다.",
  },
  "motion-draft": {
    id: "motion-draft",
    title: "Motion Draft · Dock & rotate",
    meta: "live · 원본 WebM 대체 · 1.8s",
    editable: true,
    type: "live",
    motion: "2",
    defaultColor: "#ffffff",
    defaultDuration: 1.8,
    swatches: ["#ffffff", "#55f18d", "#ff6b9d"],
    description:
      "보내주신 Draft.webm(222×132, 3.0s)은 Motion 2와 달리 360° 회전 구간이 거의 없고 대부분의 프레임이 검은 화면입니다. Mediabunny로 녹화된 저해상도 클립이라 동일한 Motion 2 컴포넌트로 대체 표시합니다.",
    webm: "assets/videos/steerix-motion-draft.webm",
  },
};

export const MOTION_LIST = Object.values(MOTIONS);

export function getMotion(id) {
  return MOTIONS[id] ?? null;
}
