# AgriConnect Architecture & Design System

AgriConnect is a comprehensive direct-from-farm e-commerce and bulk trading platform.

## Module Structure

1. **Public / Auth**: Landing page (`/`), Login (`/login`), Registration (`/register`), Admin Portal Login (`/admin/login`).
2. **Farmer Module**:
   - Layout: `src/components/Root.jsx`
   - Primary routes: `/dashboard`, `/produce`, `/orders`, `/verification`, `/shipments`, `/forecasts`, `/profile`, `/settings`.
3. **Consumer Module**:
   - Layout: `src/components/ConsumerRoot.jsx`
   - Primary routes: `/consumer` (Dashboard), `/consumer/marketplace`, `/consumer/cart`, `/consumer/orders`, `/consumer/tracking`, `/consumer/profile`.
4. **Admin Module**:
   - Layout: `src/components/AdminRoot.jsx`
   - Primary routes: `/admin` (Dashboard), `/admin/verification`, `/admin/disputes`, `/admin/users`, `/admin/listings`, `/admin/orders`, `/admin/monitoring`, `/admin/settings`.

## Design Guidelines
- Modern, clean agricultural aesthetic featuring fresh forest greens (`#166534`, `#14532d`, `#22c55e`), soft earthy neutrals, and crystal-clear photography.
- No emojis as product or category placeholders; always use high-resolution, vibrant product imagery.
