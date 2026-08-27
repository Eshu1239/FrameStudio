-- ================================================================
-- FRAMESTUDIO: CREATOR & SOCIAL SELLER CATALOG SEED
-- ================================================================

-- 1. Insert Creator / Artisan Categories
INSERT INTO public.categories (id, name, slug, description, image_url) VALUES
('a1111111-1111-1111-1111-111111111111', 'Handmade & Crafts', 'handmade-crafts', 'Artisanal crafts, handmade resin, pottery & customized gifts.', 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600'),
('a2222222-2222-2222-2222-222222222222', 'Photography & Prints', 'photography-prints', 'Curated photographic prints, framed memories & digital art creations.', 'https://images.unsplash.com/photo-1582561424760-0321d75e81fa?w=600'),
('a3333333-3333-3333-3333-333333333333', 'Fashion & Apparel', 'fashion-apparel', 'Boutique wear, designer jewelry & aesthetic creator merchandise.', 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=600'),
('a4444444-4444-4444-4444-444444444444', 'Customized Merch', 'customized-merch', 'Personalized bespoke pieces, custom desk decor & creator goods.', 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=600')
ON CONFLICT (id) DO NOTHING;

-- 2. Insert Products tailored for Instagram & Independent Sellers
INSERT INTO public.products (id, category_id, name, slug, description, price, stock, dimensions, material, image_url, is_featured) VALUES
('b1111111-1111-1111-1111-111111111111', 'a1111111-1111-1111-1111-111111111111', 'Handmade Ocean Resin Art Board', 'handmade-ocean-resin-art-board', 'Handcrafted beach-inspired epoxy resin serving board with raw edge teak wood.', 1299.00, 15, '14x8 inches', 'Epoxy Resin & Teak Wood', 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=600', true),
('b2222222-2222-2222-2222-222222222222', 'a2222222-2222-2222-2222-222222222222', 'Minimalist Gallery Art Print', 'minimalist-gallery-art-print', 'Archival museum matte photo print signed by independent creator.', 799.00, 25, '12x18 inches', '300 GSM Archival Cotton Paper', 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600', true),
('b3333333-3333-3333-3333-333333333333', 'a3333333-3333-3333-3333-333333333333', 'Artisan Handcrafted Silver Ring', 'artisan-handcrafted-silver-ring', 'Bespoke textured silver alloy band made in small studio batches.', 949.00, 20, 'Adjustable Fit', 'Sterling Silver Finish', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600', true),
('b4444444-4444-4444-4444-444444444444', 'a1111111-1111-1111-1111-111111111111', 'Ceramic Hand-Poured Soy Candle', 'ceramic-hand-poured-soy-candle', 'Small-batch organic lavender & vanilla candle in a reusable clay pot.', 549.00, 30, '250g Jar', 'Natural Soy Wax & Ceramic', 'https://images.unsplash.com/photo-1603006905003-be475563bc59?w=600', false),
('b5555555-5555-5555-5555-555555555555', 'a4444444-4444-4444-4444-444444444444', 'Custom Polaroids Memory Display Box', 'custom-polaroids-memory-display-box', 'Customizable wooden memory shadow-box with LED fairy lights for photos.', 1499.00, 10, '8x10 inches', 'Pine Wood & Acrylic Glass', 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=600', true),
('b6666666-6666-6666-6666-666666666666', 'a3333333-3333-3333-3333-333333333333', 'Organic Linen Oversized Studio Tote', 'organic-linen-oversized-studio-tote', 'Eco-friendly minimal tote bag embroidered by independent textile artists.', 699.00, 22, '16x15 inches', '100% Organic Linen', 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=600', true)
ON CONFLICT (id) DO NOTHING;

-- 3. Insert Promotional Coupons
INSERT INTO public.coupons (code, discount_percent, max_discount, min_order_value, is_active) VALUES
('CREATOR10', 10, 300.00, 500.00, true),
('STUDIO20', 20, 500.00, 1500.00, true),
('FESTIVE50', 50, 800.00, 3000.00, true)
ON CONFLICT (code) DO NOTHING;