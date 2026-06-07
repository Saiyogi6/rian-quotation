// ==========================================================================
// Rian Studioz - Live Preview Engine
// Syncs left side form controls to the right side document preview
// ==========================================================================

function initLivePreviewSync() {
    // Basic fields listeners
    const fieldsToSync = [
        { inputId: "quotation_number", previewId: "preview_quote_number" },
        { inputId: "quotation_date", previewId: "preview_quote_date", isDate: true },
        { inputId: "client_name", previewId: "preview_client_name" },
        { inputId: "client_email", previewId: "preview_client_email" },
        { inputId: "client_phone", previewId: "preview_client_phone" },
        { inputId: "client_address", previewId: "preview_client_address" },
        { inputId: "notes", previewId: "preview_notes" }
    ];

    fieldsToSync.forEach(field => {
        const input = document.getElementById(field.inputId);
        if (input) {
            input.addEventListener("input", () => syncField(field));
            syncField(field); // initial sync
        }
    });

    // We will listen to dynamic fields inputs inside the form
    document.addEventListener("input", (e) => {
        if (e.target && e.target.classList.contains("dynamic-meta-field")) {
            syncDynamicMetaFields();
        }
    });
}

function syncField(field) {
    const input = document.getElementById(field.inputId);
    const preview = document.getElementById(field.previewId);
    
    if (!input || !preview) return;
    
    if (field.isDate) {
        if (input.value) {
            const d = new Date(input.value);
            const options = { day: '2-digit', month: 'short', year: 'numeric' };
            preview.innerText = d.toLocaleDateString('en-GB', options);
        } else {
            preview.innerText = "";
        }
    } else {
        preview.innerText = input.value;
        // Handle showing/hiding parent if empty (e.g. notes)
        if (field.inputId === "notes") {
            const parent = preview.closest(".preview-notes-container");
            if (parent) {
                parent.style.display = input.value.trim() !== "" ? "block" : "none";
            }
        }
    }
}

function syncDynamicMetaFields() {
    const activeTypeCode = document.getElementById("quote_type_code").value;
    const container = document.getElementById("preview_dynamic_meta");
    if (!container) return;
    
    // Clear dynamic meta preview
    container.innerHTML = "";
    
    const activeGroup = document.getElementById(`fields_${activeTypeCode}`);
    if (!activeGroup) return;
    
    const inputs = activeGroup.querySelectorAll("input, textarea");
    if (inputs.length === 0) {
        container.style.display = "none";
        return;
    }
    
    let hasValues = false;
    let htmlContent = "";
    
    inputs.forEach(input => {
        const labelText = input.closest(".form-group").querySelector("label").innerText.replace("*", "").trim();
        const val = input.value;
        
        if (val.trim() !== "") {
            hasValues = true;
            htmlContent += `
                <div class="dynamic-meta-item">
                    <span>${labelText}</span>
                    <strong>${val}</strong>
                </div>
            `;
        }
    });
    
    if (hasValues) {
        container.innerHTML = htmlContent;
        container.style.display = "grid";
    } else {
        container.style.display = "none";
    }
}

function syncPreview() {
    // 1. Sync Dynamic Meta
    syncDynamicMetaFields();
    
    // 2. Sync Line Items Table
    const previewTbody = document.getElementById("preview_line_items_tbody");
    if (!previewTbody) return;
    
    previewTbody.innerHTML = "";
    
    document.querySelectorAll(".quote-section-block").forEach((sectionBlock) => {
        const title = sectionBlock.querySelector(".section-title-input").value;
        
        // Add Section Header Row in Table
        const headerRow = document.createElement("tr");
        headerRow.className = "section-row";
        headerRow.innerHTML = `
            <td colspan="4">${title || "Package Section"}</td>
        `;
        previewTbody.appendChild(headerRow);
        
        // Add Line Items
        sectionBlock.querySelectorAll(".line-item-row").forEach(row => {
            const desc = row.querySelector(".item-desc").value;
            const qty = parseFloat(row.querySelector(".item-qty").value) || 0;
            const price = parseFloat(row.querySelector(".item-price").value) || 0;
            const total = qty * price;
            
            if (desc.trim() !== "") {
                const itemRow = document.createElement("tr");
                itemRow.innerHTML = `
                    <td>${desc}</td>
                    <td class="qty-col">${qty}</td>
                    <td class="price-col">₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    <td class="total-col">₹${total.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                `;
                previewTbody.appendChild(itemRow);
            }
        });
    });
    
    // 3. Sync Addons in Table
    let hasAddons = false;
    document.querySelectorAll(".addon-row").forEach(row => {
        const desc = row.querySelector(".addon-desc").value;
        const price = parseFloat(row.querySelector(".addon-price").value) || 0;
        const select = row.querySelector(".addon-select");
        
        if (select && select.checked && desc.trim() !== "") {
            if (!hasAddons) {
                // Insert Addons Subheader
                const addonHeader = document.createElement("tr");
                addonHeader.className = "section-row";
                addonHeader.innerHTML = `<td colspan="4">Optional Add-ons Included</td>`;
                previewTbody.appendChild(addonHeader);
                hasAddons = true;
            }
            
            const addonRow = document.createElement("tr");
            addonRow.innerHTML = `
                <td>${desc} (Optional Add-on)</td>
                <td class="qty-col">1</td>
                <td class="price-col">₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td class="total-col">₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
            `;
            previewTbody.appendChild(addonRow);
        }
    });

    // 4. Sync Totals
    const subtotalText = document.getElementById("subtotal_display").innerText;
    const addonsText = document.getElementById("addons_total_display").innerText;
    const grandTotalText = document.getElementById("grand_total_display").innerText;
    
    document.getElementById("preview_subtotal").innerText = "₹" + subtotalText;
    
    const addonsRow = document.getElementById("preview_addons_row");
    if (addonsRow) {
        if (parseFloat(addonsText.replace(/,/g, '')) > 0) {
            addonsRow.style.display = "table-row";
            document.getElementById("preview_addons").innerText = "₹" + addonsText;
        } else {
            addonsRow.style.display = "none";
        }
    }
    
    document.getElementById("preview_grand_total").innerText = "₹" + grandTotalText;
    
    // 5. Sync Deliverables
    const delivContainer = document.getElementById("preview_deliverables_container");
    const delivSection = document.getElementById("preview_deliverables_section");
    if (delivContainer && delivSection) {
        delivContainer.innerHTML = "";
        const rows = document.querySelectorAll(".deliverable-row");
        if (rows.length === 0) {
            delivSection.style.display = "none";
        } else {
            let hasContent = false;
            rows.forEach(row => {
                const type = row.querySelector(".deliv-type").value;
                const desc = row.querySelector(".deliv-desc").value;
                const qty = parseInt(row.querySelector(".deliv-qty").value) || 0;
                
                if (desc.trim() !== "") {
                    hasContent = true;
                    let typeLabel = "Deliverable";
                    if (type === "photo") typeLabel = "Photos Output";
                    else if (type === "video") typeLabel = "Videos Output";
                    else if (type === "album") typeLabel = "Album Output";
                    else if (type === "turnaround") typeLabel = "Turnaround";
                    
                    const card = document.createElement("div");
                    card.className = "deliverable-card";
                    card.innerHTML = `
                        <div class="deliverable-card-title">${typeLabel} ${qty > 0 ? `(${qty})` : ''}</div>
                        <div>${desc}</div>
                    `;
                    delivContainer.appendChild(card);
                }
            });
            
            delivSection.style.display = hasContent ? "block" : "none";
        }
    }
    
    // 6. Sync Payment Splits
    const splitTbody = document.getElementById("preview_payment_splits_tbody");
    const splitSection = document.getElementById("preview_payment_splits_section");
    if (splitTbody && splitSection) {
        splitTbody.innerHTML = "";
        const rows = document.querySelectorAll(".payment-split-row");
        if (rows.length === 0) {
            splitSection.style.display = "none";
        } else {
            let hasContent = false;
            rows.forEach(row => {
                const stage = row.querySelector(".split-stage").value;
                const pct = parseFloat(row.querySelector(".split-percentage").value) || 0;
                const amt = parseFloat(row.querySelector(".split-amount").value) || 0;
                const due = row.querySelector(".split-due").value;
                
                if (stage.trim() !== "") {
                    hasContent = true;
                    const splitRow = document.createElement("tr");
                    splitRow.innerHTML = `
                        <td><strong>${stage}</strong> ${due ? `(${due})` : ''}</td>
                        <td style="text-align: right; width: 60px;">${pct > 0 ? `${pct}%` : ''}</td>
                        <td style="text-align: right; font-weight: 600; width: 120px;">₹${amt.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    `;
                    splitTbody.appendChild(splitRow);
                }
            });
            splitSection.style.display = hasContent ? "block" : "none";
        }
    }
}
