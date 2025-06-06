window.i18nText = {};
async function loadLanguageData(lang) {
  const sources = ["/static/Language/basis.json",
                  "/static/Language/info.json",
                  "/static/Language/title.json",
                  "/static/Language/routeplan.json"];
  const langData = {};

  for (let src of sources) {
    try {
      const res = await fetch(src);
      const data = await res.json();
      for (let key in data) {
        langData[key] = data[key];
      }
    } catch (e) {
      console.error(`Failed to load language file：${src}`, e);
    }
  }

  window.i18nText = langData;
  
  // Apply to HTML
  document.querySelectorAll("[data-langkey]").forEach(el => {
    const baseKey = el.getAttribute("data-langkey");
    const fullKey = `${baseKey}_${lang}`;
    el.innerText = langData[fullKey] || `[Missing: ${fullKey}]`;
  });
  
  populateSidebar(document.getElementById("filterCrowd").value);
}

document.addEventListener("DOMContentLoaded", function () {
  const urlParams = new URLSearchParams(window.location.search);
  const currentLang = urlParams.get("lang") || "zh";
  document.getElementById("langSelect").value = currentLang;
  loadLanguageData(currentLang);

  document.getElementById("langSelect").addEventListener("change", function () {
    const newLang = this.value;
    const u = new URL(window.location.href);
    u.searchParams.set("lang", newLang);
    window.location.href = u.toString();  // Reload and trigger language switch
  });
});

const iframe = document.getElementById("mapFrame");
if (iframe) {
  const baseURL = iframe.getAttribute("data-mapbase");
  const mapLang = lang === "zh" ? "zh-TW" : lang;

  // 把原來 URL 中的 hl=xxx 改掉（保留其他參數）
  const url = new URL(baseURL);
  url.searchParams.set("hl", mapLang);

  iframe.src = url.toString();
}
console.log("[LanguageLoader] currentLang =", lang);
