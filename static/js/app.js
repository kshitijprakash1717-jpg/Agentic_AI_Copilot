const chat = document.getElementById("chat");
const form = document.getElementById("chatForm");
const question = document.getElementById("question");
const trace = document.getElementById("trace");
const sourceUsed = document.getElementById("sourceUsed");

function escapeHtml(value = "") {
  return String(value).replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  })[character]);
}

function formatText(text = "") {
  return escapeHtml(text).replace(/\n/g, "<br>");
}

function addMessage(role, text, source = "", citations = []) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;

  const citeHtml = citations.length
    ? `<div class="citations"><strong>Sources</strong><br>${citations
        .map((citation) =>
          citation.url
            ? `<a href="${escapeHtml(citation.url)}" target="_blank" rel="noopener">${escapeHtml(citation.title)}</a>`
            : escapeHtml(citation.title),
        )
        .join("<br>")}</div>`
    : "";

  wrap.innerHTML = `<div class="avatar">AI</div><div class="bubble">${formatText(text)}${
    source
      ? `<div class="answer-source">Source: ${escapeHtml(source)}</div>`
      : ""
  }${citeHtml}</div>`;
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
}

function renderTrace(items = []) {
  trace.innerHTML = items.length
    ? items
        .map((item) => `<div class="trace-item">${escapeHtml(item)}</div>`)
        .join("")
    : '<div class="empty">No trace.</div>';
}

async function askAgent(query) {
  addMessage("user", query);
  question.value = "";
  renderTrace(["Running LangGraph workflow..."]);
  sourceUsed.textContent = "Running";

  const button = form.querySelector('button[type="submit"]');
  if (button) button.disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: query }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Request failed");

    addMessage(
      "assistant",
      data.answer,
      data.source_used,
      data.citations || [],
    );
    renderTrace(data.trace || []);
    sourceUsed.textContent = data.source_used;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    addMessage("assistant", `Error: ${message}`);
    renderTrace(["Request failed"]);
    sourceUsed.textContent = "Error";
  } finally {
    if (button) button.disabled = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = question.value.trim();
  if (query) askAgent(query);
});

document.querySelectorAll(".example").forEach((button) => {
  button.addEventListener("click", () => askAgent(button.textContent.trim()));
});

const modal = document.getElementById("uploadModal");
document.getElementById("openUpload").onclick = () =>
  modal.classList.remove("hidden");
document.getElementById("closeUpload").onclick = () =>
  modal.classList.add("hidden");
document.getElementById("uploadBtn").onclick = async () => {
  const file = document.getElementById("fileInput").files[0];
  const key = document.getElementById("adminKey").value;
  const status = document.getElementById("uploadStatus");

  if (!file) {
    status.textContent = "Choose a file first.";
    return;
  }

  status.textContent = "Indexing document...";
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/api/ingest", {
      method: "POST",
      headers: { "X-Admin-Key": key },
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Upload failed");

    status.textContent = `Indexed ${data.file}: ${data.chunks} chunks.`;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    status.textContent = `Error: ${message}`;
  }
};
