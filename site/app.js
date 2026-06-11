async function loadRecommendations() {
  const response = await fetch("recommendations.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load recommendations: ${response.status}`);
  }
  return response.json();
}

function render(payload) {
  const container = document.getElementById("recommendations");
  const runDate = document.getElementById("runDate");
  runDate.textContent = payload.run_date ? `Run date: ${payload.run_date}` : "";

  if (!payload.recommendations || payload.recommendations.length === 0) {
    container.innerHTML = '<p class="empty">No matching papers for this run.</p>';
    return;
  }

  const groups = new Map();
  const sectionLabels = payload.section_labels || {};
  payload.recommendations.forEach((paper) => {
    const section = paper.sections?.[0] || "exploratory";
    if (!groups.has(section)) groups.set(section, []);
    groups.get(section).push(paper);
  });

  container.innerHTML = Array.from(groups.entries()).map(([section, papers]) => {
    const label = sectionLabels[section] || "Exploratory but Maybe Relevant";
    const items = papers.map(renderPaper).join("");
    return `<section class="section"><h2>${escapeHtml(label)}</h2>${items}</section>`;
  }).join("");
}

function renderPaper(paper) {
  const feedbackBase = "feedback.html";
  const section = paper.sections?.[0] || "";
  const likeUrl = `${feedbackBase}?paper_id=${encodeURIComponent(paper.paper_id)}&rating=like&source=page&section=${encodeURIComponent(section)}`;
  const dislikeUrl = `${feedbackBase}?paper_id=${encodeURIComponent(paper.paper_id)}&rating=dislike&source=page&section=${encodeURIComponent(section)}`;
  const authors = Array.isArray(paper.authors) ? paper.authors.join(", ") : "";
  const categories = Array.isArray(paper.categories) ? paper.categories.join(", ") : "";
  return `
    <article class="paper" id="paper-${escapeAttr(paper.paper_id)}">
      <div class="paper-meta">#${paper.rank} · score ${paper.score} · ${escapeHtml(categories)}</div>
      <h3>${escapeHtml(paper.title)}</h3>
      <p class="authors">${escapeHtml(authors)}</p>
      <p>${escapeHtml(paper.abstract || "")}</p>
      <div class="actions">
        <a href="${likeUrl}">Like</a>
        <a href="${dislikeUrl}">Dislike</a>
      </div>
    </article>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll(" ", "-");
}

loadRecommendations().then(render).catch((error) => {
  document.getElementById("runDate").textContent = "Failed to load recommendations";
  document.getElementById("recommendations").innerHTML = `<pre class="error">${escapeHtml(error.message)}</pre>`;
});
