const params = new URLSearchParams(window.location.search);
const paperId = params.get("paper_id");
const rating = params.get("rating");
const source = params.get("source") || "page";
const titleEl = document.getElementById("statusTitle");
const detailEl = document.getElementById("statusDetail");

recordFeedback().catch((error) => {
  titleEl.textContent = "Feedback was not recorded";
  detailEl.textContent = error.message;
});

async function recordFeedback() {
  if (!paperId || !["like", "dislike"].includes(rating)) {
    throw new Error("Missing or invalid feedback parameters.");
  }

  const config = window.RECOMMENDER_CONFIG || {};
  if (!config.supabaseUrl || !config.supabaseAnonKey) {
    titleEl.textContent = "Feedback captured locally";
    detailEl.textContent = "Supabase is not configured yet. Configure SUPABASE_URL and SUPABASE_ANON_KEY in GitHub Variables to persist feedback.";
    return;
  }

  const response = await fetch(`${config.supabaseUrl.replace(/\/$/, "")}/rest/v1/feedback_events`, {
    method: "POST",
    headers: {
      apikey: config.supabaseAnonKey,
      Authorization: `Bearer ${config.supabaseAnonKey}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify({
      paper_id: paperId,
      rating,
      source,
      section: params.get("section") || null,
    }),
  });

  if (!response.ok) {
    throw new Error(`Supabase rejected feedback: ${response.status}`);
  }

  titleEl.textContent = "Feedback recorded";
  detailEl.textContent = `Recorded ${rating} for ${paperId}.`;
}
