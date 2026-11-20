"use strict";

const byId = (id) => document.getElementById(id);
const page = window.location.pathname;
const isHistory = page.startsWith("/revisions");
const preview = byId("preview");
let activeRevision;
let previewRequest;

async function readJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error("Archive request failed");
  return response.json();
}

function fileURL(revision, action, name) {
  const query = new URLSearchParams({file: name});
  return `/api/revisions/${revision}/${action}?${query}`;
}

function showFiles(revision, list) {
  activeRevision = revision;
  for (const name of revision.files) {
    const row = byId("file-row").content.cloneNode(true);
    row.querySelector(".file-name").textContent = name;
    const previewLink = row.querySelector(".preview-link");
    previewLink.href = `?${new URLSearchParams({preview: name})}`;
    previewLink.setAttribute("aria-label", `Preview ${name}`);
    previewLink.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      window.history.pushState({archivePreview: true}, "", previewLink.href);
      updatePreview();
    });
    const download = row.querySelector(".download-link");
    download.href = fileURL(revision.id, "download", name);
    download.setAttribute("aria-label", `Download ${name}`);
    list.append(row);
  }
}

async function updatePreview() {
  previewRequest?.abort();
  const name = new URLSearchParams(window.location.search).get("preview");
  if (!activeRevision?.files.includes(name)) {
    if (preview.open) preview.close();
    return;
  }

  const {id} = activeRevision;
  const text = byId("preview-text");
  byId("preview-title").textContent = name;
  byId("preview-context").textContent = `Revision ${id} / File preview`;
  byId("preview-download").href = fileURL(id, "download", name);
  text.textContent = "Loading preview…";
  if (!preview.open) preview.showModal();

  const request = new AbortController();
  previewRequest = request;
  try {
    const response = await fetch(fileURL(id, "preview", name), {signal: request.signal});
    if (!response.ok) throw new Error("Preview request failed");
    const body = await response.text();
    if (!request.signal.aborted) text.textContent = body;
  } catch {
    if (!request.signal.aborted) text.textContent = "Preview unavailable. Try opening the file again or download it.";
  }
}

function closePreview() {
  if (window.history.state?.archivePreview) {
    window.history.back();
  } else {
    window.history.replaceState(null, "", page);
    updatePreview();
  }
}

byId("close-preview").addEventListener("click", closePreview);
preview.addEventListener("cancel", (event) => {
  event.preventDefault();
  closePreview();
});
window.addEventListener("popstate", updatePreview);

async function showArchive() {
  const archive = await readJSON("/api/archive");
  byId("case-reference").textContent = archive.case_reference;
  byId("current-revision").textContent = archive.id;
  showFiles(archive, byId("current-files"));
  byId("archive").hidden = false;
}

async function showHistory() {
  const selected = page.split("/")[2];
  const {revisions} = await readJSON("/api/revisions");
  const current = revisions.find((revision) => revision.current);
  const snapshot = await readJSON(`/api/revisions/${selected || current.id}`);

  for (const revision of revisions) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = `/revisions/${revision.id}#revision-files`;
    if (revision.id === snapshot.id) link.setAttribute("aria-current", "true");
    const number = document.createElement("span");
    number.className = "mono";
    number.textContent = revision.id;
    const labels = document.createElement("span");
    const title = document.createElement("span");
    title.className = "timeline-title";
    title.textContent = revision.title;
    labels.append(title);
    if (revision.current) {
      const status = document.createElement("span");
      status.className = "timeline-status";
      status.textContent = "Current";
      labels.append(status);
    }
    link.append(number, labels);
    item.append(link);
    byId("timeline").append(item);
  }

  byId("revision-number").textContent = `Revision ${snapshot.id}${snapshot.current ? " / Current" : ""}`;
  byId("revision-title").textContent = snapshot.title;
  byId("revision-description").textContent = snapshot.description;
  byId("history-back").hidden = !selected;
  byId("archive-back").hidden = Boolean(selected);
  showFiles(snapshot, byId("historical-files"));
  byId("history").hidden = false;
  if (window.location.hash === "#revision-files") {
    const details = byId("revision-files");
    details.focus({preventScroll: true});
    if (window.matchMedia("(max-width: 790px)").matches) details.scrollIntoView();
  }
}

function showVault() {
  const form = byId("vault-form");
  const documentInput = byId("document");
  const fields = byId("vault-fields");
  const submit = byId("verify");
  const error = byId("vault-error");
  form.addEventListener("input", () => { error.hidden = true; });
  documentInput.addEventListener("change", () => {
    documentInput.setCustomValidity(documentInput.files[0]?.size > 16 * 1024
      ? "Choose a document that is 16 KiB or smaller." : "");
    documentInput.reportValidity();
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (fields.disabled) return;
    const body = new FormData(form);
    fields.disabled = true;
    error.hidden = true;
    submit.textContent = "Verifying…";
    try {
      const response = await fetch(form.action, {method: "POST", body});
      const result = await response.json();
      if (!response.ok) {
        error.textContent = result.message;
        error.hidden = false;
        return;
      }
      form.reset();
      form.hidden = true;
      byId("success-message").textContent = result.message;
      byId("flag").textContent = result.flag;
      byId("unlocked").hidden = false;
      byId("success-message").focus();
    } catch {
      error.textContent = "The vault could not be reached. Try submitting again.";
      error.hidden = false;
    } finally {
      fields.disabled = false;
      submit.textContent = "Verify evidence";
    }
  });

  byId("copy-flag").addEventListener("click", async () => {
    const flag = byId("flag");
    const status = byId("copy-status");
    try {
      await navigator.clipboard.writeText(flag.textContent);
      status.textContent = "Flag copied.";
    } catch {
      flag.parentElement.focus();
      const range = document.createRange();
      range.selectNodeContents(flag);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = "Flag selected. Use your device’s copy command.";
    }
  });
  byId("vault").hidden = false;
}

async function start() {
  const navPath = isHistory ? "/revisions" : page;
  const active = document.querySelector(`nav a[href="${navPath}"]`);
  active.setAttribute("aria-current", "page");
  document.title = `${active.textContent} | Keeper’s Archive`;
  if (isHistory) await showHistory();
  else if (page === "/vault") showVault();
  else await showArchive();
  await updatePreview();
}

start().catch(() => { byId("load-error").hidden = false; });
