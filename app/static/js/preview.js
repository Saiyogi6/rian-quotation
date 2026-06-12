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
        if (e.target && (e.target.classList.contains("dynamic-meta-field") || e.target.id === "intro_content")) {
            syncPreview();
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
        if (input.id === "intro_content") return; // skip intro note in dynamic specs grid
        
        const labelEl = input.closest(".form-group").querySelector("label");
        const labelText = labelEl ? labelEl.innerText.replace("*", "").trim() : "";
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
    
    // 2. Sync Intro Note / Greeting
    const introInput = document.getElementById("intro_content");
    const introContainer = document.getElementById("preview_intro_content_container");
    const introSpan = document.getElementById("preview_intro_content");
    if (introInput && introContainer && introSpan) {
        const text = introInput.value.trim();
        if (text) {
            introSpan.innerText = text;
            introContainer.style.display = "block";
        } else {
            introContainer.style.display = "none";
        }
    }
    
    // 3. Sync Line Items Table
    const previewTbody = document.getElementById("preview_line_items_tbody");
    if (!previewTbody) return;
    
    previewTbody.innerHTML = "";
    
    document.querySelectorAll(".quote-section-block").forEach((sectionBlock) => {
        const title = sectionBlock.querySelector(".section-title-input").value;
        
        // Find, filter, and sort selected items in this section
        const rows = Array.from(sectionBlock.querySelectorAll(".line-item-row"));
        const activeRows = rows.filter(row => {
            const desc = row.querySelector(".item-desc").value.trim();
            const isSelected = row.querySelector(".item-select") ? row.querySelector(".item-select").checked : true;
            return desc !== "" && isSelected;
        });
        
        if (activeRows.length === 0) return; // skip empty section in preview
        
        // Sort active items by display_order
        activeRows.sort((a, b) => {
            const orderA = parseInt(a.querySelector(".item-display-order")?.value || 0);
            const orderB = parseInt(b.querySelector(".item-display-order")?.value || 0);
            return orderA - orderB;
        });
        
        // Add Section Header Row in Table
        const headerRow = document.createElement("tr");
        headerRow.className = "section-row";
        headerRow.innerHTML = `
            <td colspan="4">${title || "Package Section"}</td>
        `;
        previewTbody.appendChild(headerRow);
        
        // Add Line Items
        activeRows.forEach(row => {
            const desc = row.querySelector(".item-desc").value;
            const qty = parseFloat(row.querySelector(".item-qty").value) || 0;
            const price = parseFloat(row.querySelector(".item-price").value) || 0;
            const total = qty * price;
            
            const itemRow = document.createElement("tr");
            itemRow.innerHTML = `
                <td>${desc}</td>
                <td class="qty-col">${qty}</td>
                <td class="price-col">₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td class="total-col">₹${total.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
            `;
            previewTbody.appendChild(itemRow);
        });
    });
    
    // 4. Sync Addons in Table
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

    // 5. Sync Totals
    const subtotalText = document.getElementById("subtotal_display").innerText;
    const addonsText = document.getElementById("addons_total_display").innerText;
    const discountText = document.getElementById("discount_display").innerText;
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
    
    const discountRow = document.getElementById("preview_discount_row");
    if (discountRow) {
        if (parseFloat(discountText.replace(/,/g, '')) > 0) {
            discountRow.style.display = "table-row";
            document.getElementById("preview_discount").innerText = "-₹" + discountText;
        } else {
            discountRow.style.display = "none";
        }
    }
    
    document.getElementById("preview_grand_total").innerText = "₹" + grandTotalText;
    
    // 6. Sync Grouped & Sorted Deliverables
    const delivContainer = document.getElementById("preview_deliverables_container");
    const delivSection = document.getElementById("preview_deliverables_section");
    if (delivContainer && delivSection) {
        delivContainer.innerHTML = "";
        const rows = Array.from(document.querySelectorAll(".deliverable-row"));
        
        // Filter active
        const activeDelivs = rows.map(row => {
            const isSelected = row.querySelector(".deliv-select") ? row.querySelector(".deliv-select").checked : true;
            const type = row.querySelector(".deliv-type").value;
            const desc = row.querySelector(".deliv-desc").value.trim();
            const qty = parseInt(row.querySelector(".deliv-qty").value) || 0;
            const price = parseFloat(row.querySelector(".deliv-price").value) || 0;
            const isComplimentary = (price === 0);
            
            return { isSelected, type, desc, qty, price, isComplimentary };
        }).filter(d => d.isSelected && d.desc !== "");

        if (activeDelivs.length === 0) {
            delivSection.style.display = "none";
        } else {
            // Render directly in a grid instead of grouping by groupName
            let cardsContainerHtml = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 15px;">`;
            
            activeDelivs.forEach(d => {
                let typeLabel = "Deliverable";
                if (d.type === "photo") typeLabel = "Photos Output";
                else if (d.type === "video") typeLabel = "Videos Output";
                else if (d.type === "album") typeLabel = "Album Output";
                else if (d.type === "turnaround") typeLabel = "Turnaround";
                
                let badgeHtml = "";
                if (d.isComplimentary) {
                    badgeHtml = `<div style="font-size: 11px; font-weight: 600; color: #10b981; margin-top: 5px; text-transform: uppercase; letter-spacing: 0.5px;">Complimentary</div>`;
                } else if (d.price > 0) {
                    badgeHtml = `<div style="font-size: 11px; font-weight: 600; color: var(--quote-gold, #c5a880); margin-top: 5px;">₹${d.price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>`;
                }
                
                cardsContainerHtml += `
                    <div class="deliverable-card" style="margin-bottom: 0; page-break-inside: avoid;">
                        <div class="deliverable-card-title">${typeLabel} ${d.qty > 0 ? `(${d.qty})` : ''}</div>
                        <div style="font-size: 12px; color: var(--quote-text-light, #6b7280);">${d.desc}</div>
                        ${badgeHtml}
                    </div>
                `;
            });
            
            cardsContainerHtml += `</div>`;
            delivContainer.innerHTML = cardsContainerHtml;
            delivSection.style.display = "block";
        }
    }
    
    // 7. Sync Payment Splits
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
                        <td style="text-align: right; width: 60px;">${pct > 0 ? `${pct.toFixed(0)}%` : ''}</td>
                        <td style="text-align: right; font-weight: 600; width: 120px;">₹${amt.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    `;
                    splitTbody.appendChild(splitRow);
                }
            });
            splitSection.style.display = hasContent ? "block" : "none";
        }
    }
}
