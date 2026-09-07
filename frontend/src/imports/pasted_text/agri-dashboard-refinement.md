Refine the current AgriConnect Farmer Dashboard using the uploaded/reference design.

DO NOT redesign the dashboard from scratch.
Keep the current layout, information hierarchy and overall structure, but make the following corrections and improvements.

━━━━━━━━━━━━━━━━━━━━
1. FIX THE GREEN COLOR SYSTEM
━━━━━━━━━━━━━━━━━━━━

The current green is too bright/neon and does not match the intended AgriConnect design system.

Use this exact color palette:

Primary Green:
#166534

Secondary Green:
#22C55E

Background:
#F8FAFB

Text:
#17201A

Warning:
#F59E0B

Error:
#DC2626

Success:
#16A34A

Border:
#E5E7EB

IMPORTANT COLOR USAGE:

- Sidebar background MUST be #166534.
- Primary buttons MUST use #166534.
- Active sidebar item should use #22C55E, but in a restrained way.
- Main headings should use #17201A.
- Normal text should use dark gray rather than green.
- Green should be used as an accent, not flood the entire interface.
- Status badges can use lighter tints of the appropriate status colors.
- Do NOT use neon green.
- Do NOT introduce any other green shades that conflict with this palette.

The result should feel like a professional agricultural product, not a bright gaming/crypto dashboard.

━━━━━━━━━━━━━━━━━━━━
2. FIX THE SIDEBAR
━━━━━━━━━━━━━━━━━━━━

Keep the existing sidebar structure.

Sidebar background:
#166534

AgriConnect logo at the top.

Navigation:

Dashboard
My Produce
Orders
Verification
Shipments
Forecasts
Profile
Settings

Dashboard active state:
Use #22C55E as the active background.

Keep icons simple, clean and consistent.

Do not make the sidebar excessively rounded or decorative.

━━━━━━━━━━━━━━━━━━━━
3. PROFILE MUST BE FUNCTIONAL
━━━━━━━━━━━━━━━━━━━━

The current profile area in the top-right must behave like an actual interactive profile menu.

When the user clicks the farmer profile/avatar/name:

Open a compact profile dropdown/popover.

Show:

Ravi Kumar
Farmer

Email:
ravi@example.com

Phone:
+91 XXXXX XXXXX

Divider

Profile

Logout

The email and phone number should be visually clear but secondary.

Add a clear "Logout" action at the bottom.

Use a confirmation dialog when Logout is clicked:

"Are you sure you want to logout?"

Buttons:
Cancel
Logout

Do NOT create a separate huge profile page for this interaction.

The profile dropdown should feel like a real production application.

━━━━━━━━━━━━━━━━━━━━
4. "VIEW ALL" FOR YOUR PRODUCE MUST WORK
━━━━━━━━━━━━━━━━━━━━

The "View all →" link beside "Your Produce" must be an actual navigation interaction.

When clicked, it should navigate to:

My Produce

The My Produce page should display ALL produce listings belonging to the logged-in farmer.

Do not simply expand the dashboard table.

The dashboard should continue showing only the most recent/relevant produce items.

The My Produce page should contain:

Search
Crop filter
Status filter

And a complete produce table containing:

Product
Quantity
Price/Unit
Status
Actions

Example:

Tomato
100 kg
₹40/kg
Available

Rice
500 kg
₹55/kg
Available

Mango
200 kg
₹90/kg
Available

The full page should support additional products beyond these examples.

━━━━━━━━━━━━━━━━━━━━
5. "VIEW ALL" FOR RECENT ORDERS MUST WORK
━━━━━━━━━━━━━━━━━━━━

The "View all →" link beside "Recent Orders" must also be an actual navigation interaction.

When clicked, navigate to:

Orders

The Orders page should show the farmer's complete order history.

Include:

Order ID
Product
Quantity
Buyer/Order information where appropriate
Total
Status
Date
Actions

The dashboard should only show a small number of recent orders.

━━━━━━━━━━━━━━━━━━━━
6. PRODUCT IMAGES
━━━━━━━━━━━━━━━━━━━━

Replace the tiny emoji-style/product-icon images currently used for:

Tomato
Rice
Mango
and future produce.

Use high-quality REAL agricultural/produce photography instead.

Images should look like professional marketplace product photography.

Use high-resolution images with:

- clean composition
- natural lighting
- realistic produce
- minimal distracting backgrounds
- consistent visual style
- suitable cropping
- no cartoon illustrations
- no emojis
- no AI-looking illustrations

Use separate images for each produce item.

For example:

Tomato → high-quality fresh tomato photograph
Rice → high-quality rice/grain photograph
Mango → high-quality fresh mango photograph

Use legally usable/licensed stock photography where possible.

Prefer sources such as Unsplash or other reputable stock-image sources with appropriate usage rights. For example, Unsplash has high-resolution agricultural/produce photography available under its stated license. :contentReference[oaicite:1]{index=1}

Do NOT use a single collage image for multiple products.

━━━━━━━━━━━━━━━━━━━━
7. PRODUCT IMAGE SIZE AND FORMAT
━━━━━━━━━━━━━━━━━━━━

The current produce images are too small.

Use a proper image container approximately:

48px × 48px

for the compact dashboard table.

Images should:

- maintain their aspect ratio
- use object-fit: cover
- have a subtle 6–8px border radius
- remain clearly recognizable at a glance
- be vertically centered with the product name

Example:

[ Tomato image ]  Tomato
                  100 kg
                  ₹40/kg

Do not use tiny 16px emojis/icons as product representations.

On the full "My Produce" page, use larger product thumbnails/cards where appropriate.

━━━━━━━━━━━━━━━━━━━━
8. DASHBOARD TABLE BEHAVIOR
━━━━━━━━━━━━━━━━━━━━

Keep the dashboard compact.

"Your Produce" should show only a limited number of products.

"Recent Orders" should show only recent orders.

The dashboard is an overview, while:

"My Produce" = complete produce management

"Orders" = complete order history

"Shipments" = complete shipment information

Make the "View all →" actions visually obvious but still subtle.

━━━━━━━━━━━━━━━━━━━━
9. INTERACTION / PROTOTYPE BEHAVIOR
━━━━━━━━━━━━━━━━━━━━

Create Figma prototype interactions for:

Profile click
→ Open profile dropdown

Logout
→ Open logout confirmation modal

Your Produce → View all
→ Navigate to My Produce

Recent Orders → View all
→ Navigate to Orders

Sidebar → My Produce
→ Navigate to My Produce

Sidebar → Orders
→ Navigate to Orders

Sidebar → Profile
→ Open/show farmer profile

Sidebar → Dashboard
→ Return to Farmer Dashboard

Use realistic hover/active states for clickable elements.

━━━━━━━━━━━━━━━━━━━━
10. DO NOT CHANGE THE CORE DASHBOARD STRUCTURE
━━━━━━━━━━━━━━━━━━━━

Keep:

Greeting

4 statistic cards:

Total Produce
Orders Received
Revenue
Verification Status

Your Produce

Recent Orders

Keep the compact dashboard layout from the current design.

Do not add random analytics charts.

Do not add unnecessary AI features.

Do not add gradients.

Do not add glassmorphism.

Do not add oversized illustrations.

Do not add excessive animations.

The dashboard should feel like a real agricultural marketplace used by farmers every day.

FINAL GOAL:

The result should look like a polished, human-designed production application with:

#166534 as the main agricultural green,
#22C55E as the secondary accent,
professional produce photography,
functional navigation,
functional "View all" interactions,
and a useful farmer profile/logout menu.