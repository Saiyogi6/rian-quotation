// ==========================================================================
// Rian Studioz - Main Editor JS Engine
// Handles dynamic form logic, calculations, repeating fields, and submissions
// ==========================================================================

const PRESETS_DATA = window.INJECTED_PRESETS_DATA || {
    wedding_reception: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Wedding & Reception Ceremony. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future. We eagerly await to surprise you with amazing pictures and videos.",
        sections: [
            {
                title: "Reception Coverage",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 20000, is_selected: true, group_name: "Reception", display_order: 0, item_category: "photo" },
                    { description: "Traditional Photography", qty: 1, unit_price: 10000, is_selected: true, group_name: "Reception", display_order: 1, item_category: "photo" },
                    { description: "Candid Videography (4K)", qty: 1, unit_price: 20000, is_selected: true, group_name: "Reception", display_order: 2, item_category: "video" },
                    { description: "Traditional Videography (4K)", qty: 1, unit_price: 15000, is_selected: true, group_name: "Reception", display_order: 3, item_category: "video" }
                ]
            },
            {
                title: "Wedding Coverage",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 20000, is_selected: true, group_name: "Wedding", display_order: 0, item_category: "photo" },
                    { description: "Traditional Photography", qty: 1, unit_price: 10000, is_selected: true, group_name: "Wedding", display_order: 1, item_category: "photo" },
                    { description: "Candid Videography (4K)", qty: 1, unit_price: 20000, is_selected: true, group_name: "Wedding", display_order: 2, item_category: "video" },
                    { description: "Traditional Videography (4K)", qty: 1, unit_price: 15000, is_selected: true, group_name: "Wedding", display_order: 3, item_category: "video" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "All Candid & Traditional Photos (Raw Images)", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "album", description: "2 Albums (250 Photos per Album, 40 Sheets / 80 Pages, Canvera Album with Mini Replica)", qty: 2, price: 0, is_complimentary: true, group_name: "Albums", display_order: 1 },
            { type: "video", description: "Full-Length Traditional Video", qty: 1, price: 0, is_complimentary: true, group_name: "Videos", display_order: 2 },
            { type: "turnaround", description: "Color Corrected Photos: Within 10 Days", qty: 1, price: 0, is_complimentary: true, group_name: "Delivery Timeline", display_order: 3 }
        ]
    },
    reception_only: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Reception. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future.",
        sections: [
            {
                title: "Reception Coverage",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 20000, is_selected: true, group_name: "Reception", display_order: 0, item_category: "photo" },
                    { description: "Traditional Photography", qty: 1, unit_price: 10000, is_selected: true, group_name: "Reception", display_order: 1, item_category: "photo" },
                    { description: "Candid Videography (4K)", qty: 1, unit_price: 20000, is_selected: true, group_name: "Reception", display_order: 2, item_category: "video" },
                    { description: "Traditional Videography (4K)", qty: 1, unit_price: 15000, is_selected: true, group_name: "Reception", display_order: 3, item_category: "video" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "Digital Photo Gallery (Raw & Edits)", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "album", description: "1 Premium Photobook Album", qty: 1, price: 0, is_complimentary: true, group_name: "Albums", display_order: 1 }
        ]
    },
    marriage_only: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Marriage Ceremony. Thank you for considering Rian Studioz for your big day.",
        sections: [
            {
                title: "Marriage Coverage",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 20000, is_selected: true, group_name: "Marriage Only", display_order: 0, item_category: "photo" },
                    { description: "Traditional Photography", qty: 1, unit_price: 10000, is_selected: true, group_name: "Marriage Only", display_order: 1, item_category: "photo" },
                    { description: "Traditional Videography (4K)", qty: 1, unit_price: 15000, is_selected: true, group_name: "Marriage Only", display_order: 2, item_category: "video" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "High-res Photo Delivery (Digital)", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "album", description: "1 Standard Wedding Album", qty: 1, price: 0, is_complimentary: true, group_name: "Albums", display_order: 1 }
        ]
    },
    muslim_wedding: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Nikah & Reception. Thank you for considering Rian Studioz for your big day.",
        sections: [
            {
                title: "Nikah Ceremony",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 20000, is_selected: true, group_name: "Nikah", display_order: 0, item_category: "photo" },
                    { description: "Traditional Photography", qty: 1, unit_price: 10000, is_selected: true, group_name: "Nikah", display_order: 1, item_category: "photo" },
                    { description: "Traditional Videography (4K)", qty: 1, unit_price: 15000, is_selected: true, group_name: "Nikah", display_order: 2, item_category: "video" }
                ]
            },
            {
                title: "Reception Coverage",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 20000, is_selected: true, group_name: "Reception", display_order: 0, item_category: "photo" },
                    { description: "Candid Videography", qty: 1, unit_price: 20000, is_selected: true, group_name: "Reception", display_order: 1, item_category: "video" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "All RAW + Edited Photos", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "album", description: "2 Premium Wedding Albums", qty: 2, price: 0, is_complimentary: true, group_name: "Albums", display_order: 1 }
        ]
    },
    retirement: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Retirement Function. Thank you for considering Rian Studioz for your big day.",
        sections: [
            {
                title: "Retirement Coverage",
                items: [
                    { description: "Traditional Photography", qty: 1, unit_price: 10000, is_selected: true, group_name: "Retirement", display_order: 0, item_category: "photo" },
                    { description: "Candid Photography", qty: 1, unit_price: 15000, is_selected: true, group_name: "Retirement", display_order: 1, item_category: "photo" },
                    { description: "Album (Magazine)", qty: 1, unit_price: 8000, is_selected: true, group_name: "Retirement", display_order: 2, item_category: "album" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "All Candid & Traditional Photos (Raw Images)", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "album", description: "1 Magazine Album (20 Sheets / 40 Pages)", qty: 1, price: 0, is_complimentary: true, group_name: "Album", display_order: 1 }
        ]
    },
    convocation_ad: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Convocation Ceremony & Ad Shoot. Thank you for considering Rian Studioz for your event.",
        sections: [
            {
                title: "Ad Shoot",
                items: [
                    { description: "Candid Photography", qty: 2, unit_price: 15000, is_selected: true, group_name: "Ad Shoot", display_order: 0, item_category: "photo" },
                    { description: "Candid Videography", qty: 2, unit_price: 15000, is_selected: true, group_name: "Ad Shoot", display_order: 1, item_category: "video" }
                ]
            },
            {
                title: "Convocation",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 15000, is_selected: true, group_name: "Convocation", display_order: 0, item_category: "photo" },
                    { description: "Candid Videography", qty: 1, unit_price: 15000, is_selected: true, group_name: "Convocation", display_order: 1, item_category: "video" },
                    { description: "Traditional Photography", qty: 2, unit_price: 10000, is_selected: true, group_name: "Convocation", display_order: 2, item_category: "photo" },
                    { description: "Traditional Videography", qty: 2, unit_price: 15000, is_selected: true, group_name: "Convocation", display_order: 3, item_category: "video" },
                    { description: "Drone", qty: 1, unit_price: 15000, is_selected: true, group_name: "Convocation", display_order: 4, item_category: "video" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "All Candid & Traditional Photos (Raw Images)", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "video", description: "Full-Length Traditional Video", qty: 1, price: 0, is_complimentary: true, group_name: "Videos", display_order: 1 }
        ]
    },
    election: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Election Campaign. Thank you for considering Rian Studioz for your campaign.",
        sections: [
            {
                title: "Election Campaign",
                items: [
                    { description: "Traditional Photography", qty: 10, unit_price: 12000, is_selected: true, group_name: "Campaign", display_order: 0, item_category: "photo" },
                    { description: "Traditional Videography", qty: 10, unit_price: 12000, is_selected: true, group_name: "Campaign", display_order: 1, item_category: "video" },
                    { description: "Drone", qty: 10, unit_price: 12000, is_selected: true, group_name: "Campaign", display_order: 2, item_category: "video" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "Daily Photo Feed (Raw Images)", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "video", description: "Campaign Highlight Videos", qty: 1, price: 0, is_complimentary: true, group_name: "Videos", display_order: 1 }
        ]
    },
    birthday: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Birthday Celebration. Thank you for considering Rian Studioz for your event.",
        sections: [
            {
                title: "Birthday Celebration",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 12000, is_selected: true, group_name: "Birthday", display_order: 0, item_category: "photo" },
                    { description: "Traditional Photography", qty: 1, unit_price: 8000, is_selected: true, group_name: "Birthday", display_order: 1, item_category: "photo" },
                    { description: "Traditional Videography", qty: 1, unit_price: 10000, is_selected: true, group_name: "Birthday", display_order: 2, item_category: "video" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "All photos in digital gallery", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "album", description: "1 Standard Birthday Album", qty: 1, price: 0, is_complimentary: true, group_name: "Albums", display_order: 1 }
        ]
    },
    baby_shower: {
        intro: "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Baby Shower. Thank you for considering Rian Studioz for your event.",
        sections: [
            {
                title: "Baby Shower",
                items: [
                    { description: "Candid Photography", qty: 1, unit_price: 15000, is_selected: true, group_name: "Baby Shower", display_order: 0, item_category: "photo" },
                    { description: "Traditional Photography", qty: 1, unit_price: 8000, is_selected: true, group_name: "Baby Shower", display_order: 1, item_category: "photo" },
                    { description: "Cinematic Teaser", qty: 1, unit_price: 12000, is_selected: true, group_name: "Baby Shower", display_order: 2, item_category: "video" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "Digital Photo Gallery", qty: 1, price: 0, is_complimentary: true, group_name: "Photos", display_order: 0 },
            { type: "album", description: "1 Premium photobook", qty: 1, price: 0, is_complimentary: true, group_name: "Albums", display_order: 1 }
        ]
    },
    custom: {
        intro: "Hey! A big hello from Rian Studioz. Thank you for considering Rian Studioz for your creative needs. Below is the custom tailored quotation and list of deliverables based on our discussion.",
        sections: [
            {
                title: "Custom Services",
                items: [
                    { description: "Standard Photography", qty: 1, unit_price: 10000, is_selected: true, group_name: "Custom", display_order: 0, item_category: "photo" }
                ]
            }
        ],
        deliverables: [
            { type: "photo", description: "Digital Deliverable Package", qty: 1, price: 0, is_complimentary: true, group_name: "Digital", display_order: 0 }
        ]
    }
};

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

    // 5. Setup intro content sync
    const introTextarea = document.getElementById("intro_content");
    if (introTextarea) {
        introTextarea.addEventListener("input", syncPreview);
    }
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
    const isEdit = document.getElementById("is_edit").value === "true";
    
    cards.forEach(card => {
        card.addEventListener("click", () => {
            const selectedType = card.dataset.type;
            
            cards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            typeInput.value = selectedType;
            
            // Toggle dynamic field sections
            toggleDynamicFields(selectedType);
            
            // Load preset default fields
            if (!isEdit || confirm("Switching presets will reset current sections, line items, and deliverables to their defaults. Proceed?")) {
                loadPreset(selectedType);
            }
        });
    });
    
    // Initialize active fields on page load
    if (typeInput) {
        toggleDynamicFields(typeInput.value);
        // If it is a new quote and sections are empty or it's fresh, load default preset
        const sectionsContainer = document.getElementById("sections_container");
        const isFresh = sectionsContainer && sectionsContainer.children.length === 1 && 
                        sectionsContainer.querySelector(".item-desc") && 
                        sectionsContainer.querySelector(".item-desc").value.trim() === "";
        if (!isEdit && isFresh) {
            loadPreset(typeInput.value);
        }
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

function loadPreset(typeCode) {
    const data = PRESETS_DATA.presets ? PRESETS_DATA.presets[typeCode] : PRESETS_DATA[typeCode];
    if (!data) return;
    
    // 1. Load Intro Note
    const introTextarea = document.getElementById("intro_content");
    if (introTextarea) {
        introTextarea.value = data.intro;
    }
    
    // 2. Clear and Render Sections
    const sectionsContainer = document.getElementById("sections_container");
    if (sectionsContainer) {
        sectionsContainer.innerHTML = "";
        data.sections.forEach((sec, idx) => {
            sectionsContainer.insertAdjacentHTML("beforeend", renderSectionHTML(idx, sec.title, sec.items));
        });
    }
    
    // 3. Clear and Render Deliverables
    const deliverablesTbody = document.getElementById("deliverables_tbody");
    if (deliverablesTbody) {
        deliverablesTbody.innerHTML = "";
        data.deliverables.forEach((deliv, idx) => {
            deliverablesTbody.insertAdjacentHTML("beforeend", renderDeliverableRowHTML(deliv, idx));
        });
    }
    
    // Populate dropdowns
    populateAllDescSelects();
    
    recalculateAll();
}

function renderSectionHTML(index, title, items = []) {
    let tbodyHtml = "";
    if (items.length === 0) {
        items.push({ description: "", qty: 1, unit_price: 0, is_selected: true, group_name: title, display_order: 0, item_category: "photo" });
    }
    
    items.forEach((item, itemIdx) => {
        tbodyHtml += `
            <tr class="line-item-row">
                <td style="text-align: center; vertical-align: middle;">
                    <input type="checkbox" class="item-select" ${item.is_selected ? 'checked' : ''} onchange="recalculateAll()">
                </td>
                <td>
                    <div class="desc-container" style="display: flex; flex-direction: column; gap: 5px;">
                        <select class="form-control item-desc-select" onchange="onItemDescSelectChange(this)">
                            <!-- Options populated dynamically -->
                        </select>
                        <input type="text" class="form-control item-desc" placeholder="Service description" value="${item.description}" required oninput="syncPreview()">
                    </div>
                </td>
                <td>
                    <input type="number" class="form-control item-qty" value="${item.qty}" step="1" min="1" style="text-align: center;" oninput="onItemMathChange(this)">
                </td>
                <td>
                    <input type="number" class="form-control item-price" value="${item.unit_price}" step="100" min="0" style="text-align: right;" oninput="onItemMathChange(this)">
                </td>
                <td class="item-total-cell" style="text-align: right; padding-top: 18px; font-weight: 600;">${(item.qty * item.unit_price).toFixed(2)}</td>
                <td>
                    <button type="button" class="action-icon text-danger" onclick="removeLineItem(this)"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    });

    return `
        <div class="quote-section-block form-section" data-index="${index}">
            <div class="section-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <h3 class="section-title-label">${title || `Grouped Package Section ${index + 1}`}</h3>
                <div>
                    <button type="button" class="btn btn-danger btn-sm" onclick="removeSection(this, event)">Remove Section</button>
                    <i class="fas fa-chevron-down" style="margin-left: 10px;"></i>
                </div>
            </div>
            <div class="section-content">
                <div class="form-group">
                    <label>Section Title (e.g. Wedding, Reception, Ad Shoot)</label>
                    <input type="text" class="form-control section-title-input" value="${title}" oninput="updateSectionLabel(this)">
                </div>
                
                <table class="line-items-editor-table">
                    <thead>
                        <tr>
                            <th style="width: 40px; text-align: center;">Active</th>
                            <th>Service Description</th>
                            <th class="qty-col">Qty</th>
                            <th class="price-col">Unit Price (₹)</th>
                            <th class="total-col" style="text-align: right;">Total (₹)</th>
                            <th style="width: 50px;"></th>
                        </tr>
                    </thead>
                    <tbody class="line-items-tbody">
                        ${tbodyHtml}
                    </tbody>
                </table>
                <button type="button" class="btn btn-secondary btn-sm" onclick="addLineItem(this)">+ Add Service Item</button>
            </div>
        </div>
    `;
}

function renderDeliverableRowHTML(item = {}, index = 0) {
    const type = item.type || "photo";
    const description = item.description || "";
    const qty = item.qty !== undefined ? item.qty : 1;
    const price = item.price !== undefined ? item.price : 0;
    const is_selected = item.is_selected !== undefined ? item.is_selected : true;

    return `
        <tr class="deliverable-row">
            <td style="text-align: center; vertical-align: middle;">
                <input type="checkbox" class="deliv-select" ${is_selected ? 'checked' : ''} onchange="recalculateAll()">
            </td>
            <td>
                <select class="form-control deliv-type" onchange="syncPreview()">
                    <option value="photo" ${type === 'photo' ? 'selected' : ''}>Photos</option>
                    <option value="video" ${type === 'video' ? 'selected' : ''}>Videos / Teaser</option>
                    <option value="album" ${type === 'album' ? 'selected' : ''}>Album / Print</option>
                    <option value="turnaround" ${type === 'turnaround' ? 'selected' : ''}>Turnaround Time</option>
                    <option value="other" ${type === 'other' ? 'selected' : ''}>Other</option>
                </select>
            </td>
            <td>
                <input type="text" class="form-control deliv-desc" value="${description}" required oninput="syncPreview()">
            </td>
            <td>
                <input type="number" class="form-control deliv-qty" value="${qty}" step="1" min="0" style="text-align: center;" oninput="syncPreview()">
            </td>
            <td>
                <input type="number" class="form-control deliv-price" value="${price}" step="100" min="0" style="text-align: right;" oninput="syncPreview()">
            </td>
            <td>
                <button type="button" class="action-icon text-danger" onclick="removeDeliverable(this)"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `;
}

// --- SECTIONS & LINE ITEMS ACTIONS ---
function addSection() {
    const container = document.getElementById("sections_container");
    const sectionIndex = container.children.length;
    container.insertAdjacentHTML("beforeend", renderSectionHTML(sectionIndex, "New Section"));
    recalculateAll();
}

function removeSection(button, event) {
    event.stopPropagation();
    if (confirm("Are you sure you want to remove this entire package section?")) {
        button.closest(".quote-section-block").remove();
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
    tbody.insertAdjacentHTML("beforeend", `
        <tr class="line-item-row">
            <td style="text-align: center; vertical-align: middle;">
                <input type="checkbox" class="item-select" checked onchange="recalculateAll()">
            </td>
            <td>
                <div class="desc-container" style="display: flex; flex-direction: column; gap: 5px;">
                    <select class="form-control item-desc-select" onchange="onItemDescSelectChange(this)">
                        <!-- Options populated dynamically -->
                    </select>
                    <input type="text" class="form-control item-desc" placeholder="Service description" required oninput="syncPreview()">
                </div>
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
    `);
    const newRow = tbody.lastElementChild;
    const select = newRow.querySelector(".item-desc-select");
    populateServiceDescSelect(select, "");
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

// --- DELIVERABLES ACTIONS ---
function addDeliverable() {
    const tbody = document.getElementById("deliverables_tbody");
    const index = tbody.children.length;
    tbody.insertAdjacentHTML("beforeend", renderDeliverableRowHTML({}, index));
    syncPreview();
}

function removeDeliverable(button) {
    button.closest("tr").remove();
    recalculateAll();
}

function onDelivPriceChange(input) {
    recalculateAll();
}

function onDelivComplimentaryChange(checkbox) {
    const row = checkbox.closest("tr");
    const priceInput = row.querySelector(".deliv-price");
    if (checkbox.checked) {
        priceInput.value = 0;
        priceInput.disabled = true;
    } else {
        priceInput.disabled = false;
    }
    recalculateAll();
}

// --- PAYMENT SPLITS ACTIONS ---
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

// --- ADD-ONS ACTIONS ---
function addAddOnRow() {
    const tbody = document.getElementById("addons_tbody");
    const rowHtml = `
        <tr class="addon-row">
            <td>
                <div class="desc-container" style="display: flex; flex-direction: column; gap: 5px;">
                    <select class="form-control addon-desc-select" onchange="onAddonDescSelectChange(this)">
                        <!-- Options populated dynamically -->
                    </select>
                    <input type="text" class="form-control addon-desc" placeholder="Add-on service" required oninput="syncPreview()">
                </div>
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
    const newRow = tbody.lastElementChild;
    const select = newRow.querySelector(".addon-desc-select");
    populateAddonDescSelect(select, "");
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
    
    // 1. Calculate section totals from active/selected line items
    document.querySelectorAll(".quote-section-block").forEach(section => {
        section.querySelectorAll(".line-item-row").forEach(row => {
            const isSelected = row.querySelector(".item-select") ? row.querySelector(".item-select").checked : true;
            const qty = parseFloat(row.querySelector(".item-qty").value) || 0;
            const price = parseFloat(row.querySelector(".item-price").value) || 0;
            const total = qty * price;
            row.querySelector(".item-total-cell").innerText = total.toFixed(2);
            if (isSelected) {
                subtotal += total;
            }
        });
    });

    // 2. Add deliverable prices if active/selected and not complimentary
    let deliverablesTotal = 0;
    document.querySelectorAll(".deliverable-row").forEach(row => {
        const isSelected = row.querySelector(".deliv-select") ? row.querySelector(".deliv-select").checked : true;
        const price = parseFloat(row.querySelector(".deliv-price").value) || 0;
        const isComplimentary = (price === 0);
        const qty = parseFloat(row.querySelector(".deliv-qty").value) || 1;
        if (isSelected && !isComplimentary) {
            deliverablesTotal += qty * price;
        }
    });
    
    subtotal += deliverablesTotal;
    
    // 3. Add-ons calculations
    let addonsTotal = 0;
    document.querySelectorAll(".addon-row").forEach(row => {
        const select = row.querySelector(".addon-select");
        const price = parseFloat(row.querySelector(".addon-price").value) || 0;
        if (select && select.checked) {
            addonsTotal += price;
        }
    });
    
    const totalBeforeDiscount = subtotal + addonsTotal;
    
    // 4. Calculate discount
    const discountType = document.getElementById("discount_type") ? document.getElementById("discount_type").value : "none";
    const discountVal = parseFloat(document.getElementById("discount_value") ? document.getElementById("discount_value").value : 0) || 0;
    let discountAmount = 0;
    if (discountType === "fixed") {
        discountAmount = discountVal;
    } else if (discountType === "percentage") {
        discountAmount = totalBeforeDiscount * (discountVal / 100);
    }
    
    const grandTotal = Math.max(0, totalBeforeDiscount - discountAmount);
    
    // 5. Update displays
    const subtotalDisplay = document.getElementById("subtotal_display");
    const addonsDisplay = document.getElementById("addons_total_display");
    const discountDisplay = document.getElementById("discount_display");
    const grandTotalDisplay = document.getElementById("grand_total_display");
    
    if (subtotalDisplay) subtotalDisplay.innerText = subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (addonsDisplay) addonsDisplay.innerText = addonsTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (discountDisplay) discountDisplay.innerText = discountAmount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (grandTotalDisplay) grandTotalDisplay.innerText = grandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    
    // 6. Update splits based on new total
    redistributePaymentSplits(grandTotal);
    
    // 7. Update right side preview
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
    const intro_content = document.getElementById("intro_content") ? document.getElementById("intro_content").value : "";
    const discount_type = document.getElementById("discount_type") ? document.getElementById("discount_type").value : "none";
    const discount_value = parseFloat(document.getElementById("discount_value") ? document.getElementById("discount_value").value : 0) || 0;
    
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
        
        sectionBlock.querySelectorAll(".line-item-row").forEach((row, i_idx) => {
            const description = row.querySelector(".item-desc").value;
            const qty = parseFloat(row.querySelector(".item-qty").value) || 1;
            const unit_price = parseFloat(row.querySelector(".item-price").value) || 0;
            const is_selected = row.querySelector(".item-select") ? row.querySelector(".item-select").checked : true;
            const group_name = row.querySelector(".item-group-name") ? row.querySelector(".item-group-name").value : title;
            const display_order = parseInt(row.querySelector(".item-display-order") ? row.querySelector(".item-display-order").value : i_idx) || 0;
            const item_category = row.querySelector(".item-cat") ? row.querySelector(".item-cat").value : "other";
            
            if (description.trim() !== "") {
                line_items.push({ description, qty, unit_price, is_selected, group_name, display_order, item_category });
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
    document.querySelectorAll(".deliverable-row").forEach((row, d_idx) => {
        const type = row.querySelector(".deliv-type").value;
        const description = row.querySelector(".deliv-desc").value;
        const qty = parseInt(row.querySelector(".deliv-qty").value) || 0;
        const is_selected = row.querySelector(".deliv-select") ? row.querySelector(".deliv-select").checked : true;
        const price = parseFloat(row.querySelector(".deliv-price") ? row.querySelector(".deliv-price").value : 0) || 0;
        const is_complimentary = (price === 0);
        const group_name = type;
        const display_order = d_idx;
        
        if (description.trim() !== "") {
            deliverables.push({ type, description, qty, is_selected, price, is_complimentary, group_name, display_order, item_category: type });
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
        discount_type,
        discount_value,
        intro_content,
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

// --- DYNAMIC PRESETS DROPDOWN LOGIC ---

function populateServiceDescSelect(selectElement, selectedValue = "") {
    const typeCode = document.getElementById("quote_type_code")?.value || "wedding_reception";
    const preset = PRESETS_DATA.presets ? PRESETS_DATA.presets[typeCode] : PRESETS_DATA[typeCode];
    
    // Clear select
    selectElement.innerHTML = "";
    
    // Add default select option
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "-- Select Predefined Service --";
    selectElement.appendChild(defaultOption);
    
    let isPredefinedMatched = false;
    
    if (preset && preset.sections) {
        // Collect all predefined items in this preset
        const predefinedItems = [];
        preset.sections.forEach(sec => {
            sec.items.forEach(item => {
                if (!predefinedItems.find(i => i.description === item.description)) {
                    predefinedItems.push(item);
                }
            });
        });
        
        predefinedItems.forEach(item => {
            const opt = document.createElement("option");
            opt.value = item.description;
            opt.textContent = `${item.description} (₹${item.unit_price})`;
            opt.dataset.price = item.unit_price;
            if (item.description === selectedValue) {
                opt.selected = true;
                isPredefinedMatched = true;
            }
            selectElement.appendChild(opt);
        });
    }
    
    // Add Custom option
    const customOption = document.createElement("option");
    customOption.value = "__custom__";
    customOption.textContent = "Custom Service (Type manually)...";
    if (selectedValue && !isPredefinedMatched) {
        customOption.selected = true;
    }
    selectElement.appendChild(customOption);
    
    // Show/hide the text input
    const textInput = selectElement.parentElement.querySelector(".item-desc");
    if (selectElement.value === "__custom__" || selectElement.value === "") {
        textInput.style.display = "block";
    } else {
        textInput.style.display = "none";
    }
}

function onItemDescSelectChange(selectElement) {
    const textInput = selectElement.parentElement.querySelector(".item-desc");
    const priceInput = selectElement.closest(".line-item-row").querySelector(".item-price");
    
    if (selectElement.value === "__custom__") {
        textInput.style.display = "block";
        textInput.value = "";
        textInput.focus();
    } else if (selectElement.value === "") {
        textInput.style.display = "block";
        textInput.value = "";
    } else {
        textInput.style.display = "none";
        textInput.value = selectElement.value;
        
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        const price = selectedOption.dataset.price;
        if (price !== undefined) {
            priceInput.value = price;
        }
    }
    onItemMathChange(priceInput);
}

function populateAllDescSelects() {
    document.querySelectorAll(".line-item-row").forEach(row => {
        const select = row.querySelector(".item-desc-select");
        const input = row.querySelector(".item-desc");
        if (select && input) {
            populateServiceDescSelect(select, input.value);
        }
    });
}

function populateAddonDescSelect(selectElement, selectedValue = "") {
    const addons = PRESETS_DATA.addons || [
        { "description": "1 Extra Traditional Photography", "price": 10000 },
        { "description": "1 Extra Traditional Videography(4K)", "price": 15000 },
        { "description": "1 Extra Candid Photography", "price": 15000 },
        { "description": "1 Extra Candid Videography", "price": 15000 },
        { "description": "Drone", "price": 12000 },
        { "description": "1 Extra Album", "price": 20000 },
        { "description": "LED Wall (6 x 8)", "price": 13000 },
        { "description": "LED TV(50\u2019Inches)", "price": 5000 },
        { "description": "Spot Mixing", "price": 10000 },
        { "description": "PhotoBooth", "price": 25000 },
        { "description": "360o Spinny", "price": 15000 },
        { "description": "Youtube Live Streaming 1080p", "price": 10000 }
    ];
    
    selectElement.innerHTML = "";
    
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "-- Select Predefined Add-on --";
    selectElement.appendChild(defaultOption);
    
    let isPredefinedMatched = false;
    addons.forEach(item => {
        const opt = document.createElement("option");
        opt.value = item.description;
        opt.textContent = `${item.description} (₹${item.price})`;
        opt.dataset.price = item.price;
        if (item.description === selectedValue) {
            opt.selected = true;
            isPredefinedMatched = true;
        }
        selectElement.appendChild(opt);
    });
    
    const customOption = document.createElement("option");
    customOption.value = "__custom__";
    customOption.textContent = "Custom Add-on (Type manually)...";
    if (selectedValue && !isPredefinedMatched) {
        customOption.selected = true;
    }
    selectElement.appendChild(customOption);
    
    const textInput = selectElement.parentElement.querySelector(".addon-desc");
    if (selectElement.value === "__custom__" || selectElement.value === "") {
        textInput.style.display = "block";
    } else {
        textInput.style.display = "none";
    }
}

function onAddonDescSelectChange(selectElement) {
    const textInput = selectElement.parentElement.querySelector(".addon-desc");
    const priceInput = selectElement.closest(".addon-row").querySelector(".addon-price");
    
    if (selectElement.value === "__custom__") {
        textInput.style.display = "block";
        textInput.value = "";
        textInput.focus();
    } else if (selectElement.value === "") {
        textInput.style.display = "block";
        textInput.value = "";
    } else {
        textInput.style.display = "none";
        textInput.value = selectElement.value;
        
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        const price = selectedOption.dataset.price;
        if (price !== undefined) {
            priceInput.value = price;
        }
    }
    onAddonMathChange(priceInput);
}

function populateAllAddonDescSelects() {
    document.querySelectorAll(".addon-row").forEach(row => {
        const select = row.querySelector(".addon-desc-select");
        const input = row.querySelector(".addon-desc");
        if (select && input) {
            populateAddonDescSelect(select, input.value);
        }
    });
}

