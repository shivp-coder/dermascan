document.addEventListener("DOMContentLoaded", () => {
    const uploadArea = document.getElementById("uploadArea");
    const fileInput = document.getElementById("fileInput");
    const previewContainer = document.getElementById("previewContainer");
    const imagePreview = document.getElementById("imagePreview");
    const clearBtn = document.getElementById("clearBtn");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const uploadSection = document.getElementById("uploadSection");
    const loadingSection = document.getElementById("loadingSection");
    const resultsSection = document.getElementById("resultsSection");
    const newAnalysisBtn = document.getElementById("newAnalysisBtn");

    let selectedFile = null;

    // Upload area click
    uploadArea.addEventListener("click", () => fileInput.click());

    // Drag and drop
    uploadArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadArea.classList.add("drag-over");
    });

    uploadArea.addEventListener("dragleave", () => {
        uploadArea.classList.remove("drag-over");
    });

    uploadArea.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadArea.classList.remove("drag-over");
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // File input change
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    });

    // Clear button
    clearBtn.addEventListener("click", () => {
        selectedFile = null;
        fileInput.value = "";
        previewContainer.hidden = true;
        uploadArea.hidden = false;
        analyzeBtn.disabled = true;
    });

    // Analyze button
    analyzeBtn.addEventListener("click", () => {
        if (!selectedFile) return;
        performAnalysis();
    });

    // New analysis button
    newAnalysisBtn.addEventListener("click", () => {
        selectedFile = null;
        fileInput.value = "";
        previewContainer.hidden = true;
        uploadArea.hidden = false;
        analyzeBtn.disabled = true;
        resultsSection.hidden = true;
        uploadSection.hidden = false;
    });

    function handleFile(file) {
        const validTypes = [
            "image/png", "image/jpeg", "image/bmp", "image/tiff",
        ];
        if (!validTypes.includes(file.type)) {
            alert("Please select a valid image file (PNG, JPG, BMP, or TIFF).");
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            alert("File is too large. Maximum size is 10MB.");
            return;
        }

        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            previewContainer.hidden = false;
            uploadArea.hidden = true;
            analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    async function performAnalysis() {
        uploadSection.hidden = true;
        loadingSection.hidden = false;
        resultsSection.hidden = true;

        const formData = new FormData();
        formData.append("image", selectedFile);

        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Analysis failed");
            }

            displayResults(data);
        } catch (err) {
            alert("Error: " + err.message);
            uploadSection.hidden = false;
        } finally {
            loadingSection.hidden = true;
        }
    }

    function displayResults(data) {
        // Severity
        const severityCard = document.getElementById("severityCard");
        severityCard.className = "severity-card severity-" + data.severity_score;
        document.getElementById("severityScore").textContent =
            data.severity_score + " / 5";
        document.getElementById("severityLabel").textContent =
            data.severity_label;

        // Conditions
        const condList = document.getElementById("conditionsList");
        condList.innerHTML = "";
        data.top_conditions.forEach((cond, i) => {
            const card = document.createElement("div");
            card.className = "condition-card";
            card.innerHTML = `
                <div>
                    <div class="condition-name">${i + 1}. ${escapeHtml(cond.condition)}</div>
                    <div class="condition-desc">${escapeHtml(cond.description)}</div>
                </div>
                <div class="condition-confidence">${cond.confidence_percent}%</div>
            `;
            condList.appendChild(card);
        });

        // ABCDE
        const abcdeContent = document.getElementById("abcdeContent");
        abcdeContent.innerHTML = "";
        const abcdeLabels = {
            asymmetry: "A — Asymmetry",
            border: "B — Border",
            color: "C — Color",
            diameter: "D — Diameter",
            evolution: "E — Evolution",
        };
        Object.entries(data.abcde_assessment).forEach(([key, value]) => {
            const item = document.createElement("div");
            item.className = "abcde-item";
            const displayValue = value.replace(/_/g, " ");
            let statusClass = "status-normal";
            if (value === "concerning") statusClass = "status-concerning";
            else if (value === "mild") statusClass = "status-mild";
            item.innerHTML = `
                <span class="abcde-label">${abcdeLabels[key] || key}</span>
                <span class="${statusClass}">${escapeHtml(displayValue)}</span>
            `;
            abcdeContent.appendChild(item);
        });

        // Next steps
        const nextSteps = document.getElementById("nextStepsList");
        nextSteps.innerHTML = "";
        data.next_steps.forEach((step) => {
            const li = document.createElement("li");
            li.textContent = step;
            nextSteps.appendChild(li);
        });

        // Doctor recommendation
        document.getElementById("doctorRec").textContent =
            data.doctor_recommendation;

        // Disclaimer
        document.getElementById("disclaimer").textContent = data.disclaimer;

        resultsSection.hidden = false;
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
});
