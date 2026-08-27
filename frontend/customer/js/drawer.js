// ================================================================
// COMPREHENSIVE TERMS & CONDITIONS CATALOG
// ================================================================
const CUSTOMER_TERMS = [
    "1. Account Authenticity: Customers must provide accurate, verified information during signup and checkout.",
    "2. Studio Commission Agreements: Custom creative orders are initiated strictly upon payment confirmation or COD selection.",
    "3. UPI Transaction Integrity: Direct UPI transfers must correspond exactly to the invoice amount on bank verification.",
    "4. Order Modification Window: Physical items may only be amended prior to vendor courier dispatch.",
    "5. Dispatch Tracking: Registered tracking identifiers are issued upon handover to logistics couriers.",
    "6. Delivery Inspection: Goods must be inspected upon delivery; damages must be reported within 48 hours with unboxing media.",
    "7. Intellectual Property Rights: Bespoke artworks and photo shoots remain the intellectual asset of the respective creator until full settlement.",
    "8. Personal Non-Commercial License: Purchased prints are for personal display unless commercial licensing is explicitly invoiced.",
    "9. Service Booking Time Slots: Scheduled studio sessions require 24-hour advance notice for rescheduling.",
    "10. Cancellation Policies: Personalized or custom-dimensioned art pieces are non-refundable once production commences.",
    "11. Return Authorization: Standard non-customized goods may be returned within 7 days in original condition.",
    "12. Promo Code Usability: Promotional vouchers cannot be combined with secondary concurrent platform coupons.",
    "13. Address Precision: Delivery failures arising from incorrect customer addresses require re-dispatch surcharges.",
    "14. Cash on Delivery Obligation: Refusal of COD orders without valid reason may result in temporary account restriction.",
    "15. Digital Proofing: Client approvals on digital mockup drafts are considered binding prior to final print execution.",
    "16. Color Variations: Slight chromatic variances between screen displays and physical resin/ink mediums are inherent to artisanal craft.",
    "17. Data Privacy: Contact credentials are exclusively utilized for delivery execution and critical order dispatches.",
    "18. Platform Etiquette: Abusive behavior towards creators, vendors, or courier executives will terminate platform privileges.",
    "19. Force Majeure: Delays due to natural weather disruptions or logistical strikes are addressed with best-effort dispatch schedules.",
    "20. Security Credentials: Users are responsible for safeguarding login passwords and OTP verification tokens.",
    "21. Age Requirement: Account holders must be at least 18 years of age or possess guardian supervision for monetary transactions.",
    "22. Dispute Escalation: Unresolved transaction disputes will undergo administrative mediation via FrameStudio Support.",
    "23. Wishlist Exclusivity: Saving items in wishlists does not lock inventory against concurrent live purchases.",
    "24. Feedback Guidelines: Product reviews must represent genuine purchase experiences without defamatory remarks.",
    "25. Regulatory Compliance: All purchases comply with Indian e-commerce consumer guidelines and IT Act provisions."
];

const VENDOR_TERMS = [
    "1. Verification & Onboarding: Vendors must maintain verified identity and valid studio credentials for administrative approval.",
    "2. Listing Authenticity: All catalog entries must showcase original works, accurate materials, dimensions, and authentic photos.",
    "3. Fulfillments & SLA: Orders must be processed and dispatched within the declared production lead time.",
    "4. Direct Bank Verification: Vendors must independently audit UPI QR credits on their banking records before confirming orders.",
    "5. Courier & Tracking Assignment: Live tracking IDs and courier partner details must be submitted promptly upon dispatch.",
    "6. Packaging Standards: Fragile artworks (glass, resin, ceramic) must employ industry-standard shock-absorbent cushioning.",
    "7. Price Transparency: Listed prices must incorporate applicable taxes without concealed surcharges at checkout.",
    "8. Stock Accuracy: Real-time inventory and booking slot availability must be maintained to prevent overbooking.",
    "9. Quality Assurance: Physical deliverables must match descriptions and client-approved mockups without defect.",
    "10. Service Booking Punctuality: Studio and photography sessions must adhere strictly to the scheduled booking timeframe.",
    "11. Copyright Warranties: Vendors warrant that all artworks, designs, and media do not infringe third-party intellectual property.",
    "12. Customer Data Confidentiality: Client addresses and contact numbers may not be exported or used for external solicitation.",
    "13. Dispute Co-operation: Vendors must respond to customer escalation inquiries within 24 business hours.",
    "14. Return Handling: Damaged or misdescribed goods must be replaced or refunded in coordination with platform moderation.",
    "15. Platform Conduct: Vendors shall not redirect transactions outside FrameStudio to evade platform safeguards.",
    "16. Account Integrity: Vendor credentials and dashboard administrative rights are non-transferable.",
    "17. Catalog Moderation: FrameStudio reserves the right to unlist offerings that violate quality or safety benchmarks.",
    "18. Promotional Alignment: Discounts applied via platform campaigns must be honored across all accepted orders.",
    "19. Review Integrity: Vendors may not manipulate ratings or author fraudulent testimonials.",
    "20. Suspension & Revocation: Repeated dispatch failures or unverified listings may lead to immediate vendor suspension.",
    "21. Direct Client Communication: Professionalism must be maintained across all direct client correspondences.",
    "22. Statutory Tax Compliance: Vendors are responsible for managing their internal business taxation and invoices.",
    "23. Termination Notice: Vendors desiring to deactivate their studio catalog must fulfill all pending ledger orders first."
];

// ================================================================
// DRAWER & MODAL INJECTION ENGINE (LOCKED DARK THEME)
// ================================================================
const DrawerEngine = {
    init(role = 'customer') {
        // Clear any leftover theme setting and lock to dark
        localStorage.removeItem('fs_theme');
        document.documentElement.removeAttribute('data-theme');

        this.injectDrawerHtml(role);
        this.injectModals();
        this.loadProfileData();
    },

    loadProfileData() {
        const user = Auth.getUser();
        if (!user) return;

        const avatarImg = document.getElementById('drawerUserAvatar');
        const nameEl = document.getElementById('drawerUserName');
        const roleEl = document.getElementById('drawerUserRole');

        if (avatarImg) avatarImg.src = user.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150';
        if (nameEl) nameEl.innerText = user.full_name || user.email.split('@')[0];
        if (roleEl) roleEl.innerText = (user.role || 'customer').toUpperCase();
    },

    injectDrawerHtml(role) {
        const isVendorOrAdmin = role === 'admin' || role === 'vendor' || role === 'seller';
        const drawerHtml = `
            <div class="offcanvas offcanvas-start offcanvas-luxury" tabindex="-1" id="fsHamburgerDrawer" aria-labelledby="fsHamburgerLabel">
                <div class="offcanvas-header border-bottom border-secondary pb-3">
                    <h5 class="offcanvas-title fw-bold brand-font text-white" id="fsHamburgerLabel">
                        Frame<span style="color:#00f2fe">Studio</span>
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas"></button>
                </div>

                <div class="offcanvas-body d-flex flex-column justify-content-between px-3 py-4">
                    <div class="d-flex flex-column gap-3">
                        <!-- Profile Card Snapshot -->
                        <div class="drawer-profile-box d-flex align-items-center gap-3">
                            <img id="drawerUserAvatar" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150" class="drawer-avatar-preview" alt="Avatar">
                            <div>
                                <h6 class="fw-bold text-white mb-1" id="drawerUserName">User Profile</h6>
                                <span class="badge ${isVendorOrAdmin ? 'bg-primary' : 'bg-secondary'} small text-uppercase" id="drawerUserRole">CUSTOMER</span>
                            </div>
                        </div>

                        <!-- Menu Options -->
                        <nav class="d-flex flex-column gap-1 mt-2">
                            <a href="javascript:void(0)" onclick="DrawerEngine.openProfileModal()" class="drawer-menu-item">
                                <i class="fas fa-user-pen text-info"></i> Edit My Profile
                            </a>

                            ${!isVendorOrAdmin ? `
                                <a href="cart.html" class="drawer-menu-item">
                                    <i class="fas fa-bag-shopping text-warning"></i> My Cart / Wishlist
                                </a>
                                <a href="orders.html" class="drawer-menu-item">
                                    <i class="fas fa-box-open text-primary"></i> Track Orders
                                </a>
                            ` : `
                                <a href="../admin/dashboard.html" class="drawer-menu-item">
                                    <i class="fas fa-gauge-high text-primary"></i> Studio Dashboard
                                </a>
                            `}

                            <a href="javascript:void(0)" onclick="DrawerEngine.openPasswordModal()" class="drawer-menu-item">
                                <i class="fas fa-key text-success"></i> Change Password
                            </a>

                            <a href="javascript:void(0)" onclick="DrawerEngine.openTermsModal('${isVendorOrAdmin ? 'vendor' : 'customer'}')" class="drawer-menu-item">
                                <i class="fas fa-file-contract text-danger"></i> Terms & Conditions
                            </a>

                            <a href="javascript:void(0)" onclick="DrawerEngine.openFaqModal()" class="drawer-menu-item">
                                <i class="fas fa-circle-question text-info"></i> Help & FAQs
                            </a>
                        </nav>
                    </div>

                    <!-- Bottom Logout Button -->
                    <div class="pt-4 border-top border-secondary">
                        <button onclick="Auth.logout()" class="btn btn-outline-danger w-100 py-2 d-flex align-items-center justify-content-center gap-2 fw-bold">
                            <i class="fas fa-sign-out-alt"></i> Sign Out
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', drawerHtml);
    },

    injectModals() {
        const modalsHtml = `
            <!-- EDIT PROFILE MODAL -->
            <div class="modal fade" id="modalEditProfile" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content auth-card text-white border-0" style="background:#0d1322; border: 1px solid rgba(0,242,254,0.3) !important;">
                        <div class="modal-header border-0 pb-0">
                            <h5 class="modal-title fw-bold"><i class="fas fa-user-circle text-info me-2"></i>My Profile Details</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-4">
                            <form id="profileUpdateForm">
                                <div class="text-center mb-4">
                                    <img id="editAvatarPreview" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150" class="drawer-avatar-preview mb-2" alt="Avatar">
                                    <div>
                                        <label for="avatarFileInput" class="btn btn-sm btn-luxury-outline mt-1">
                                            <i class="fas fa-camera me-1"></i> Upload Picture from Device
                                        </label>
                                        <input type="file" id="avatarFileInput" class="d-none" accept="image/*" onchange="DrawerEngine.handleAvatarFile(event)">
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label class="form-label auth-label">Full Name</label>
                                    <input type="text" id="profFullName" class="form-control auth-input" required>
                                </div>

                                <div id="vendorAgencyField" class="mb-3 d-none">
                                    <label class="form-label auth-label">Company / Agency Name</label>
                                    <input type="text" id="profAgencyName" class="form-control auth-input" placeholder="e.g. Apex Visuals & Frames">
                                </div>

                                <div class="row g-3 mb-4">
                                    <div class="col-6">
                                        <label class="form-label auth-label">Age</label>
                                        <input type="number" id="profAge" class="form-control auth-input" placeholder="e.g. 24" min="12" max="100">
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label auth-label">Gender</label>
                                        <select id="profGender" class="form-select auth-input">
                                            <option value="">Select</option>
                                            <option value="Female">Female</option>
                                            <option value="Male">Male</option>
                                            <option value="Non-Binary">Non-Binary</option>
                                            <option value="Prefer not to say">Prefer not to say</option>
                                        </select>
                                    </div>
                                </div>

                                <button type="submit" class="btn btn-luxury w-100 py-3 fw-bold">
                                    <i class="fas fa-save me-1"></i> Save Profile Details
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CHANGE PASSWORD MODAL -->
            <div class="modal fade" id="modalChangePassword" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered" style="max-width: 420px;">
                    <div class="modal-content auth-card text-white border-0" style="background:#0d1322; border: 1px solid rgba(255,255,255,0.2) !important;">
                        <div class="modal-header border-0 pb-0">
                            <h5 class="modal-title fw-bold"><i class="fas fa-key text-warning me-2"></i>Change Password</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-4">
                            <form id="passwordResetDrawerForm">
                                <p class="text-light small mb-3">To update your password, request a secure 6-digit OTP code sent to your registered email.</p>
                                <button type="button" onclick="DrawerEngine.sendPasswordOtp()" id="btnSendDrawerOtp" class="btn btn-luxury-outline w-100 mb-3 py-2">
                                    <i class="fas fa-paper-plane me-1"></i> Send Verification OTP
                                </button>
                                
                                <div class="mb-3">
                                    <label class="form-label auth-label">6-Digit Code</label>
                                    <input type="text" id="drawerOtpInput" class="form-control auth-input" placeholder="123456" maxlength="6" required>
                                </div>

                                <div class="mb-4">
                                    <label class="form-label auth-label">New Password</label>
                                    <input type="password" id="drawerNewPassInput" class="form-control auth-input" placeholder="••••••••" minlength="6" required>
                                </div>

                                <button type="submit" class="btn btn-luxury w-100 py-3 fw-bold">Update Password</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TERMS & CONDITIONS MODAL -->
            <div class="modal fade" id="modalTermsCatalog" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
                    <div class="modal-content auth-card text-white border-0" style="background:#0d1322; border: 1px solid rgba(255,255,255,0.2) !important;">
                        <div class="modal-header border-bottom border-secondary">
                            <h5 class="modal-title fw-bold" id="termsModalTitle"><i class="fas fa-file-contract text-info me-2"></i>Terms & Conditions</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-4" id="termsListBody"></div>
                    </div>
                </div>
            </div>

            <!-- HELP & FAQ MODAL -->
            <div class="modal fade" id="modalFaqSheet" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content auth-card text-white border-0" style="background:#0d1322; border: 1px solid rgba(255,255,255,0.2) !important;">
                        <div class="modal-header border-bottom border-secondary">
                            <h5 class="modal-title fw-bold"><i class="fas fa-circle-question text-info me-2"></i>Help Center & Frequently Asked Questions</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-4">
                            <div class="accordion accordion-flush" id="faqAccordion">
                                <div class="accordion-item bg-transparent text-white border-bottom border-secondary">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed bg-transparent text-info fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                                            How do payments and UPI transfers work?
                                        </button>
                                    </h2>
                                    <div id="faq1" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                        <div class="accordion-body text-light small">
                                            You can pay instantly using Google Pay, PhonePe, or Paytm via our verified custom QR code. The vendor confirms the credit on their bank ledger before dispatching your package.
                                        </div>
                                    </div>
                                </div>
                                <div class="accordion-item bg-transparent text-white border-bottom border-secondary">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed bg-transparent text-info fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                                            How are custom art pieces delivered safely?
                                        </button>
                                    </h2>
                                    <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                        <div class="accordion-body text-light small">
                                            Vendors package fragile resin and glass artworks using multi-layer bubble shielding and wooden corner braces, assigned with tracked courier partners (Blue Dart, Delhivery).
                                        </div>
                                    </div>
                                </div>
                                <div class="accordion-item bg-transparent text-white border-bottom border-secondary">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed bg-transparent text-info fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">
                                            How do creators and agencies register?
                                        </button>
                                    </h2>
                                    <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                        <div class="accordion-body text-light small">
                                            Sellers select "Vendor / Agency" upon sign up. The account enters pending moderation until the platform Administrator reviews and activates the listing dashboard.
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalsHtml);

        // Bind Profile Form Submission
        document.getElementById('profileUpdateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                full_name: document.getElementById('profFullName').value.trim(),
                agency_name: document.getElementById('profAgencyName').value.trim(),
                age: document.getElementById('profAge').value,
                gender: document.getElementById('profGender').value,
                avatar_url: document.getElementById('editAvatarPreview').src
            };

            try {
                const res = await fetch(`${API_BASE}/profile/update`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${Auth.getToken()}`
                    },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok && data.success) {
                    Auth.setUser(data.user, Auth.getToken());
                    DrawerEngine.loadProfileData();
                    bootstrap.Modal.getInstance(document.getElementById('modalEditProfile')).hide();
                    alert('Profile updated successfully!');
                } else {
                    alert(data.message || 'Error updating profile');
                }
            } catch (err) {
                alert('Server error updating profile.');
            }
        });

        // Bind Password Reset Submission
        document.getElementById('passwordResetDrawerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const user = Auth.getUser();
            const otp = document.getElementById('drawerOtpInput').value.trim();
            const new_password = document.getElementById('drawerNewPassInput').value;

            try {
                const res = await fetch(`${API_BASE}/auth/reset-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: user.email, otp, new_password })
                });
                const data = await res.json();
                if (res.ok && data.success) {
                    alert('Password changed successfully!');
                    bootstrap.Modal.getInstance(document.getElementById('modalChangePassword')).hide();
                } else {
                    alert(data.message || 'Failed to update password');
                }
            } catch (err) {
                alert('Server error resetting password.');
            }
        });
    },

    handleAvatarFile(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(evt) {
            document.getElementById('editAvatarPreview').src = evt.target.result;
        };
        reader.readAsDataURL(file);
    },

    openProfileModal() {
        const user = Auth.getUser();
        if (!user) return;

        document.getElementById('profFullName').value = user.full_name || '';
        document.getElementById('profAge').value = user.age || '';
        document.getElementById('profGender').value = user.gender || '';
        document.getElementById('editAvatarPreview').src = user.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150';

        const isVendor = user.role === 'vendor' || user.role === 'seller';
        const vendorField = document.getElementById('vendorAgencyField');
        if (isVendor) {
            vendorField.classList.remove('d-none');
            document.getElementById('profAgencyName').value = user.agency_name || '';
        } else {
            vendorField.classList.add('d-none');
        }

        new bootstrap.Modal(document.getElementById('modalEditProfile')).show();
    },

    openPasswordModal() {
        new bootstrap.Modal(document.getElementById('modalChangePassword')).show();
    },

    async sendPasswordOtp() {
        const user = Auth.getUser();
        if (!user) return;

        const btn = document.getElementById('btnSendDrawerOtp');
        btn.disabled = true;
        btn.innerText = 'Sending OTP...';

        try {
            const res = await fetch(`${API_BASE}/auth/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: user.email })
            });
            const data = await res.json();
            alert(data.message || 'OTP sent! Please check your terminal or email.');
            btn.disabled = false;
            btn.innerText = 'Resend Code';
        } catch (err) {
            alert('Failed to send OTP code.');
            btn.disabled = false;
            btn.innerText = 'Send Verification OTP';
        }
    },

    openTermsModal(type = 'customer') {
        const titleEl = document.getElementById('termsModalTitle');
        const listEl = document.getElementById('termsListBody');
        const terms = type === 'vendor' ? VENDOR_TERMS : CUSTOMER_TERMS;

        titleEl.innerHTML = `<i class="fas fa-file-contract text-info me-2"></i>${type === 'vendor' ? 'Vendor & Agency Operating Terms (23 Clauses)' : 'Customer Terms of Service (25 Clauses)'}`;
        listEl.innerHTML = `
            <div class="d-flex flex-column gap-2">
                ${terms.map(t => `<div class="p-2 rounded border border-secondary text-light small" style="background: rgba(255,255,255,0.03);">${t}</div>`).join('')}
            </div>
        `;
        new bootstrap.Modal(document.getElementById('modalTermsCatalog')).show();
    },

    openFaqModal() {
        new bootstrap.Modal(document.getElementById('modalFaqSheet')).show();
    }
};