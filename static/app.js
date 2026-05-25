const ingestionMessage = document.getElementById("ingestion-message");
const resultsBox = document.getElementById("search-results");
const statsBox = document.getElementById("stats-box");
const sourceFilter = document.getElementById("source-filter");
const sourceLabels = {
    openalex: "OpenAlex",
    europe_pmc: "Europe PMC",
    upload: "Upload TXT",
};

async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);
    const isJson = response.headers.get("content-type")?.includes("application/json");
    const payload = isJson ? await response.json() : null;

    if (!response.ok) {
        const detail = payload?.detail || "Request failed";
        throw new Error(detail);
    }

    return payload;
}

function showMessage(text, type = "success") {
    ingestionMessage.textContent = text;
    ingestionMessage.className = `message ${type}`;
}

function renderEmptyState(target, text) {
    target.innerHTML = `<div class="empty-state">${text}</div>`;
}

function formatSourceName(sourceName) {
    return sourceLabels[sourceName] || sourceName;
}

function formatSimilarity(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return `similarity = ${Number(value).toFixed(4)}`;
}

async function refreshOverview() {
    const stats = await apiRequest("/api/stats");

    statsBox.innerHTML = `
        <div class="stat-card"><strong>${stats.total_documents}</strong><p>documents</p></div>
        <div class="stat-card"><strong>${stats.total_chunks}</strong><p>chunks</p></div>
        <div class="stat-card"><strong>${Object.keys(stats.sources).length}</strong><p>sources</p></div>
    `;
}

async function loadSources() {
    const data = await apiRequest("/api/sources");
    const options = [`<option value="">All sources</option>`].concat(
        data.sources.map(
            (source) => `<option value="${source.name}">${formatSourceName(source.name)}</option>`
        )
    );
    sourceFilter.innerHTML = options.join("");
}

async function handleSourceImport(event, sourceName) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload = {
        limit: Number(formData.get("limit")),
    };

    try {
        showMessage("Import in progress...", "success");
        const result = await apiRequest(`/api/ingestion/${sourceName}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        showMessage(result.message, "success");
        await refreshOverview();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function handleUpload(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    try {
        showMessage("Uploading TXT...", "success");
        const result = await apiRequest("/api/ingestion/upload", {
            method: "POST",
            body: formData,
        });
        showMessage(result.message, "success");
        event.currentTarget.reset();
        await refreshOverview();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function handleSearch(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload = {
        query: formData.get("query"),
        source: formData.get("source") || null,
    };

    try {
        const result = await apiRequest("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!result.results.length) {
            renderEmptyState(resultsBox, "No matching chunks were found.");
            return;
        }

        resultsBox.innerHTML = result.results
            .map(
                (item) => `
                    <article class="result-card">
                        <h3>${item.title}</h3>
                        <div class="meta">
                            <span class="pill">${formatSourceName(item.source)}</span>
                            ${item.similarity !== null ? `<span class="pill">${formatSimilarity(item.similarity)}</span>` : ""}
                        </div>
                        <p>${item.snippet}</p>
                        ${item.source_url ? `<a href="${item.source_url}" target="_blank" rel="noreferrer">Open source</a>` : ""}
                    </article>
                `
            )
            .join("");
    } catch (error) {
        renderEmptyState(resultsBox, error.message);
    }
}

document.getElementById("openalex-form").addEventListener("submit", (event) => {
    handleSourceImport(event, "openalex");
});
document.getElementById("europepmc-form").addEventListener("submit", (event) => {
    handleSourceImport(event, "europe_pmc");
});
document.getElementById("upload-form").addEventListener("submit", handleUpload);
document.getElementById("search-form").addEventListener("submit", handleSearch);

async function init() {
    try {
        await loadSources();
        await refreshOverview();
        renderEmptyState(resultsBox, "No results yet.");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

init();
