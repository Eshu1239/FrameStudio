import uuid
from database import get_db

def generate_order_number():
    """Generates a clean, unique order reference."""
    return f"FS-{uuid.uuid4().hex[:8].upper()}"

def calculate_cart_totals(items, coupon_code=None):
    """
    Validates cart items against live Supabase database records
    and calculates accurate subtotals, shipping, and discounts.
    """
    if not items or not isinstance(items, list) or len(items) == 0:
        return {
            'items': [],
            'subtotal': 0.0,
            'discount': 0.0,
            'shipping_fee': 0.0,
            'total': 0.0,
            'coupon_applied': None
        }, None

    db = get_db()
    
    # Extract IDs safely (handling both 'id' and 'product_id')
    product_ids = []
    for item in items:
        p_id = item.get('product_id') or item.get('id')
        if p_id:
            product_ids.append(str(p_id))

    if not product_ids:
        return None, "No valid product IDs provided in cart items."

    try:
        # Fetch fresh product details from database
        res = db.table('products').select('id, name, price, stock, image_url').in_('id', product_ids).execute()
        products_map = {str(p['id']): p for p in (res.data or [])}

        verified_items = []
        subtotal = 0.0

        for item in items:
            p_id = str(item.get('product_id') or item.get('id', ''))
            qty = int(item.get('quantity', 1))
            if qty <= 0:
                continue

            # Fallback to item payload if DB lookup is pending
            db_product = products_map.get(p_id)
            if db_product:
                unit_price = float(db_product.get('price', 0))
                prod_name = db_product.get('name', 'Product')
                prod_img = db_product.get('image_url', '')
            else:
                unit_price = float(item.get('price', item.get('unit_price', 0)))
                prod_name = item.get('name', item.get('product_name', 'Product'))
                prod_img = item.get('image_url', item.get('product_image', ''))

            item_subtotal = round(unit_price * qty, 2)
            subtotal += item_subtotal

            verified_items.append({
                'product_id': p_id,
                'product_name': prod_name,
                'product_image': prod_img,
                'unit_price': unit_price,
                'quantity': qty,
                'subtotal': item_subtotal
            })

        subtotal = round(subtotal, 2)
        shipping_fee = 0.0 if subtotal >= 999.0 or subtotal == 0 else 50.0
        discount = 0.0
        applied_coupon = None

        # Process Coupon if provided
        if coupon_code and subtotal > 0:
            c_code = str(coupon_code).strip().upper()
            c_res = db.table('coupons').select('*').eq('code', c_code).eq('is_active', True).execute()
            if c_res.data:
                c_data = c_res.data[0]
                min_val = float(c_data.get('min_order_value', 0))
                if subtotal >= min_val:
                    d_percent = float(c_data.get('discount_percent', 0))
                    max_d = float(c_data.get('max_discount', 500.0))
                    calculated_discount = (subtotal * d_percent) / 100.0
                    discount = round(min(calculated_discount, max_d), 2)
                    applied_coupon = {
                        'code': c_data['code'],
                        'discount_percent': d_percent,
                        'discount_amount': discount
                    }

        total = round(max(0.0, subtotal - discount + shipping_fee), 2)

        return {
            'items': verified_items,
            'subtotal': subtotal,
            'discount': discount,
            'shipping_fee': shipping_fee,
            'total': total,
            'coupon_applied': applied_coupon
        }, None

    except Exception as e:
        return None, f"Database cart calculation failed: {str(e)}"