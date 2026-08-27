import time
from database import get_db

def calculate_cart_totals(items, coupon_code=None):
    db = get_db()
    subtotal = 0.0
    validated_items = []

    for item in items:
        p_id = item.get('product_id')
        qty = int(item.get('quantity', 1))

        if not p_id:
            continue

        try:
            # Query product without throwing if not found
            res = db.table('products').select('*').eq('id', p_id).execute()
            if not res.data:
                continue  # Skip stale or deleted items automatically

            product = res.data[0]

            if product['stock'] < qty:
                return None, f"Insufficient stock for {product['name']}. Available: {product['stock']}"

            price = float(product['price'])
            item_subtotal = price * qty
            subtotal += item_subtotal

            validated_items.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'product_image': product['image_url'],
                'unit_price': price,
                'quantity': qty,
                'subtotal': item_subtotal
            })
        except Exception as e:
            print(f"Error querying product {p_id}: {e}")
            continue

    # Calculate Promo Discount
    discount = 0.0
    if coupon_code and subtotal > 0:
        try:
            c_res = db.table('coupons').select('*').eq('code', coupon_code.upper()).eq('is_active', True).execute()
            if c_res.data:
                coupon = c_res.data[0]
                if subtotal >= float(coupon.get('min_order_value', 0)):
                    raw_discount = (subtotal * float(coupon['discount_percent'])) / 100.0
                    discount = min(raw_discount, float(coupon.get('max_discount', 500.0)))
        except Exception as e:
            print(f"Coupon error: {e}")

    # Shipping Calculation (Free above Rs. 999)
    shipping_fee = 0.0 if subtotal >= 999.0 or subtotal == 0.0 else 99.0
    final_total = max(0.0, subtotal - discount + shipping_fee)

    return {
        'subtotal': round(subtotal, 2),
        'discount': round(discount, 2),
        'shipping_fee': round(shipping_fee, 2),
        'total': round(final_total, 2),
        'items': validated_items
    }, None

def generate_order_number():
    timestamp = int(time.time())
    return f"FS-ORD-{timestamp % 1000000:06d}"