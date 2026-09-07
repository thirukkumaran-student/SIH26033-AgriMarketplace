// Shared application data — single source of truth

export const FARMER = {
  name: 'Ravi Kumar',
  role: 'Farmer',
  email: 'ravi@example.com',
  phone: '+91 98765 43210',
  location: 'Chennai, Tamil Nadu',
  avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face',
  verified: true,
  verifiedOn: '01 Sep 2025',
  memberSince: 'January 2024',
}

export const PRODUCE_IMAGES = {
  'Tomato':          'https://images.unsplash.com/photo-1582284540020-8acbe03f4924?w=96&h=96&fit=crop',
  'Rice':            'https://images.unsplash.com/photo-1635562985686-4f8bb9c0d3bf?w=96&h=96&fit=crop',
  'Mango':           'https://images.unsplash.com/photo-1732472581875-89ff83f18439?w=96&h=96&fit=crop',
  'Wheat':           'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=96&h=96&fit=crop',
  'Onion':           'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=96&h=96&fit=crop',
  'Potato':          'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=96&h=96&fit=crop',
  'Tomato (Grade A)':'https://images.unsplash.com/photo-1582284540020-8acbe03f4924?w=96&h=96&fit=crop',
  'Basmati Rice':    'https://images.unsplash.com/photo-1635562985686-4f8bb9c0d3bf?w=96&h=96&fit=crop',
  'Alphonso Mango':  'https://images.unsplash.com/photo-1732472581875-89ff83f18439?w=96&h=96&fit=crop',
  'Tomatoes':        'https://images.unsplash.com/photo-1582284540020-8acbe03f4924?w=96&h=96&fit=crop',
  'Mangoes':         'https://images.unsplash.com/photo-1732472581875-89ff83f18439?w=96&h=96&fit=crop',
}

export const DEFAULT_IMG = 'https://images.unsplash.com/photo-1582284540020-8acbe03f4924?w=96&h=96&fit=crop'

export const PRODUCE_LIST = [
  { id: 1, name: 'Tomato',  category: 'Vegetables', qty: 100, unit: 'kg', price: 40,  status: 'Available',    updated: '05 Sep 2025' },
  { id: 2, name: 'Rice',    category: 'Grains',     qty: 500, unit: 'kg', price: 55,  status: 'Available',    updated: '04 Sep 2025' },
  { id: 3, name: 'Mango',   category: 'Fruits',     qty: 200, unit: 'kg', price: 90,  status: 'Low Stock',    updated: '03 Sep 2025' },
  { id: 4, name: 'Wheat',   category: 'Grains',     qty: 300, unit: 'kg', price: 42,  status: 'Available',    updated: '01 Sep 2025' },
  { id: 5, name: 'Onion',   category: 'Vegetables', qty: 150, unit: 'kg', price: 30,  status: 'Out of Stock', updated: '30 Aug 2025' },
  { id: 6, name: 'Potato',  category: 'Vegetables', qty: 400, unit: 'kg', price: 28,  status: 'Available',    updated: '28 Aug 2025' },
]

export const ORDERS_LIST = [
  { id: 'ORD1023', product: 'Tomatoes', buyer: 'Retail Buyer',  buyerEmail: 'contact@retailbuyer.com', buyerPhone: '+91 98765 43210', buyerAddress: 'Chennai, Tamil Nadu', qty: 50,  unit: 'kg', total: 2000,  status: 'Processing', date: '05 Sep 2025', placedTime: '10:00 AM', processedTime: '02:00 PM' },
  { id: 'ORD1021', product: 'Rice',     buyer: 'FreshMart',     buyerEmail: 'orders@freshmart.in',    buyerPhone: '+91 90000 12345', buyerAddress: 'Pune, Maharashtra',   qty: 100, unit: 'kg', total: 5500,  status: 'Shipped',    date: '04 Sep 2025', placedTime: '09:00 AM', processedTime: '11:00 AM' },
  { id: 'ORD1018', product: 'Mangoes',  buyer: 'Metro Foods',   buyerEmail: 'buy@metrofoods.com',     buyerPhone: '+91 88888 77777', buyerAddress: 'Bangalore, Karnataka',qty: 30,  unit: 'kg', total: 2700,  status: 'Delivered',  date: '03 Sep 2025', placedTime: '08:00 AM', processedTime: '10:00 AM' },
  { id: 'ORD1015', product: 'Wheat',    buyer: 'Local Store',   buyerEmail: 'info@localstore.com',    buyerPhone: '+91 87654 32100', buyerAddress: 'Hyderabad, Telangana',qty: 100, unit: 'kg', total: 4200,  status: 'Cancelled',  date: '02 Sep 2025', placedTime: '07:00 AM', processedTime: '—' },
  { id: 'ORD1012', product: 'Onion',    buyer: 'GreenKart',     buyerEmail: 'hello@greenkart.com',    buyerPhone: '+91 99999 00001', buyerAddress: 'Delhi, NCR',          qty: 40,  unit: 'kg', total: 1200,  status: 'Pending',    date: '01 Sep 2025', placedTime: '06:00 AM', processedTime: '—' },
]

export const SHIPMENTS_LIST = [
  { id: 'SHP1023', orderId: 'ORD1023', transporter: 'FastTrack Logistics', deliveryDate: '07 Sep 2025', status: 'In Transit', tracking: 'FT9876543210' },
  { id: 'SHP1021', orderId: 'ORD1021', transporter: 'BlueDart',            deliveryDate: '06 Sep 2025', status: 'Delivered',  tracking: 'BD1234567890' },
  { id: 'SHP1018', orderId: 'ORD1018', transporter: 'SafeMove',            deliveryDate: '04 Sep 2025', status: 'Delivered',  tracking: 'SM0011223344' },
  { id: 'SHP1015', orderId: 'ORD1015', transporter: '—',                   deliveryDate: '—',           status: 'Cancelled',  tracking: '—' },
]

export const DOCUMENTS = [
  { type: 'Aadhaar Card',         number: 'XXXX-XXXX-1234', submittedOn: '25 Aug 2025', status: 'Approved' },
  { type: 'Land Ownership Proof', number: 'TN-12-2020-5678',submittedOn: '26 Aug 2025', status: 'Approved' },
  { type: 'Bank Account Proof',   number: 'XXXX-5678',      submittedOn: '27 Aug 2025', status: 'Approved' },
]

export const CROP_CATEGORIES = ['All Categories', 'Vegetables', 'Grains', 'Fruits']
export const STATUS_OPTIONS   = ['All Status', 'Available', 'Low Stock', 'Out of Stock']
export const ORDER_STATUS_OPTIONS = ['All Status', 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
export const SHIPMENT_STATUS_OPTIONS = ['All Status', 'In Transit', 'Delivered', 'Cancelled', 'Preparing']

export const ORDER_STATUS_VARIANT = {
  Processing: 'warning',
  Shipped:    'brand',
  Delivered:  'success',
  Pending:    'secondary',
  Cancelled:  'danger',
}

export const PRODUCE_STATUS_VARIANT = {
  'Available':    'success',
  'Low Stock':    'warning',
  'Out of Stock': 'danger',
}

export const SHIPMENT_STATUS_VARIANT = {
  'In Transit': 'brand',
  'Delivered':  'success',
  'Cancelled':  'danger',
  'Preparing':  'secondary',
}

export const DOC_STATUS_VARIANT = {
  Approved: 'success',
  Pending:  'warning',
  Rejected: 'danger',
}

export const formatPrice = n => `₹${Number(n).toLocaleString('en-IN')}`

export const CROP_OPTIONS = CROP_CATEGORIES
