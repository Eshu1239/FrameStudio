import random
import time
import os
from flask import Blueprint, request, jsonify
from database import get_db
from auth import token_required, seller_required
from services import calculate_cart_totals, generate_order_number

api = Blueprint('api', __name__)

# Master Administrator Email (Strictly protected - only this email holds Super Admin rights)
MASTER_ADMIN_EMAIL = 'eshwarie633@gmail.com'

# In-memory OTP store for password resets (email -> {otp, user_id, created_at})
OTP_STORE = {}

# ================================================================
# HEALTH CHECK
# ================================================================
@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'online', 'service': 'FrameStudio Flask API'}), 200


# ================================================================
# AUTHENTICATION & MULTI-ROLE REGISTRATION
# ================================================================
@api.route('/auth/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    role = data.get('role', 'customer').lower()

    if not email or not password or not full_name:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if 'admin' in role or role == 'admin':
        return jsonify({
            'success': False,
            'message': 'Security violation: Administrator accounts cannot be created via public registration.'
        }), 403

    if role not in ['customer', 'seller', 'vendor']:
        role = 'customer'

    is_approved = False if role in ['seller', 'vendor'] else True

    db = get_db()
    try:
        auth_res = db.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": full_name, "role": role}
        })
        
        if not auth_res.user:
            return jsonify({'success': False, 'message': 'Failed to create user account'}), 400

        db.table('profiles').update({
            'full_name': full_name,
            'role': role,
            'is_approved': is_approved
        }).eq('id', auth_res.user.id).execute()

        msg = 'Account registered successfully!'
        if not is_approved:
            msg = 'Registration submitted! Your Vendor/Agency account is pending Admin approval before you can sign in.'

        return jsonify({'success': True, 'message': msg, 'is_approved': is_approved}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@api.route('/auth/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400

    try:
        from database import supabase_public
        auth_res = supabase_public.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        db = get_db()
        profile_res = db.table('profiles').select('*').eq('id', auth_res.user.id).single().execute()
        profile = profile_res.data if profile_res.data else {
            'id': auth_res.user.id,
            'email': email,
            'full_name': auth_res.user.user_metadata.get('full_name', 'Customer'),
            'role': auth_res.user.user_metadata.get('role', 'customer'),
            'is_approved': True
        }

        if profile.get('role') == 'admin' and email != MASTER_ADMIN_EMAIL:
            db.table('profiles').update({'role': 'customer'}).eq('id', auth_res.user.id).execute()
            profile['role'] = 'customer'

        if profile.get('role') in ['seller', 'vendor'] and not profile.get('is_approved', True):
            return jsonify({
                'success': False,
                'message': 'Your Vendor/Agency account is currently awaiting Admin approval. Please contact the administrator.'
            }), 403

        return jsonify({
            'success': True,
            'token': auth_res.session.access_token,
            'user': profile
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Invalid email or password', 'error': str(e)}), 401


# ================================================================
# USER PROFILE UPDATE
# ================================================================
@api.route('/profile/update', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json() or {}
    update_data = {}

    if 'full_name' in data and data['full_name'] is not None:
        update_data['full_name'] = data['full_name'].strip()
    if 'age' in data and data['age'] != '' and data['age'] is not None:
        try:
            update_data['age'] = int(data['age'])
        except ValueError:
            pass
    if 'gender' in data and data['gender'] is not None:
        update_data['gender'] = data['gender'].strip()
    if 'agency_name' in data and data['agency_name'] is not None:
        update_data['agency_name'] = data['agency_name'].strip()
    if 'avatar_url' in data and data['avatar_url'] is not None:
        update_data['avatar_url'] = data['avatar_url']

    db = get_db()
    try:
        res = db.table('profiles').update(update_data).eq('id', current_user['id']).execute()
        if not res.data:
            return jsonify({'success': False, 'message': 'Failed to update profile'}), 400

        return jsonify({'success': True, 'message': 'Profile updated successfully!', 'user': res.data[0]}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ================================================================
# PASSWORD RECOVERY (OTP FLOW)
# ================================================================
@api.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'success': False, 'message': 'Please enter your registered email address'}), 400

    db = get_db()
    try:
        profile = db.table('profiles').select('id, full_name').eq('email', email).execute()
        if not profile.data:
            return jsonify({'success': False, 'message': 'No account registered with this email'}), 404

        otp_code = f"{random.randint(100000, 999999)}"
        OTP_STORE[email] = {
            'otp': otp_code,
            'user_id': profile.data[0]['id'],
            'created_at': time.time()
        }

        try:
            from database import supabase_public
            supabase_public.auth.reset_password_for_email(email)
        except Exception:
            pass

        db.table('notifications').insert({
            'user_id': profile.data[0]['id'],
            'title': 'Password Reset OTP Requested',
            'message': f"Your 6-digit password reset verification code is: {otp_code}"
        }).execute()

        print(f"\n[SECURITY OTP] Password reset OTP for {email}: {otp_code}\n")

        return jsonify({
            'success': True,
            'message': f'Verification OTP sent to {email}. (Check console/email)'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@api.route('/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    otp_entered = data.get('otp', '').strip()
    new_password = data.get('new_password', '')

    if not email or not otp_entered or not new_password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400

    record = OTP_STORE.get(email)
    if not record:
        return jsonify({'success': False, 'message': 'No OTP request found for this email. Please request again.'}), 400

    if time.time() - record['created_at'] > 600:
        OTP_STORE.pop(email, None)
        return jsonify({'success': False, 'message': 'OTP has expired. Please request a new one.'}), 400

    if record['otp'] != otp_entered:
        return jsonify({'success': False, 'message': 'Invalid verification code'}), 400

    db = get_db()
    try:
        db.auth.admin.update_user_by_id(record['user_id'], {"password": new_password})
        OTP_STORE.pop(email, None)
        return jsonify({'success': True, 'message': 'Password has been reset successfully! Please sign in.'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ================================================================
# CATEGORIES & PUBLIC STOREFRONT CATALOG
# ================================================================
@api.route('/categories', methods=['GET'])
def get_categories():
    db = get_db()
    res = db.table('categories').select('*').order('name').execute()
    return jsonify({'success': True, 'data': res.data}), 200


@api.route('/products', methods=['GET'])
def get_products():
    db = get_db()
    category = request.args.get('category')
    search = request.args.get('search')
    sort = request.args.get('sort', 'newest')

    query = db.table('products').select('*, categories(name, slug)')

    if category:
        c_res = db.table('categories').select('id').eq('slug', category).execute()
        if c_res.data:
            query = query.eq('category_id', c_res.data[0]['id'])

    if search:
        query = query.ilike('name', f'%{search}%')

    if sort == 'price_low':
        query = query.order('price', desc=False)
    elif sort == 'price_high':
        query = query.order('price', desc=True)
    else:
        query = query.order('created_at', desc=True)

    res = query.execute()
    return jsonify({'success': True, 'data': res.data}), 200


@api.route('/products/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    db = get_db()
    res = db.table('products').select('*, categories(name, slug)').eq('id', product_id).single().execute()
    if not res.data:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    return jsonify({'success': True, 'data': res.data}), 200


# ================================================================
# CART RECALCULATION & COUPONS
# ================================================================
@api.route('/cart/verify', methods=['POST'])
def verify_cart():
    data = request.get_json() or {}
    items = data.get('items', [])
    coupon = data.get('coupon')

    result, err = calculate_cart_totals(items, coupon)
    if err:
        return jsonify({'success': False, 'message': err}), 400

    return jsonify({'success': True, 'data': result}), 200


@api.route('/coupons/apply', methods=['POST'])
def apply_coupon():
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    subtotal = float(data.get('subtotal', 0))

    db = get_db()
    res = db.table('coupons').select('*').eq('code', code).eq('is_active', True).execute()
    if not res.data:
        return jsonify({'success': False, 'message': 'Invalid or expired coupon code'}), 400

    coupon = res.data[0]
    if subtotal < float(coupon.get('min_order_value', 0)):
        return jsonify({'success': False, 'message': f"Minimum order value of Rs. {coupon['min_order_value']} required"}), 400

    discount = (subtotal * float(coupon['discount_percent'])) / 100.0
    discount = min(discount, float(coupon.get('max_discount', 500.0)))

    return jsonify({
        'success': True,
        'coupon': {
            'code': coupon['code'],
            'discount_percent': coupon['discount_percent'],
            'discount_amount': round(discount, 2)
        }
    }), 200


# ================================================================
# CHECKOUT & CUSTOMER ORDERS
# ================================================================
@api.route('/orders/checkout', methods=['POST'])
@token_required
def checkout(current_user):
    data = request.get_json() or {}
    items = data.get('items', [])
    payment_method = data.get('payment_method')
    address = data.get('address')
    coupon_code = data.get('coupon_code')

    if not items or payment_method not in ['UPI', 'COD'] or not address:
        return jsonify({'success': False, 'message': 'Incomplete checkout parameters'}), 400

    totals, err = calculate_cart_totals(items, coupon_code)
    if err:
        return jsonify({'success': False, 'message': err}), 400

    db = get_db()
    order_num = generate_order_number()

    initial_payment_status = 'Pending Verification' if payment_method == 'UPI' else 'Pending'
    initial_order_status = 'Confirmed' if payment_method == 'COD' else 'Pending'

    order_payload = {
        'order_number': order_num,
        'user_id': current_user['id'],
        'subtotal': totals['subtotal'],
        'discount': totals['discount'],
        'shipping_fee': totals['shipping_fee'],
        'total': totals['total'],
        'payment_method': payment_method,
        'payment_status': initial_payment_status,
        'order_status': initial_order_status,
        'shipping_address': address
    }

    order_res = db.table('orders').insert(order_payload).execute()
    if not order_res.data:
        return jsonify({'success': False, 'message': 'Failed to create order'}), 500

    created_order = order_res.data[0]

    for item in totals['items']:
        db.table('order_items').insert({
            'order_id': created_order['id'],
            'product_id': item['product_id'],
            'product_name': item['product_name'],
            'product_image': item['product_image'],
            'unit_price': item['unit_price'],
            'quantity': item['quantity'],
            'subtotal': item['subtotal']
        }).execute()
        
        try:
            db.rpc('decrement_stock', {'p_id': item['product_id'], 'qty': item['quantity']}).execute()
        except Exception:
            pass

    db.table('payments').insert({
        'order_id': created_order['id'],
        'method': payment_method,
        'amount': totals['total'],
        'status': initial_payment_status
    }).execute()

    db.table('shipping').insert({
        'order_id': created_order['id'],
        'status': 'Processing'
    }).execute()

    db.table('notifications').insert({
        'user_id': current_user['id'],
        'title': 'Order Placed Successfully!',
        'message': f"Your order {order_num} has been placed via {payment_method}."
    }).execute()

    return jsonify({'success': True, 'order': created_order}), 201


@api.route('/orders/my-orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    db = get_db()
    res = db.table('orders').select('*, order_items(*), shipping(*), payments(*)').eq('user_id', current_user['id']).order('created_at', desc=True).execute()
    return jsonify({'success': True, 'data': res.data}), 200


@api.route('/orders/<order_id>', methods=['GET'])
@token_required
def get_order_by_id(current_user, order_id):
    db = get_db()
    query = db.table('orders').select('*, order_items(*), shipping(*), payments(*), profiles(full_name, email, phone)').eq('id', order_id)
    
    if current_user.get('role') not in ['seller', 'vendor', 'admin']:
        query = query.eq('user_id', current_user['id'])

    res = query.single().execute()
    if not res.data:
        return jsonify({'success': False, 'message': 'Order not found'}), 404

    return jsonify({'success': True, 'data': res.data}), 200


# ================================================================
# VENDOR / ADMIN CONTROLLERS (WITH STRICT MULTI-TENANT ISOLATION)
# ================================================================

@api.route('/admin/dashboard-stats', methods=['GET'])
@token_required
@seller_required
def admin_stats(current_user):
    db = get_db()
    is_master_admin = (current_user.get('role') == 'admin' and current_user.get('email') == MASTER_ADMIN_EMAIL)
    vendor_id = current_user['id']

    if is_master_admin:
        orders_res = db.table('orders').select('total, order_status, payment_status, created_at').execute()
        orders = orders_res.data or []

        total_sales = sum(float(o['total']) for o in orders if o.get('payment_status') == 'Successful' or o.get('order_status') == 'Delivered')
        total_orders = len(orders)
        new_orders = len([o for o in orders if o.get('order_status') in ['Pending', 'Confirmed']])

        prod_res = db.table('products').select('id, name, stock').lte('stock', 5).execute()
        low_stock = prod_res.data or []

        users_res = db.table('profiles').select('id, role, is_approved').execute()
        all_users = users_res.data or []

        total_users = len(all_users)
        total_customers = len([u for u in all_users if (u.get('role') or '').lower() == 'customer'])
        total_vendors = len([u for u in all_users if (u.get('role') or '').lower() in ['vendor', 'seller']])
        pending_vendors = len([u for u in all_users if (u.get('role') or '').lower() in ['vendor', 'seller'] and u.get('is_approved') is False])

        return jsonify({
            'success': True,
            'stats': {
                'total_sales': round(total_sales, 2),
                'total_orders': total_orders,
                'new_orders': new_orders,
                'low_stock_count': len(low_stock),
                'total_users': total_users,
                'total_customers': total_customers,
                'total_vendors': total_vendors,
                'pending_vendors': pending_vendors
            }
        }), 200
    else:
        vendor_prods_res = db.table('products').select('id, stock').eq('seller_id', vendor_id).execute()
        vendor_prods = vendor_prods_res.data or []
        vendor_prod_ids = [p['id'] for p in vendor_prods]
        low_stock_count = len([p for p in vendor_prods if (p.get('stock') or 0) <= 5])

        if not vendor_prod_ids:
            return jsonify({
                'success': True,
                'stats': {
                    'total_sales': 0.0,
                    'total_orders': 0,
                    'new_orders': 0,
                    'low_stock_count': 0
                }
            }), 200

        items_res = db.table('order_items').select('order_id, subtotal, product_id').in_('product_id', vendor_prod_ids).execute()
        vendor_items = items_res.data or []
        vendor_order_ids = list(set([it['order_id'] for it in vendor_items if it.get('order_id')]))

        if not vendor_order_ids:
            return jsonify({
                'success': True,
                'stats': {
                    'total_sales': 0.0,
                    'total_orders': 0,
                    'new_orders': 0,
                    'low_stock_count': low_stock_count
                }
            }), 200

        orders_res = db.table('orders').select('id, total, order_status, payment_status').in_('id', vendor_order_ids).execute()
        vendor_orders = orders_res.data or []

        paid_order_ids = set([o['id'] for o in vendor_orders if o.get('payment_status') == 'Successful' or o.get('order_status') == 'Delivered'])
        total_sales = sum(float(it['subtotal']) for it in vendor_items if it.get('order_id') in paid_order_ids)
        total_orders = len(vendor_orders)
        new_orders = len([o for o in vendor_orders if o.get('order_status') in ['Pending', 'Confirmed']])

        return jsonify({
            'success': True,
            'stats': {
                'total_sales': round(total_sales, 2),
                'total_orders': total_orders,
                'new_orders': new_orders,
                'low_stock_count': low_stock_count
            }
        }), 200


@api.route('/admin/my-products', methods=['GET'])
@token_required
@seller_required
def get_vendor_products(current_user):
    db = get_db()
    is_master_admin = (current_user.get('role') == 'admin' and current_user.get('email') == MASTER_ADMIN_EMAIL)
    
    try:
        query = db.table('products').select('*, categories(*)').order('created_at', desc=True)
        
        if not is_master_admin:
            query = query.eq('seller_id', current_user['id'])

        res = query.execute()
        return jsonify({'success': True, 'data': res.data or []}), 200
    except Exception as e:
        try:
            fallback = db.table('products').select('*').order('created_at', desc=True)
            if not is_master_admin:
                fallback = fallback.eq('seller_id', current_user['id'])
            res_fb = fallback.execute()
            return jsonify({'success': True, 'data': res_fb.data or []}), 200
        except Exception as err:
            return jsonify({'success': False, 'message': str(err)}), 500


@api.route('/admin/orders', methods=['GET'])
@token_required
@seller_required
def admin_orders(current_user):
    db = get_db()
    is_master_admin = (current_user.get('role') == 'admin' and current_user.get('email') == MASTER_ADMIN_EMAIL)
    
    if is_master_admin:
        res = db.table('orders').select('*, order_items(*), shipping(*), payments(*), profiles(full_name, email)').order('created_at', desc=True).execute()
        return jsonify({'success': True, 'data': res.data or []}), 200

    vendor_prods_res = db.table('products').select('id').eq('seller_id', current_user['id']).execute()
    vendor_prod_ids = set([p['id'] for p in (vendor_prods_res.data or [])])

    if not vendor_prod_ids:
        return jsonify({'success': True, 'data': []}), 200

    items_res = db.table('order_items').select('*').in_('product_id', list(vendor_prod_ids)).execute()
    vendor_items = items_res.data or []
    vendor_order_ids = list(set([it['order_id'] for it in vendor_items if it.get('order_id')]))

    if not vendor_order_ids:
        return jsonify({'success': True, 'data': []}), 200

    orders_res = db.table('orders').select('*, shipping(*), payments(*), profiles(full_name, email)').in_('id', vendor_order_ids).order('created_at', desc=True).execute()
    raw_orders = orders_res.data or []

    filtered_orders = []
    for o in raw_orders:
        o_items = [it for it in vendor_items if it.get('order_id') == o['id']]
        if o_items:
            o_copy = dict(o)
            o_copy['order_items'] = o_items
            o_copy['total'] = sum(float(it.get('subtotal', 0)) for it in o_items)
            filtered_orders.append(o_copy)

    return jsonify({'success': True, 'data': filtered_orders}), 200


@api.route('/admin/orders/<order_id>/status', methods=['PUT'])
@token_required
@seller_required
def update_order_status(current_user, order_id):
    data = request.get_json() or {}
    new_order_status = data.get('order_status')
    new_payment_status = data.get('payment_status')

    db = get_db()
    update_data = {}
    if new_order_status:
        update_data['order_status'] = new_order_status
    if new_payment_status:
        update_data['payment_status'] = new_payment_status

    if update_data:
        db.table('orders').update(update_data).eq('id', order_id).execute()
        if new_payment_status:
            db.table('payments').update({'status': new_payment_status}).eq('order_id', order_id).execute()

    return jsonify({'success': True, 'message': 'Order updated successfully'}), 200


@api.route('/admin/orders/<order_id>/shipping', methods=['PUT'])
@token_required
@seller_required
def update_shipping(current_user, order_id):
    data = request.get_json() or {}
    courier = data.get('courier_name')
    tracking = data.get('tracking_number')
    exp_date = data.get('expected_delivery')

    db = get_db()
    db.table('shipping').update({
        'courier_name': courier,
        'tracking_number': tracking,
        'expected_delivery': exp_date,
        'status': 'Shipped'
    }).eq('order_id', order_id).execute()

    db.table('orders').update({'order_status': 'Shipped'}).eq('id', order_id).execute()

    return jsonify({'success': True, 'message': 'Shipping updated and order marked Shipped'}), 200


# ================================================================
# CATALOG CRUD (WITH AUTOMATIC SELLER LINKING)
# ================================================================
@api.route('/admin/products', methods=['POST'])
@token_required
@seller_required
def create_product(current_user):
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    category_id = data.get('category_id')
    custom_category = data.get('custom_category', '').strip()
    price = float(data.get('price', 0))
    stock = int(data.get('stock', 1))
    description = data.get('description', '').strip()
    dimensions = data.get('dimensions', 'Custom Standard').strip()
    material = data.get('material', 'Artisanal Handcrafted').strip()
    image_url = data.get('image_url', 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600')

    if not name or price <= 0:
        return jsonify({'success': False, 'message': 'Name and a valid Price are required'}), 400

    db = get_db()

    if category_id == 'OTHER' or not category_id:
        if not custom_category:
            return jsonify({'success': False, 'message': 'Please specify your custom category name'}), 400
        
        cat_slug = custom_category.lower().replace(' ', '-').replace('/', '-')[:50]
        existing_cat = db.table('categories').select('id').eq('slug', cat_slug).execute()
        if existing_cat.data:
            category_id = existing_cat.data[0]['id']
        else:
            new_cat = db.table('categories').insert({
                'name': custom_category.title(),
                'slug': cat_slug,
                'description': f'Custom offerings under {custom_category.title()}'
            }).execute()
            if new_cat.data:
                category_id = new_cat.data[0]['id']
            else:
                return jsonify({'success': False, 'message': 'Failed to create category'}), 500

    slug = name.lower().replace(' ', '-').replace('/', '-')[:50]

    res = db.table('products').insert({
        'name': name,
        'slug': slug,
        'category_id': category_id,
        'seller_id': current_user['id'],
        'price': price,
        'stock': stock,
        'description': description,
        'dimensions': dimensions,
        'material': material,
        'image_url': image_url,
        'is_featured': True
    }).execute()

    if not res.data:
        return jsonify({'success': False, 'message': 'Failed to save product/service'}), 500

    return jsonify({'success': True, 'data': res.data[0]}), 201


@api.route('/admin/products/<product_id>', methods=['PUT'])
@token_required
@seller_required
def update_product(current_user, product_id):
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    category_id = data.get('category_id')
    custom_category = data.get('custom_category', '').strip()
    price = data.get('price')
    stock = data.get('stock')
    description = data.get('description', '').strip()
    dimensions = data.get('dimensions', '').strip()
    material = data.get('material', '').strip()
    image_url = data.get('image_url', '').strip()

    if not name or price is None or stock is None:
        return jsonify({'success': False, 'message': 'Title, Price, and Stock are required'}), 400

    db = get_db()
    is_master_admin = (current_user.get('role') == 'admin' and current_user.get('email') == MASTER_ADMIN_EMAIL)

    existing = db.table('products').select('seller_id').eq('id', product_id).single().execute()
    if not existing.data:
        return jsonify({'success': False, 'message': 'Listing not found'}), 404
    if not is_master_admin and existing.data.get('seller_id') != current_user['id']:
        return jsonify({'success': False, 'message': 'Unauthorized: You can only edit your own listings'}), 403

    if category_id == 'OTHER':
        if not custom_category:
            return jsonify({'success': False, 'message': 'Please specify your custom category name'}), 400
        
        cat_slug = custom_category.lower().replace(' ', '-').replace('/', '-')[:50]
        existing_cat = db.table('categories').select('id').eq('slug', cat_slug).execute()
        if existing_cat.data:
            category_id = existing_cat.data[0]['id']
        else:
            new_cat = db.table('categories').insert({
                'name': custom_category.title(),
                'slug': cat_slug,
                'description': f'Custom offerings under {custom_category.title()}'
            }).execute()
            if new_cat.data:
                category_id = new_cat.data[0]['id']
            else:
                return jsonify({'success': False, 'message': 'Failed to create category'}), 500

    update_payload = {
        'name': name,
        'slug': name.lower().replace(' ', '-').replace('/', '-')[:50],
        'category_id': category_id,
        'price': float(price),
        'stock': int(stock),
        'description': description,
        'dimensions': dimensions,
        'material': material,
        'image_url': image_url or 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600'
    }

    res = db.table('products').update(update_payload).eq('id', product_id).execute()
    if not res.data:
        return jsonify({'success': False, 'message': 'Failed to update listing'}), 500

    return jsonify({'success': True, 'message': 'Listing updated successfully!', 'data': res.data[0]}), 200


@api.route('/admin/products/<product_id>', methods=['DELETE'])
@token_required
@seller_required
def delete_product(current_user, product_id):
    db = get_db()
    is_master_admin = (current_user.get('role') == 'admin' and current_user.get('email') == MASTER_ADMIN_EMAIL)

    existing = db.table('products').select('seller_id').eq('id', product_id).single().execute()
    if not existing.data:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    if not is_master_admin and existing.data.get('seller_id') != current_user['id']:
        return jsonify({'success': False, 'message': 'Unauthorized: You can only delete your own listings'}), 403

    db.table('products').delete().eq('id', product_id).execute()
    return jsonify({'success': True, 'message': 'Item removed successfully'}), 200


# ================================================================
# SUPER ADMIN USER MODERATION
# ================================================================
@api.route('/admin/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    if current_user.get('role') != 'admin' or current_user.get('email') != MASTER_ADMIN_EMAIL:
        return jsonify({'success': False, 'message': 'Unauthorized: Super Admin access required'}), 403

    db = get_db()
    users_res = db.table('profiles').select('*').order('created_at', desc=True).execute()
    return jsonify({'success': True, 'data': users_res.data}), 200


@api.route('/admin/users/<user_id>/approval', methods=['PUT'])
@token_required
def set_user_approval(current_user, user_id):
    if current_user.get('role') != 'admin' or current_user.get('email') != MASTER_ADMIN_EMAIL:
        return jsonify({'success': False, 'message': 'Unauthorized: Super Admin access required'}), 403

    data = request.get_json() or {}
    is_approved = data.get('is_approved', True)

    db = get_db()
    db.table('profiles').update({'is_approved': is_approved}).eq('id', user_id).execute()
    return jsonify({'success': True, 'message': f"Vendor status updated to {'Approved' if is_approved else 'Suspended'}"}), 200


@api.route('/admin/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if current_user.get('role') != 'admin' or current_user.get('email') != MASTER_ADMIN_EMAIL:
        return jsonify({'success': False, 'message': 'Unauthorized: Super Admin access required'}), 403

    db = get_db()
    try:
        target = db.table('profiles').select('email').eq('id', user_id).single().execute()
        if target.data and target.data.get('email') == MASTER_ADMIN_EMAIL:
            return jsonify({'success': False, 'message': 'Protected Master Admin account cannot be deleted.'}), 400

        db.auth.admin.delete_user(user_id)
        db.table('profiles').delete().eq('id', user_id).execute()
        return jsonify({'success': True, 'message': 'User permanently removed'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ================================================================
# SUPER ADMIN ORDER PURGE
# ================================================================
@api.route('/admin/orders/<order_id>', methods=['DELETE'])
@token_required
def delete_order_admin_only(current_user, order_id):
    if current_user.get('role') != 'admin' or current_user.get('email') != MASTER_ADMIN_EMAIL:
        return jsonify({'success': False, 'message': 'Unauthorized: Only Super Admin can purge orders.'}), 403

    db = get_db()
    try:
        db.table('payments').delete().eq('order_id', order_id).execute()
        db.table('shipping').delete().eq('order_id', order_id).execute()
        db.table('order_items').delete().eq('order_id', order_id).execute()
        db.table('orders').delete().eq('id', order_id).execute()
        return jsonify({'success': True, 'message': 'Order removed from ledger.'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ================================================================
# REVIEWS & RATINGS ENGINE
# ================================================================
@api.route('/products/<product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    db = get_db()
    try:
        res = db.table('reviews').select('*, profiles(full_name, avatar_url)').eq('product_id', product_id).order('created_at', desc=True).execute()
        return jsonify({'success': True, 'data': res.data or []}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@api.route('/reviews', methods=['POST'])
@token_required
def submit_review(current_user):
    data = request.get_json() or {}
    product_id = data.get('product_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip()
    order_id = data.get('order_id')

    if not product_id or not rating or not comment:
        return jsonify({'success': False, 'message': 'Product, star rating, and review text are required.'}), 400

    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            return jsonify({'success': False, 'message': 'Rating must be between 1 and 5 stars.'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid rating format.'}), 400

    db = get_db()
    try:
        review_payload = {
            'product_id': product_id,
            'user_id': current_user['id'],
            'rating': rating_int,
            'comment': comment,
            'order_id': order_id
        }
        res = db.table('reviews').insert(review_payload).execute()
        if not res.data:
            return jsonify({'success': False, 'message': 'Failed to save review.'}), 500

        all_reviews = db.table('reviews').select('rating').eq('product_id', product_id).execute()
        ratings = [r['rating'] for r in (all_reviews.data or [])]
        avg_calc = round(sum(ratings) / len(ratings), 2) if ratings else 5.0
        total_cnt = len(ratings)

        db.table('products').update({
            'avg_rating': avg_calc,
            'total_reviews': total_cnt
        }).eq('id', product_id).execute()

        return jsonify({'success': True, 'message': 'Review submitted successfully!', 'data': res.data[0]}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400