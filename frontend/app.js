const API = "https://crochet-pattern-gen.onrender.com";

// US->UK term mapping for display toggle (applied client-side, model always outputs US)
const US_TO_UK_TERMS = [
  ["single crochet", "double crochet"],
  ["half double crochet", "half treble crochet"],
  ["double crochet", "treble crochet"],
  ["treble crochet", "double treble crochet"],
];
const US_TO_UK_ABBR = [
  [/\bsc\b/g, "dc"],
  [/\bhdc\b/g, "htr"],
  [/\bdc\b/g, "tr"],
  [/\btr\b/g, "dtr"],
];

function convertToUK(text) {
  // Single-pass: match longest terms first to prevent cascading
  const termMap = new Map(US_TO_UK_TERMS);
  const sortedTerms = Array.from(termMap.keys()).sort((a, b) => b.length - a.length);
  const termPattern = new RegExp(
    "\\b(" + sortedTerms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")\\b",
    "gi"
  );
  let out = text.replace(termPattern, m => termMap.get(m.toLowerCase()) || m);
  for (const [re, to] of US_TO_UK_ABBR) out = out.replace(re, to);
  return out;
}

let currentPattern = null;
let currentId = null;
let useUK = false;
let currentInspiration = [];

document.getElementById("generateBtn").addEventListener("click", async () => {
  const desc = document.getElementById("description").value.trim();
  if (!desc) return;
  const btn = document.getElementById("generateBtn");
  btn.disabled = true;
  btn.textContent = "Generating...";
  try {
    const res = await fetch(`${API}/generate`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({description: desc}),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    currentPattern = data.pattern;
    currentId = data.id;
    currentInspiration = data.inspiration || [];
    renderPattern(data.pattern, data.inspiration);
    document.getElementById("output").style.display = "block";
  } catch (e) {
    alert("Generation failed: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate Pattern";
  }
});

document.getElementById("ukToggle").addEventListener("change", (e) => {
  useUK = e.target.checked;
  if (currentPattern) renderPattern(currentPattern, currentInspiration);
});

document.getElementById("exportBtn").addEventListener("click", () => {
  window.open(`${API}/export/${currentId}?uk=${useUK}`, "_blank");
});

document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.tab).classList.add("active");
  });
});

function conv(t) { return useUK ? convertToUK(t) : t; }

function renderPattern(pattern, inspiration) {
  const el = document.getElementById("patternText");
  let html = "<div class=\"pattern-text\">";

  if (pattern.author || pattern.source_url) {
    html += "<div class=\"attribution\">Pattern by " + (pattern.author || "Unknown");
    if (pattern.source_url) {
      html += " &mdash; <a href=\"" + pattern.source_url + "\" target=\"_blank\">" + pattern.source_url + "</a>";
    }
    html += "</div>";
  }

  html += "<h3>Materials</h3><ul>";
  for (const y of pattern.materials.yarn) {
    html += "<li>" + y.weight + " weight yarn" + (y.color ? ", " + y.color : "") + (y.amount ? " (" + y.amount + ")" : "") + "</li>";
  }
  html += "<li>Hook: " + pattern.materials.hook + "</li>";
  for (const n of (pattern.materials.notions || [])) html += "<li>" + n + "</li>";
  html += "</ul>";

  if (pattern.abbreviations && Object.keys(pattern.abbreviations).length) {
    html += "<h3>Abbreviations</h3><p>";
    html += Object.entries(pattern.abbreviations).map(([a, m]) => a + ": " + m).join(", ");
    html += "</p>";
  }

  for (const part of pattern.parts) {
    html += "<h3>" + part.name + (part.make > 1 ? " (make " + part.make + ")" : "") + "</h3>";
    for (const r of part.rounds) {
      html += "<div class=\"round-row\"><span class=\"round-num\">Rnd " + r.round + "</span><span>" + conv(r.instruction) + "</span><span class=\"round-count\">(" + r.stitch_count + ")</span></div>";
    }
  }

  if (pattern.assembly) html += "<h3>Assembly</h3><p>" + conv(pattern.assembly) + "</p>";
  html += "</div>";
  el.innerHTML = html;

  const inspEl = document.getElementById("inspiration");
  if (inspiration && inspiration.length) {
    const items = inspiration.map(s => {
      const link = s.source_url ? "<a href=\"" + s.source_url + "\" target=\"_blank\">" + s.title + "</a>" : s.title;
      return "<li>" + link + (s.author ? " by " + s.author : "") + "</li>";
    }).join("");
    inspEl.innerHTML = "<details class=\"inspiration\"><summary>Inspired by " + inspiration.length + " pattern(s)</summary><ul>" + items + "</ul></details>";
    inspEl.style.display = "block";
  } else {
    inspEl.style.display = "none";
  }

  document.getElementById("patternJson").textContent = JSON.stringify(pattern, null, 2);
}
