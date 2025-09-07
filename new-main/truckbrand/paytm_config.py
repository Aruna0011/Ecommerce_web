import os
from django.conf import settings

# PayTM Configuration
# Merchant ID and other credentials
PAYTM_MERCHANT_ID = '7678143019@pthdfc'  # Updated merchant ID
PAYTM_MERCHANT_KEY = os.getenv('PAYTM_MERCHANT_KEY', 'YOUR_MERCHANT_KEY')
PAYTM_WEBSITE = os.getenv('PAYTM_WEBSITE', 'DEFAULT')
PAYTM_CHANNEL_ID = os.getenv('PAYTM_CHANNEL_ID', 'WEB')
PAYTM_INDUSTRY_TYPE_ID = os.getenv('PAYTM_INDUSTRY_TYPE_ID', 'Retail')

# Environment check
DEBUG = getattr(settings, 'DEBUG', True)

# Production URLs
PAYTM_PAYMENT_GATEWAY_URL = 'https://securegw.paytm.in/theia/processTransaction'
PAYTM_TRANSACTION_STATUS_URL = 'https://securegw.paytm.in/order/status'

# Callback URL
if DEBUG:
    PAYTM_CALLBACK_URL = 'https://yourdomain.com/handlerequest/'
else:
    PAYTM_CALLBACK_URL = 'https://yourdomain.com/handlerequest/'

# Transaction URL for checking status
PAYTM_TRANSACTION_URL = 'https://securegw.paytm.in/theia/processTransaction'
