// ==========================================================================
// Rian Studioz - Main Editor JS Engine
// Handles dynamic form logic, calculations, repeating fields, and submissions
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Collapsible Sections
    initCollapsibleSections();
    
    // 2. Initialize Quote Type Selection
    initQuoteTypeSelector();
    
    // 3. Initialize Live Preview Sync (if preview elements are present)
    if (document.querySelector(".quote-canvas")) {
        initLivePreviewSync();
    }
    
    // 4. Perform Initial Calculations
    recalculateAll();
});

/* ==========================================
   Collapsible Sections
   ========================================== */
function initCollapsibleSections() {
    document.querySelectorAll(".section-header").forEach(header => {
        header.addEventListener("click", () => {
            const section = header.parentElement;
            section.classList.toggle("collapsed");
        });
    });
}

/* ==========================================
   Quote Type Selector Flow
   ========================================== */
function initQuoteTypeSelector() {
    const cards = document.querySelectorAll(".preset-card");
    const typeInput = document.getElementById("quote_type_code");
    
    cards.forEach(card => {
        card.addEventListener("click", () => {
            const selectedType = card.dataset.type;
            
            // If it's an edit view, warning that switching type resets fields might be useful, 
            // but for smooth UX we can just switch.
            cards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            typeInput.value = selectedType;
            
            // Toggle dynamic field sections
            toggleDynamicFields(selectedType);
            
            // Trigger live preview refresh
            recalculateAll();
        });
    });
    
    // Initialize active fields on page load
    if (typeInput) {
        toggleDynamicFields(typeInput.value);
    }
}

function toggleDynamicFields(typeCode) {
    // Hide all dynamic meta inputs
    document.querySelectorAll(".dynamic-meta-input-group").forEach(group => {
        group.style.display = "none";
        group.querySelectorAll("input, textarea").forEach(el => el.disabled = true);
    });
    
    // Show active ones
    const activeGroup = document.getElementById(`fields_${typeCode}`);
    if (activeGroup) {
        activeGroup.style.display = "block";
        activeGroup.querySelectorAll("input, textarea").forEach(el => el.disabled = false);
    }
}

/* ==========================================
   Dynamic Repeating Fields & Editors
   ========================================== */

// --- SECTIONS & LINE ITEMS ---
function addSection() {
    const container = document.getElementById("sections_container");
    const sectionIndex = container.children.length;
    
    const sectionHtml = `
        <div class="quote-section-block form-section" data-index="${sectionIndex}">
            <div class="section-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <h3 class="section-title-label">Grouped Package Section ${sectionIndex + 1}</h3>
                <div>
                    <button type="button" class="btn btn-danger btn-sm" onclick="removeSection(this, event)">Remove Section</button>
                    <i class="fas fa-chevron-down" style="margin-left: 10px;"></i>
                </div>
            </div>
            <div class="section-content">
                <div class="form-group">
                    <label>Section Title (e.g. Wedding, Reception, Ad Shoot)</label>
                    <input type="text" class="form-control section-title-input" value="New Section" oninput="updateSectionLabel(this)">
                </div>
                
                <table class="line-items-editor-table">
                    <thead>
                        <tr>
                            <th>Service Description</th>
                            <th class="qty-col">Qty</th>
                            <th class="price-col">Unit Price (₹)</th>
                            <th class="total-col" style="text-align: right;">Total (₹)</th>
                            <th style="width: 50px;"></th>
                        </tr>
                    </thead>
                    <tbody class="line-items-tbody">
                        <tr class="line-item-row">
                            <td>
                                <input type="text" class="form-control item-desc" placeholder="Service description" required oninput="syncPreview()">
                            </td>
                            <td>
                                <input type="number" class="form-control item-qty" value="1" step="1" min="1" style="text-align: center;" oninput="onItemMathChange(this)">
                            </td>
                            <td>
                                <input type="number" class="form-control item-price" value="0" step="100" min="0" style="text-align: right;" oninput="onItemMathChange(this)">
                            </td>
                            <td class="item-total-cell" style="text-align: right; padding-top: 18px; font-weight: 600;">0.00</td>
                            <td>
                                <button type="button" class="action-icon text-danger" onclick="removeLineItem(this)"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <button type="button" class="btn btn-secondary btn-sm" onclick="addLineItem(this)">+ Add Service Item</button>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML("beforeend", sectionHtml);
    recalculateAll();
}

function removeSection(button, event) {
    event.stopPropagation(); // prevent collapsing trigger
    if (confirm("Are you sure you want to remove this entire package section and all its service items?")) {
        button.closest(".quote-section-block").remove();
        // Reindex section identifiers
        reindexSections();
        recalculateAll();
    }
}

function reindexSections() {
    const container = document.getElementById("sections_container");
    Array.from(container.children).forEach((section, idx) => {
        section.dataset.index = idx;
        const titleLabel = section.querySelector(".section-title-label");
        const titleInput = section.querySelector(".section-title-input");
        if (titleInput && titleInput.value.trim() !== "") {
            titleLabel.innerText = titleInput.value;
        } else {
            titleLabel.innerText = `Grouped Package Section ${idx + 1}`;
        }
    });
}

function updateSectionLabel(input) {
    const sectionBlock = input.closest(".quote-section-block");
    const label = sectionBlock.querySelector(".section-title-label");
    label.innerText = input.value.trim() !== "" ? input.value : `Grouped Package Section ${parseInt(sectionBlock.dataset.index) + 1}`;
    syncPreview();
}

function addLineItem(button) {
    const tbody = button.closest(".section-content").querySelector(".line-items-tbody");
    const rowHtml = `
        <tr class="line-item-row">
            <td>
                <input type="text" class="form-control item-desc" placeholder="Service description" required oninput="syncPreview()">
            </td>
            <td>
                <input type="number" class="form-control item-qty" value="1" step="1" min="1" style="text-align: center;" oninput="onItemMathChange(this)">
            </td>
            <td>
                <input type="number" class="form-control item-price" value="0" step="100" min="0" style="text-align: right;" oninput="onItemMathChange(this)">
            </td>
            <td class="item-total-cell" style="text-align: right; padding-top: 18px; font-weight: 600;">0.00</td>
            <td>
                <button type="button" class="action-icon text-danger" onclick="removeLineItem(this)"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `;
    tbody.insertAdjacentHTML("beforeend", rowHtml);
    recalculateAll();
}

function removeLineItem(button) {
    const tbody = button.closest(".line-items-tbody");
    if (tbody.children.length > 1) {
        button.closest("tr").remove();
        recalculateAll();
    } else {
        alert("Each section must contain at least one service line item.");
    }
}

function onItemMathChange(input) {
    const row = input.closest("tr");
    const qty = parseFloat(row.querySelector(".item-qty").value) || 0;
    const price = parseFloat(row.querySelector(".item-price").value) || 0;
    const total = qty * price;
    
    row.querySelector(".item-total-cell").innerText = total.toFixed(2);
    recalculateAll();
}

// --- DELIVERABLES ---
function addDeliverable() {
    const tbody = document.getElementById("deliverables_tbody");
    const rowHtml = `
        <tr class="deliverable-row">
            <td>
                <select class="form-control deliv-type" onchange="syncPreview()">
                    <option value="photo">Photos</option>
                    <option value="video">Videos / Teaser</option>
                    <option value="album">Album / Print</option>
                    <option value="turnaround">Turnaround Time</option>
                    <option value="other">Other</option>
                </select>
            </td>
            <td>
                <input type="text" class="form-control deliv-desc" placeholder="Deliverable details" required oninput="syncPreview()">
            </td>
            <td>
                <input type="number" class="form-control deliv-qty" value="1" step="1" min="0" style="text-align: center;" oninput="syncPreview()">
            </td>
            <td>
                <button type="button" class="action-icon text-danger" onclick="removeDeliverable(this)"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `;
    tbody.insertAdjacentHTML("beforeend", rowHtml);
    syncPreview();
}

function removeDeliverable(button) {
    button.closest("tr").remove();
    syncPreview();
}

// --- PAYMENT SPLITS ---
function addPaymentSplit() {
    const tbody = document.getElementById("payment_splits_tbody");
    const rowHtml = `
        <tr class="payment-split-row">
            <td>
                <input type="text" class="form-control split-stage" placeholder="e.g. Booking Advance" required oninput="syncPreview()">
            </td>
            <td>
                <input type="number" class="form-control split-percentage" value="0" step="5" min="0" max="100" style="text-align: center;" oninput="onSplitPercentChange(this)">
            </td>
            <td>
                <input type="number" class="form-control split-amount" value="0" step="500" min="0" style="text-align: right;" oninput="onSplitAmountChange(this)">
            </td>
            <td>
                <input type="text" class="form-control split-due" placeholder="e.g. On Booking" oninput="syncPreview()">
            </td>
            <td>
                <button type="button" class="action-icon text-danger" onclick="removePaymentSplit(this)"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `;
    tbody.insertAdjacentHTML("beforeend", rowHtml);
    syncPreview();
}

function removePaymentSplit(button) {
    button.closest("tr").remove();
    syncPreview();
}

function onSplitPercentChange(input) {
    const grandTotal = parseFloat(document.getElementById("grand_total_display").innerText.replace(/,/g, '')) || 0;
    const row = input.closest("tr");
    const pct = parseFloat(input.value) || 0;
    const amount = (grandTotal * pct) / 100;
    row.querySelector(".split-amount").value = amount.toFixed(2);
    syncPreview();
}

function onSplitAmountChange(input) {
    const grandTotal = parseFloat(document.getElementById("grand_total_display").innerText.replace(/,/g, '')) || 0;
    const row = input.closest("tr");
    const amount = parseFloat(input.value) || 0;
    const pct = grandTotal > 0 ? (amount / grandTotal) * 100 : 0;
    row.querySelector(".split-percentage").value = pct.toFixed(0);
    syncPreview();
}

function redistributePaymentSplits(grandTotal) {
    const rows = document.querySelectorAll(".payment-split-row");
    if (rows.length === 0) return;
    
    // If we have splits, try to match amounts to percentages
    rows.forEach(row => {
        const pctInput = row.querySelector(".split-percentage");
        const amtInput = row.querySelector(".split-amount");
        const pct = parseFloat(pctInput.value) || 0;
        
        if (pct > 0) {
            const amount = (grandTotal * pct) / 100;
            amtInput.value = amount.toFixed(2);
        }
    });
}

// --- ADD-ONS ---
function addAddOnRow() {
    const tbody = document.getElementById("addons_tbody");
    const rowHtml = `
        <tr class="addon-row">
            <td>
                <input type="text" class="form-control addon-desc" placeholder="Add-on service" required oninput="syncPreview()">
            </td>
            <td>
                <input type="number" class="form-control addon-price" value="0" step="500" min="0" style="text-align: right;" oninput="onAddonMathChange(this)">
            </td>
            <td style="text-align: center; padding-top: 12px;">
                <input type="checkbox" class="addon-select" checked onchange="recalculateAll()">
            </td>
            <td>
                <button type="button" class="action-icon text-danger" onclick="removeAddOn(this)"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `;
    tbody.insertAdjacentHTML("beforeend", rowHtml);
    recalculateAll();
}

function removeAddOn(button) {
    button.closest("tr").remove();
    recalculateAll();
}

function onAddonMathChange(input) {
    recalculateAll();
}

/* ==========================================
   Calculation Core
   ========================================== */
function recalculateAll() {
    let subtotal = 0;
    
    // 1. Calculate section totals
    document.querySelectorAll(".quote-section-block").forEach(section => {
        let sectionTotal = 0;
        section.querySelectorAll(".line-item-row").forEach(row => {
            const qty = parseFloat(row.querySelector(".item-qty").value) || 0;
            const price = parseFloat(row.querySelector(".item-price").value) || 0;
            const total = qty * price;
            row.querySelector(".item-total-cell").innerText = total.toFixed(2);
            sectionTotal += total;
        });
        subtotal += sectionTotal;
    });
    
    // 2. Add-ons calculations
    let addonsTotal = 0;
    document.querySelectorAll(".addon-row").forEach(row => {
        const select = row.querySelector(".addon-select");
        const price = parseFloat(row.querySelector(".addon-price").value) || 0;
        if (select && select.checked) {
            addonsTotal += price;
        }
    });
    
    const grandTotal = subtotal + addonsTotal;
    
    // 3. Update displays
    const subtotalDisplay = document.getElementById("subtotal_display");
    const addonsDisplay = document.getElementById("addons_total_display");
    const grandTotalDisplay = document.getElementById("grand_total_display");
    
    if (subtotalDisplay) subtotalDisplay.innerText = subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (addonsDisplay) addonsDisplay.innerText = addonsTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (grandTotalDisplay) grandTotalDisplay.innerText = grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    
    // 4. Update splits based on new total
    redistributePaymentSplits(grandTotal);
    
    // 5. Update right side preview
    syncPreview();
}

/* ==========================================
   Form Submission (AJAX JSON)
   ========================================== */
async function saveQuote(statusVal = "draft") {
    // 1. Client Details & Core fields
    const quotation_number = document.getElementById("quotation_number").value;
    const quotation_date = document.getElementById("quotation_date").value;
    const brand_id = parseInt(document.getElementById("brand_id").value);
    const template_id = parseInt(document.getElementById("template_id").value);
    const quote_type_code = document.getElementById("quote_type_code").value;
    const notes = document.getElementById("notes").value;
    
    const client_name = document.getElementById("client_name").value;
    const client_email = document.getElementById("client_email").value;
    const client_phone = document.getElementById("client_phone").value;
    const client_address = document.getElementById("client_address").value;
    
    if (!client_name || !quotation_date) {
        alert("Please fill in Client Name and Quotation Date.");
        return;
    }
    
    // 2. Gather Dynamic fields based on active quote type
    const details = {};
    const activeGroup = document.getElementById(`fields_${quote_type_code}`);
    if (activeGroup) {
        activeGroup.querySelectorAll("input, textarea").forEach(el => {
            const key = el.name;
            const val = el.value;
            details[key] = val;
        });
    }
    
    // 3. Gather Sections and line items
    const sections = [];
    document.querySelectorAll(".quote-section-block").forEach(sectionBlock => {
        const title = sectionBlock.querySelector(".section-title-input").value;
        const line_items = [];
        
        sectionBlock.querySelectorAll(".line-item-row").forEach(row => {
            const description = row.querySelector(".item-desc").value;
            const qty = parseFloat(row.querySelector(".item-qty").value) || 1;
            const unit_price = parseFloat(row.querySelector(".item-price").value) || 0;
            
            if (description.trim() !== "") {
                line_items.push({ description, qty, unit_price });
            }
        });
        
        if (title.trim() !== "" && line_items.length > 0) {
            sections.push({ title, line_items });
        }
    });
    
    if (sections.length === 0) {
        alert("Please add at least one package section with line items.");
        return;
    }
    
    // 4. Gather Deliverables
    const deliverables = [];
    document.querySelectorAll(".deliverable-row").forEach(row => {
        const type = row.querySelector(".deliv-type").value;
        const description = row.querySelector(".deliv-desc").value;
        const qty = parseInt(row.querySelector(".deliv-qty").value) || 0;
        
        if (description.trim() !== "") {
            deliverables.push({ type, description, qty });
        }
    });
    
    // 5. Gather Payment Splits
    const payment_splits = [];
    let splitSum = 0;
    document.querySelectorAll(".payment-split-row").forEach(row => {
        const stage_name = row.querySelector(".split-stage").value;
        const percentage = parseFloat(row.querySelector(".split-percentage").value) || null;
        const amount = parseFloat(row.querySelector(".split-amount").value) || 0;
        const due_date = row.querySelector(".split-due").value;
        
        if (stage_name.trim() !== "") {
            payment_splits.push({ stage_name, percentage, amount, due_date });
            splitSum += amount;
        }
    });
    
    // Validate split sum matches grand total
    const grandTotal = parseFloat(document.getElementById("grand_total_display").innerText.replace(/,/g, '')) || 0;
    if (payment_splits.length > 0 && Math.abs(splitSum - grandTotal) > 1) {
        if (!confirm(`Warning: The sum of payment milestone amounts (₹${splitSum.toFixed(2)}) does not match the Grand Total (₹${grandTotal.toFixed(2)}). Do you want to proceed anyway?`)) {
            return;
        }
    }
    
    // 6. Gather Add-ons
    const add_ons = [];
    document.querySelectorAll(".addon-row").forEach(row => {
        const description = row.querySelector(".addon-desc").value;
        const price = parseFloat(row.querySelector(".addon-price").value) || 0;
        const is_selected = row.querySelector(".addon-select").checked;
        
        if (description.trim() !== "") {
            add_ons.push({ description, price, is_selected });
        }
    });
    
    // 7. Compile full payload
    const payload = {
        quotation_number,
        quotation_date,
        status: statusVal,
        notes,
        brand_id,
        quote_type_code,
        template_id,
        client_name,
        client_email,
        client_phone,
        client_address,
        details,
        sections,
        deliverables,
        payment_splits,
        add_ons
    };
    
    // Submit via AJAX
    const isEdit = document.getElementById("is_edit").value === "true";
    const quoteId = document.getElementById("quote_id") ? document.getElementById("quote_id").value : null;
    
    const url = isEdit ? `/api/quotes/${quoteId}` : `/api/quotes`;
    const method = isEdit ? "PUT" : "POST";
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to save quotation");
        }
        
        const savedQuote = await response.json();
        
        // Export PDF and dispatch webhook automatically
        await exportPdf(savedQuote.id);
        
        alert("Quotation saved and PDF generated successfully!");
        window.location.href = "/";
    } catch (e) {
        alert("Error: " + e.message);
    }
}

async function exportPdf(quoteId) {
    try {
        const response = await fetch(`/api/quotes/${quoteId}/export-pdf`, {
            method: "POST"
        });
        if (!response.ok) {
            console.error("Failed to generate PDF automatically");
        }
    } catch (e) {
        console.error("Error auto-generating PDF: ", e);
    }
}
