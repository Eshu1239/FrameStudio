// Dynamic API Base URL: Automatically points to Localhost during development or Render in production
// FrameStudio API Base Configuration
const API_BASE = window.location.hostname.includes('render.com')
    ? 'https://framestudio-backend.onrender.com/api'
    : 'http://localhost:5000/api';
const Auth = {
    getUser() {
        try {
            return JSON.parse(localStorage.getItem('fs_user'));
        } catch {
            return null;
        }
    },
    getToken() {
        return localStorage.getItem('fs_token');
    },
    setUser(user, token) {
        localStorage.setItem('fs_user', JSON.stringify(user));
        if (token) localStorage.setItem('fs_token', token);
    },
    logout() {
        localStorage.removeItem('fs_user');
        localStorage.removeItem('fs_token');
        const isInAdmin = window.location.pathname.includes('/admin/');
        window.location.href = isInAdmin ? '../customer/login.html' : 'login.html';
    },
    checkAuth(requireAuth = false) {
        const user = this.getUser();
        const token = this.getToken();
        if (requireAuth && (!user || !token)) {
            const isInAdmin = window.location.pathname.includes('/admin/');
            window.location.href = isInAdmin ? '../customer/login.html' : 'login.html';
            return null;
        }
        return user;
    },
    renderNavAuth() {
        const navContainer = document.getElementById('navAuthLinks');
        if (!navContainer) return;

        const user = this.getUser();
        if (user) {
            const roleLabel = user.role ? user.role.toUpperCase() : 'USER';
            const isAdminOrVendor = user.role === 'admin' || user.role === 'vendor' || user.role === 'seller';

            navContainer.innerHTML = `
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle text-white d-flex align-items-center gap-2 fw-semibold" href="#" role="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user-circle fs-5" style="color: #00f2fe;"></i>
                        <span>${user.full_name || user.email.split('@')[0]}</span>
                        <span class="badge ${user.role === 'admin' ? 'bg-danger' : (isAdminOrVendor ? 'bg-primary' : 'bg-secondary')} small">${roleLabel}</span>
                    </a>
                    <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end shadow-lg" style="background: #0d1322; border: 1px solid rgba(255,255,255,0.15);">
                        ${isAdminOrVendor ? `<li><a class="dropdown-item py-2 text-info" href="../admin/dashboard.html"><i class="fas fa-shield-halved me-2"></i>Admin Dashboard</a></li>` : ''}
                        <li><a class="dropdown-item py-2 text-white" href="orders.html"><i class="fas fa-box-open me-2"></i>My Orders</a></li>
                        <li><hr class="dropdown-divider border-secondary"></li>
                        <li><a class="dropdown-item py-2 text-danger" href="javascript:Auth.logout()"><i class="fas fa-sign-out-alt me-2"></i>Sign Out</a></li>
                    </ul>
                </li>
            `;
        } else {
            navContainer.innerHTML = `
                <li class="nav-item">
                    <a href="login.html" class="nav-link text-white fw-semibold">Sign In</a>
                </li>
                <li class="nav-item">
                    <a href="register.html" class="btn btn-luxury btn-sm ms-2">Sign Up</a>
                </li>
            `;
        }
    }
};

// Global Shopping Cart Helper
const Cart = {
    get() {
        return this.getItems();
    },
    getItems() {
        try {
            return JSON.parse(localStorage.getItem('fs_cart')) || [];
        } catch {
            return [];
        }
    },
    save(items) {
        localStorage.setItem('fs_cart', JSON.stringify(items));
        this.updateBadge();
    },
    add(product, qty = 1) {
        const items = this.getItems();
        const existing = items.find(i => i.product_id === product.id);
        if (existing) {
            existing.quantity += qty;
        } else {
            items.push({
                product_id: product.id,
                product_name: product.name,
                product_image: product.image_url,
                unit_price: parseFloat(product.price),
                quantity: qty
            });
        }
        this.save(items);
    },
    remove(productId) {
        const items = this.getItems().filter(i => i.product_id !== productId);
        this.save(items);
    },
    updateQuantity(productId, qty) {
        const items = this.getItems();
        const item = items.find(i => i.product_id === productId);
        if (item) {
            if (qty <= 0) {
                this.remove(productId);
                return;
            }
            item.quantity = qty;
            this.save(items);
        }
    },
    clear() {
        localStorage.removeItem('fs_cart');
        this.updateBadge();
    },
    updateBadge() {
        const badge = document.getElementById('cartBadge');
        if (!badge) return;
        const total = this.getItems().reduce((sum, i) => sum + i.quantity, 0);
        badge.innerText = total;
        badge.style.display = total > 0 ? 'inline-block' : 'none';
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Auth.renderNavAuth();
    Cart.updateBadge();
});

// Order Status Tagline Helper
function getOrderStatusTagline(status) {
    const taglines = {
        'Pending': 'Your order has been received and is awaiting seller confirmation.',
        'Confirmed': 'Your order is confirmed! The studio is preparing your handcrafted items.',
        'Processing': 'Your custom pieces are currently being handcrafted in the studio.',
        'Shipped': 'Your order has been dispatched and is on its way to you.',
        'Out for Delivery': 'Your parcel is out for delivery today.',
        'Delivered': 'Your order has been successfully delivered. Enjoy your handcrafted creation!',
        'Cancelled': 'This order has been cancelled.'
    };
    return taglines[status] || `Status updated to ${status}.`;
}