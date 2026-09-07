IMPORTANT: Treat this Figma project as a complete, connected web application prototype — NOT as a collection of separate static UI screens.

I will be creating multiple pages for AgriConnect, an agricultural marketplace platform.

Every screen you create must be designed with modularity, reusable components, and working prototype connectivity in mind.

1. MULTI-PAGE ARCHITECTURE

Do not build every page as one giant frame or one monolithic design.

Organize the Figma file into logical pages/sections:

Shared Components

Sidebar
Top navigation/header
Profile dropdown
Buttons
Inputs
Search bars
Dropdowns
Modal dialogs
Status badges
Tables
Cards
Product cards
Product image components
Pagination
Toast/success/error messages
Empty states
Loading states

Farmer

Farmer Dashboard
My Produce
Add/Edit Produce
Orders
Order Details
Verification
Shipments
Forecasts
Profile
Settings

Consumer

Consumer Dashboard
Marketplace
Product Details
Cart/Checkout
Orders
Order Details
Shipment Tracking
Disputes

Admin

Admin Dashboard
Farmer Verification
Disputes
Monitoring

Create these as separate frames/pages where appropriate, with clear naming.

Do NOT duplicate the same sidebar/header/profile components independently on every page. Create reusable components and use instances.

2. SHARED DESIGN SYSTEM

Use one consistent AgriConnect design system across the entire application.

Colors

Primary: #166534
Secondary: #22C55E
Background: #F8FAFB
Text: #17201A
Border: #E5E7EB
Warning: #F59E0B
Error: #DC2626
Success: #16A34A

Typography

Font: Inter
H1: 32px Bold
H2: 24px Semibold
H3: 20px Semibold
Body: 16px Regular
Small: 14px Regular

Use reusable color/text styles or variables wherever possible.

Do not introduce random shades of green.

Avoid:

Neon green
Excessive gradients
Glassmorphism
Huge rounded cards
Excessive shadows
Generic AI-generated dashboard layouts
Unnecessary decorative graphics

The design should feel like a real premium agricultural marketplace product.

3. REUSABLE COMPONENTS

Build reusable components rather than recreating UI elements.

For example:

Button component

Primary
Secondary
Danger
Text
Disabled
Hover
Pressed

Status Badge component

Pending
Processing
Shipped
Delivered
Cancelled
Available
Low Stock
Out of Stock

Modal component

Default
Confirmation
Success
Error

Table component

Header
Row
Hover state
Empty state

Product Image component

Small
Medium
Large

Use component variants and interactive components wherever appropriate instead of creating duplicate versions. Figma interactive components should be used for reusable UI states.

4. EVERY BUTTON MUST WORK

Do not leave decorative or dead buttons.

Every visible button, link, icon button, menu item, tab, dropdown, filter, search control and navigation item must have a meaningful interaction.

If an interaction belongs to another page:

CREATE THE REQUIRED PAGE AND CONNECT IT.

Do not simply make the button look clickable.

Examples:

View all → → navigate to the corresponding full page.

Add Produce → open Add Produce form/modal.

Edit → open Edit Produce form.

Delete → open Delete confirmation.

Orders → navigate to Orders.

Order ID → navigate to Order Details.

Track Shipment → navigate to Shipment Tracking.

Profile → open Profile or profile dropdown.

Logout → confirmation modal → logout state.

Back → return to the previous relevant screen.

Cancel → close modal/form and return to previous state.

Save → show success state and return/update the relevant page.

If a button logically requires a page that has not been designed yet, create a placeholder version of that page with the correct shared layout and connect it now. It can be improved later.

Never leave an interaction disconnected just because the destination page hasn't been fully designed yet.

5. PAGE CONNECTIVITY

Think about the application as a navigation graph:

Login
↓
Role-based Dashboard

Farmer:

Dashboard
↔ My Produce
↔ Orders
↔ Order Details
↔ Shipments
↔ Verification
↔ Forecasts
↔ Profile
↔ Settings

Consumer:

Dashboard
↔ Marketplace
↔ Product Details
↔ Cart/Checkout
↔ Orders
↔ Order Details
↔ Shipment Tracking
↔ Disputes

Admin:

Dashboard
↔ Farmer Verification
↔ Disputes
↔ Monitoring

Navigation should feel like a real web application.

Use Navigate to for page-level navigation and overlays for dropdowns, confirmations and modal interactions. Figma supports both navigation and overlays specifically for these prototype flows.

6. SIDEBAR MUST BE SHARED

The Farmer sidebar should be one reusable component:

Dashboard
My Produce
Orders
Verification
Shipments
Forecasts
Profile
Settings

The active page should automatically have the correct active state.

Example:

On Dashboard → Dashboard active.

On My Produce → My Produce active.

On Orders → Orders active.

Do not redesign the sidebar separately for every page.

7. PROFILE MUST BE SHARED

Clicking the profile/avatar/name anywhere in the Farmer application should open the same reusable profile dropdown.

Show:

Ravi Kumar
Farmer

Email: ravi@example.com
Phone: +91 XXXXX XXXXX

Profile

Logout

Logout should open:

Are you sure you want to logout?

Cancel | Logout

Reuse this component across all Farmer pages.

8. INTERACTION STATES

Do not only design the default state.

Important interactive components should have:

Default
Hover
Active
Pressed
Disabled
Loading
Success
Error
Empty

For example, Add Produce should have:

Default → Loading → Success / Error.

Use Figma variables and conditional interactions where useful to avoid unnecessarily duplicating frames. Figma supports variables, multiple actions and conditional logic for more dynamic prototypes.

9. FORMS MUST BE FUNCTIONAL

Forms should not be purely visual.

Include realistic prototype states for:

Empty
Filled
Validation error
Loading
Successful submission

Example:

Add Produce
→ user fills form
→ clicks Add Produce
→ loading state
→ success message
→ produce appears in My Produce

Where Figma's prototype capabilities allow, use variables/conditional logic to simulate state changes instead of creating unnecessary duplicate screens.

10. SEARCH AND FILTERS

Search bars and filters must have visible interaction states.

Example:

Search → filtered result state.

Status filter → Available / Low Stock / Out of Stock.

Dropdown → opens options.

Selected filter → visually reflected.

Clear filter → returns to All.

Use variables where useful for simulating dynamic UI state.

11. DATA CONSISTENCY

Keep the same example data across connected screens.

Example:

If Dashboard shows:

Tomato — 100 kg — ₹40/kg

My Produce should show the same product.

Product Details should show the same product.

Orders should reference the same product where applicable.

Do not randomly change product names, prices or quantities between screens.

12. MODULARITY RULE

IMPORTANT: Do not build the entire application into one giant frame.

Keep:

Shared Components

separate from:

Page Frames

and keep each page logically independent.

This is important because more pages will be added later and existing components should be reusable without rebuilding them.

When a new page needs a component that already exists, reuse the existing component instead of creating another copy.

13. PROTOTYPE QUALITY CHECK

Before considering each screen complete, check:

Does every button do something?
Does every navigation item go somewhere?
Do View All links work?
Do Back buttons work?
Do modals open and close?
Do dropdowns open and close?
Does Profile work?
Does Logout work?
Do forms have success/error states?
Do filters have interaction states?
Are pages connected to the correct destinations?
Are shared components actually reused?
Is the active sidebar state correct?
Are there any dead clickable elements?

If something is intended to be clickable, it must have a prototype interaction.

14. CURRENT PAGE

Now create the requested page using the above architecture.

Do not redesign the entire application again.

Reuse all existing AgriConnect components and connect this page to the existing pages.

If a required destination page doesn't exist yet, create a minimal connected placeholder using the same design system so that the interaction works.

Prioritize:

Functionality → Connectivity → Reusability → Visual polish.

The result should feel like one cohesive, production-quality web application rather than separate AI-generated screens.