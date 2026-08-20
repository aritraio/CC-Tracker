"""
Realistic sample statement texts representing various Indian credit card issuers.
Used for deterministic testing and fixture generation.
"""

HDFC_SAMPLE_TEXT = """HDFC BANK
Credit Card Statement
Card No: 4524 XXXX XXXX 1234
Statement Period : 16/03/2024 to 15/04/2024
Statement Date : 15/04/2024
Payment Due Date : 05/05/2024
Total Amount Due : 45,230.50
Minimum Amount Due : 2,300.00
Credit Limit : 3,00,000.00
Available Credit Limit : 2,54,769.50
Opening Balance : 0.00
Total Debits : 45,230.50
Total Credits : 0.00

Date Transaction Description Amount (in Rs.)
16/03/2024 SWIGGY BANGALORE IN 549.00
18/03/2024 BLINKIT COMMERCE GURGAON 1,240.50
22/03/2024 AMAZON SELLER SERVICES MUMBAI 3,499.00
25/03/2024 NETFLIX ENTERTAINMENT SERVICES 649.00
01/04/2024 HPCL AUTO FUELS BANGALORE 2,500.00
04/04/2024 ANNUAL MEMBERSHIP FEE 1,500.00
04/04/2024 IGST-DB@18.00% 270.00
10/04/2024 ZOMATO RESTAURANTS NEW DELHI 820.00
12/04/2024 UBER INDIA SYSTEMS MUMBAI 403.00
14/04/2024 APPLE SERVICES RETAIL 33,800.00
"""

HDFC_SAMPLE_WITH_PAYMENTS = """HDFC BANK
Card No: 4524 XXXX XXXX 5678
Statement Date : 15/04/2024
Payment Due Date : 05/05/2024
Total Amount Due : 8,450.00
Minimum Amount Due : 500.00
Credit Limit : 2,00,000.00
Available Credit Limit : 1,91,550.00
Opening Balance : 12,500.00
Total Debits : 8,450.00
Total Credits : 12,500.00

Date Transaction Description Amount (in Rs.)
17/03/2024 AUTOPAY PAYMENT RECEIVED - THANK YOU 12,500.00 Cr
20/03/2024 ZEPTO QUICK COMMERCE 450.00
25/03/2024 SPOTIFY INDIA SUBSCRIPTION 119.00
02/04/2024 RELIANCE DIGITAL RETAIL 7,881.00
"""

ICICI_SAMPLE_TEXT = """ICICI BANK LIMITED
Statement of Card Account
Card No: 4375 12XX XXXX 4321
Statement Period : From 21/03/2024 to 20/04/2024
Statement Date : 20/04/2024
Payment Due Date : 10/05/2024
Total Amount Due : ₹ 32,450.00
Minimum Amount Due : ₹ 1,650.00
Credit Limit : ₹ 4,50,000.00
Available Credit Limit : ₹ 4,17,550.00
Opening Balance : ₹ 0.00
Total Debits : ₹ 32,450.00
Total Credits : ₹ 0.00

Transaction Details
Date Ref No Details Amount (INR)
22/03/2024 10928374 SWIGGY FOOD DELIVERY BANGALORE 680.00 DR
26/03/2024 10928375 AMAZON INDIA PAYMENTS 12,999.00 DR
30/03/2024 10928376 MAKEMYTRIP TRAVEL GURGAON 14,500.00 DR
05/04/2024 10928377 STARBUCKS COFFEE KORAMANGALA 750.00 DR
10/04/2024 10928378 BLINKIT COMMERCE 1,521.00 DR
15/04/2024 10928379 BOOKMYSHOW TICKETS MUMBAI 2,000.00 DR

ICICI Bank Reward Points Summary
Opening Points: 1,200 Points Earned: 450 Points Redeemed: 0 Closing Points: 1,650
"""

SBI_SAMPLE_TEXT = """SBI Cards and Payment Services Limited
SBI Card Statement
Card No: 4129 XXXX XXXX 9876
Statement Period : From 13/03/2024 to 12/04/2024
Statement Date : 12 Apr 2024
Payment Due Date : 02 May 2024
Total Amount Due : Rs. 28,950.00
Minimum Amount Due : Rs. 1,450.00
Credit Limit : Rs. 2,00,000.00
Available Credit Limit : Rs. 1,71,050.00
Previous Balance : Rs. 0.00
Total Debits : Rs. 28,950.00
Total Credits : Rs. 0.00

Date Transaction Details Type Amount (in Rs.)
15 Mar 2024 ZOMATO ORDER ONLINE D 890.00
18 Mar 2024 FLIPKART INTERNET BANGALORE D 18,490.00
24 Mar 2024 CULT FIT HEALTHCARE BANGALORE D 6,990.00
29 Mar 2024 UBER TRIP BANGALORE D 380.00
05 Apr 2024 SHELL PETROL PUMP WHITEFIELD D 2,200.00

Reward Summary
Opening Balance: 4000 Points Earned: 580 Closing Balance: 4580
"""

AXIS_SAMPLE_TEXT = """AXIS BANK
Summary of Card Account
Axis Bank Credit Card
Card No: 5241 XXXX XXXX 7890
Statement Period : 18/03/2024 to 17/04/2024
Statement Date : 17/04/2024
Payment Due Date : 07/05/2024
Total Amount Due : ₹ 24,150.00
Minimum Amount Due : ₹ 1,210.00
Total Credit Limit : ₹ 3,50,000.00
Available Credit Limit : ₹ 3,25,850.00
Opening Balance : ₹ 0.00
Total Debits : ₹ 24,150.00
Total Credits : ₹ 0.00

Transaction Details
Date Particulars Amount (INR)
20/03/2024 MYNTRA DESIGNS BANGALORE 4,200.00 DR
24/03/2024 DMART READY MUMBAI 3,850.00 DR
28/03/2024 TATA CLIC SHOPPING 12,500.00 DR
02/04/2024 AIRTEL BROADBAND BILLPAY 1,180.00 DR
10/04/2024 CHAIPOS RESTAURANTS 2,420.00 DR

EDGE REWARDS Points Summary
Opening: 2500 Earned: 480 Redeemed: 0 Closing: 2980
"""

AMEX_SAMPLE_TEXT = """American Express Banking Corp.
Membership Rewards Credit Card Statement
Card No: 3759 XXXXXX 1234
Statement Period : From 01/04/2024 to 30/04/2024
Statement Date : 30/04/2024
Payment Due Date : 18/05/2024
Total Amount Due : Rs. 64,800.00
Minimum Amount Due : Rs. 3,240.00
Credit Limit : Rs. 5,00,000.00
Available Credit Limit : Rs. 4,35,200.00
Previous Balance : Rs. 0.00
Total Debits : Rs. 64,800.00
Total Credits : Rs. 0.00

Transactions Date Details Amount (INR)
02/04/2024 TAJ HOTELS RESORTS MUMBAI 42,000.00
08/04/2024 INDIGO AIRLINES GURGAON 14,500.00
14/04/2024 STARBUCKS INDIA 1,300.00
20/04/2024 CROMA ELECTRONICS BANGALORE 7,000.00

Membership Rewards Summary
Opening Balance: 15,000 Earned: 1,296 New Balance: 16,296
"""
