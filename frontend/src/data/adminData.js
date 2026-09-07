export const ADMIN_CREDENTIALS = { email: 'admin@123', password: 'admin@123' }

export const ADMIN_STATS = {
  totalFarmers: { value: '1,248', change: '+12%', label: 'vs last month' },
  pendingVerification: { value: '24', change: '+9%', label: 'vs last week' },
  activeListings: { value: '3,482', change: '+19%', label: 'vs last month' },
  openDisputes: { value: '12', change: '+22%', label: 'vs last week' },
}

export const VERIFICATION_QUEUE = [
  { id: 'FRM1023', name: 'Ravi Kumar',  avatar: 'RK', submitted: '02 Sep 2025', docs: 3, status: 'Pending' },
  { id: 'FRM1045', name: 'Arun Kumar',  avatar: 'AK', submitted: '01 Sep 2025', docs: 2, status: 'Pending' },
  { id: 'FRM0982', name: 'Suresh',      avatar: 'S',  submitted: '31 Aug 2025', docs: 4, status: 'Pending' },
  { id: 'FRM1107', name: 'Priya Kumar', avatar: 'PK', submitted: '30 Aug 2025', docs: 3, status: 'Pending' },
]

export const ALL_VERIFICATIONS = [
  { id: 'FRM1023', name: 'Ravi Kumar',   avatar: 'RK', phone: '+91 98765 43210', email: 'ravi.kumar@email.com',   submitted: '02 Sep 2025', docs: 3, status: 'Pending',  district: 'Thanjavur' },
  { id: 'FRM1045', name: 'Arun Kumar',   avatar: 'AK', phone: '+91 87654 32109', email: 'arun.k@email.com',      submitted: '01 Sep 2025', docs: 2, status: 'Pending',  district: 'Chennai'   },
  { id: 'FRM0982', name: 'Suresh',       avatar: 'S',  phone: '+91 76543 21098', email: 'suresh@email.com',      submitted: '31 Aug 2025', docs: 4, status: 'Approved', district: 'Madurai'   },
  { id: 'FRM1107', name: 'Priya Kumar',  avatar: 'PK', phone: '+91 65432 10987', email: 'priya.k@email.com',     submitted: '30 Aug 2025', docs: 3, status: 'Rejected', district: 'Coimbatore'},
  { id: 'FRM1009', name: 'Manoj Singh',  avatar: 'MS', phone: '+91 98760 11223', email: 'manoj.s@email.com',     submitted: '28 Aug 2025', docs: 3, status: 'Pending',  district: 'Salem'     },
  { id: 'FRM1076', name: 'Lakshmi Devi', avatar: 'LD', phone: '+91 91234 56789', email: 'lakshmi.d@email.com',   submitted: '25 Aug 2025', docs: 2, status: 'Approved', district: 'Trichy'    },
  { id: 'FRM1061', name: 'Karthik R',    avatar: 'KR', phone: '+91 99876 66554', email: 'karthik.r@email.com',   submitted: '23 Aug 2025', docs: 3, status: 'Pending',  district: 'Vellore'   },
  { id: 'FRM1054', name: 'Selvam',       avatar: 'S2', phone: '+91 88776 55443', email: 'selvam.farm@email.com', submitted: '21 Aug 2025', docs: 4, status: 'Approved', district: 'Tirunelveli'},
]

export const FARMER_DETAIL = {
  id: 'FRM1023', name: 'Ravi Kumar', avatar: 'RK',
  phone: '+91 98765 43210', email: 'ravi.kumar@email.com',
  location: 'Thanjavur, Tamil Nadu', farmSize: '5 acres',
  primaryCrops: 'Rice, Groundnut', memberSince: '02 Sep 2025',
  status: 'Pending Review', submittedAt: '02 Sep 2025, 10:24 AM',
  notes: 'Please verify the land document and bank details.',
  documents: [
    { name: 'Aadhaar / ID Proof', file: 'aadhaar_ravi.pdf' },
    { name: 'Land Document',      file: 'land_doc.pdf'     },
    { name: 'Bank Details',       file: 'bank_passbook.pdf'},
  ],
}

export const OPEN_DISPUTES = [
  { id: 'DSP1023', issue: 'Damaged Tomatoes',   priority: 'High',   status: 'Open'         },
  { id: 'DSP1021', issue: 'Quantity Mismatch',  priority: 'Medium', status: 'Under Review' },
  { id: 'DSP1018', issue: 'Payment Issue',      priority: 'Low',    status: 'Open'         },
]

export const ALL_DISPUTES = [
  { id: 'DSP1023', orderId: 'ORD1042', raisedBy: 'Consumer', issue: 'Damaged Tomatoes',   priority: 'High',   status: 'Open'         },
  { id: 'DSP1038', orderId: 'ORD1038', raisedBy: 'Consumer', issue: 'Quantity Mismatch',  priority: 'Medium', status: 'Under Review' },
  { id: 'DSP1018', orderId: 'ORD1032', raisedBy: 'Consumer', issue: 'Payment Issue',      priority: 'Low',    status: 'Resolved'     },
  { id: 'DSP1015', orderId: 'ORD1021', raisedBy: 'Consumer', issue: 'Wrong Product',      priority: 'Medium', status: 'Open'         },
  { id: 'DSP1012', orderId: 'ORD1018', raisedBy: 'Farmer',   issue: 'Delayed Payment',    priority: 'Low',    status: 'Resolved'     },
  { id: 'DSP1010', orderId: 'ORD1007', raisedBy: 'Consumer', issue: 'Product Quality',    priority: 'High',   status: 'Under Review' },
  { id: 'DSP1008', orderId: 'ORD0998', raisedBy: 'Farmer',   issue: 'Cancellation Request',priority: 'Low',  status: 'Resolved'     },
]

export const DISPUTE_DETAIL = {
  id: 'DSP1023', orderId: 'ORD1042', priority: 'High', status: 'Open',
  raisedOn: '02 Sep 2025, 11:30 AM',
  consumer: { name: 'Ananya Sharma', phone: '+91 88165 11223', email: 'ananya.s@email.com' },
  farmer:   { name: 'Ravi Kumar',    phone: '+91 98765 43210', email: 'ravi.kumar@email.com' },
  issueType: 'Damaged Tomatoes',
  description: 'The tomatoes received were damaged and not fit for consumption. Around 40% of this produce was spoiled.',
  order: { product: 'Tomatoes (Organic)', qty: '50 kg', orderDate: '30 Aug 2025', deliveryDate: '01 Sep 2025', deliveryAddr: 'Chennai, Tamil Nadu', payment: 'UPI', orderStatus: 'Delivered', total: '₹1,250' },
}

export const RECENT_ACTIVITY = [
  { text: 'Farmer Ravi Kumar submitted verification', time: '5 min ago',  color: '#166534' },
  { text: 'New dispute #DSP1023 raised',              time: '18 min ago', color: '#dc2626' },
  { text: '12 new produce listings added',            time: '32 min ago', color: '#2563eb' },
  { text: 'Order #ORD1042 shipped',                   time: '45 min ago', color: '#166534' },
  { text: 'Farmer Suresh verified',                   time: '1 hour ago', color: '#166534' },
]

export const MONITORING_STATS = [
  { label: 'Farmers',    value: '1,248', color: '#166534', bg: '#dcfce7' },
  { label: 'Consumers',  value: '3,542', color: '#2563eb', bg: '#dbeafe' },
  { label: 'Bulk Buyers',value: '320',   color: '#7c3aed', bg: '#ede9fe' },
  { label: 'Financiers', value: '48',    color: '#d97706', bg: '#fef3c7' },
  { label: 'Logistics',  value: '76',    color: '#0891b2', bg: '#cffafe' },
]

export const USERS_LIST = [
  { name: 'Ravi Kumar',     role: 'Farmer',    contact: '+91 98765 43210', status: 'Verified', joined: '02 Sep 2025' },
  { name: 'Ananya Sharma',  role: 'Consumer',  contact: '+91 88165 11223', status: 'Active',   joined: '15 Aug 2025' },
  { name: 'Gibtel Foods Ltd',role: 'Bulk Buyer',contact: '+91 99987 66654', status: 'Active',   joined: '12 Aug 2025' },
  { name: 'Karthik R',      role: 'Financier', contact: '+91 88776 55443', status: 'Active',   joined: '10 Aug 2025' },
  { name: 'FastTrack Logistics',role: 'Logistics',contact: '+91 77845 44322',status: 'Active', joined: '08 Aug 2025' },
]

export const PRODUCE_LISTINGS = [
  { product: 'Tomatoes', farmer: 'Ravi Kumar',  qty: '500 kg', price: '₹25/kg', status: 'Active'  },
  { product: 'Rice (Pon 1)', farmer: 'Suresh',  qty: '1,000 kg',price: '₹40/kg',status: 'Active'  },
  { product: 'Groundnut', farmer: 'Arun Kumar', qty: '300 kg', price: '₹60/kg', status: 'Pending' },
  { product: 'Mango',    farmer: 'Priya Kumar', qty: '200 kg', price: '₹80/kg', status: 'Active'  },
  { product: 'Banana',   farmer: 'Selvam',      qty: '400 kg', price: '₹30/kg', status: 'Active'  },
]
