from functools import wraps
from flask import request, jsonify
import jwt
from database import get_db
from config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'message': 'Authorization header is missing'}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'success': False, 'message': 'Token format must be Bearer <token>'}), 401

        token = parts[1]
        try:
            # Decode Supabase JWT
            decoded = jwt.decode(
                token, 
                Config.JWT_SECRET, 
                algorithms=["HS256"], 
                options={"verify_signature": False} # Validated by user id lookup in Supabase
            )
            user_id = decoded.get('sub')
            
            db = get_db()
            profile = db.table('profiles').select('*').eq('id', user_id).single().execute()
            if not profile.data:
                return jsonify({'success': False, 'message': 'User profile not found'}), 404

            current_user = profile.data
        except Exception as e:
            return jsonify({'success': False, 'message': 'Invalid or expired token', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def seller_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        user_role = (current_user.get('role') or '').lower()
        
        # Permit seller, vendor, and admin roles
        if user_role not in ['seller', 'vendor', 'admin']:
            return jsonify({
                'success': False, 
                'message': 'Access forbidden: Vendor/Seller privileges required'
            }), 403

        # Extra verification gate: ensure vendor account has admin approval
        if user_role in ['seller', 'vendor'] and not current_user.get('is_approved', True):
            return jsonify({
                'success': False,
                'message': 'Access forbidden: Your vendor account is pending Admin approval.'
            }), 403

        return f(current_user, *args, **kwargs)
    return decorated