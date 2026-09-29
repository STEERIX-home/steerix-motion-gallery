const SERVER_HINT = `
  <main style="max-width:640px;margin:0 auto;padding:48px 24px;font-family:Inter,system-ui,sans-serif;line-height:1.6;color:#f5f7f8;background:#030506;min-height:100svh">
    <p style="margin:0 0 8px;color:#55f18d;font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase">Local preview required</p>
    <h1 style="margin:0 0 16px;font-size:2rem;line-height:1.1">로컬 서버에서 열어야 합니다</h1>
    <p style="margin:0 0 16px;color:rgb(236 243 239 / 0.72)">
      이 갤러리는 ES Module(<code>import</code>)을 사용합니다.
      <code>index.html</code> 파일을 Finder에서 더블클릭하면 모듈 로드가 차단되어 카드와 애니메이션이 표시되지 않습니다.
    </p>
    <pre style="margin:0 0 16px;padding:16px;border-radius:16px;background:rgb(255 255 255 / 0.05);overflow:auto">cd steerix-motion-gallery
./start.sh</pre>
    <p style="margin:0;color:rgb(236 243 239 / 0.72)">
      실행 후 브라우저에서
      <a href="http://localhost:8765/" style="color:#78ffa8">http://localhost:8765/</a>
      를 열어주세요.
    </p>
  </main>
`;

export function blockIfFileProtocol() {
  if (location.protocol !== "file:") return false;

  const render = () => {
    document.body.innerHTML = SERVER_HINT;
    document.title = "Local server required · Steerix Motion Gallery";
  };

  if (document.body) render();
  else document.addEventListener("DOMContentLoaded", render, { once: true });

  return true;
}

export function showBootError(message) {
  const gallery = document.querySelector("[data-gallery], [data-detail-root]");
  if (!gallery) return;

  gallery.innerHTML = `
    <div style="padding:24px;border:1px solid rgb(255 107 157 / 0.35);border-radius:16px;background:rgb(255 107 157 / 0.08);color:#ffd5e3">
      <strong>갤러리를 불러오지 못했습니다.</strong>
      <p style="margin:8px 0 0">${message}</p>
    </div>
  `;
}
