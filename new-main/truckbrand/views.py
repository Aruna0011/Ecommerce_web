from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from truckbrand.models import Contact, Product, Orders, OrderUpdate
from django.contrib import messages
from django.conf import settings
from math import ceil
import json
import requests
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction

# Import PayTM config
from .paytm_config import *
from paytmchecksum import PaytmChecksum
# Create your views here.
def index(request):
    allprods=[]
    catprods=Product.objects.values('category','id')
    print(catprods)
    cats={item['category'] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlides=n//4+ceil((n/4)-(n//4))
        allprods.append([prod,range(1,nSlides),nSlides])
        params={'allprods':allprods}
    return render(request,'index.html',params)

def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon... ")
        return render(request,"contact.html")

    return render(request,"contact.html")

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
@csrf_protect
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to proceed with checkout")
        return redirect('/cart/login')
    
    if request.method == 'POST':
        # Check if this is the initial form submission or payment submission
        if 'payment_method' in request.POST:
            # Process payment
            return process_payment(request)
        else:
            # Initial form submission - show order summary
            return show_order_summary(request)
    
    # GET request - show checkout form
    return render(request, 'checkout.html', {'request': request})

@require_http_methods(["POST"])
@csrf_protect
def show_order_summary(request):
    """Show order summary with payment options in one step"""
    print("\n=== SHOW_ORDER_SUMMARY VIEW STARTED ===")
    print(f"Request method: {request.method}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print("POST data:", request.POST)
    
    # Debug: Print session data
    print("Session data:", dict(request.session))
    
    try:
        # Get form data
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        amount = request.POST.get('amt', '0')
        items_json = request.POST.get('itemsJson', '{}')
        
        # Debug: Print form data
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Items JSON: {items_json}")
        
        # Prepare context
        context = {
            'shipping_address': {
                'name': name,
                'street_address': address1,
                'apartment': address2,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'phone': phone,
                'email': email,
            },
            'form_data': {
                'name': name,
                'email': email,
                'phone': phone,
                'address1': address1,
                'address2': address2,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'amount': amount,
                'itemsJson': items_json
            },
            'cart_items': items_json,
            'cart_items_json': items_json,  # Add this line
            'cart_total': amount,
        }
        
        # Store order data in session for payment processing
        request.session['order_data'] = context['form_data']
        
        # Debug: Print context before rendering
        print("Rendering template with context:", context)
        
        return render(request, 'order_summary.html', context)
        
    except Exception as e:
        print(f"Error in show_order_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, "An error occurred while processing your order. Please try again.")
        return redirect('checkout')
    
    # Log all headers for debugging
    print("\n--- Request Headers ---")
    for header, value in request.META.items():
        if header.startswith('HTTP_') or header in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            print(f"{header}: {value}")
    
    if not request.user.is_authenticated:
        print("User not authenticated, redirecting to login")
        messages.warning(request, "Please login to proceed with checkout")
        return redirect('/cart/login')
        
    try:
        # Get form data
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '').strip()
        amount_str = request.POST.get('amt', '0')
        email = request.POST.get('email', '').strip()
        address1 = request.POST.get('address1', '').strip()
        address2 = request.POST.get('address2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Debug: Print all received POST data
        print("\n--- Form Data ---")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Phone: {phone}")
        print(f"Address: {address1}, {address2}")
        print(f"City: {city}, State: {state}, ZIP: {zip_code}")
        print(f"Amount: {amount_str}")
        print(f"Items JSON: {items_json[:100]}..." if items_json else "No items in cart")
        
        # Debug: Print all form fields
        print("\n--- Form Field Values ---")
        for field in ['name', 'email', 'phone', 'address1', 'address2', 'city', 'state', 'zip_code', 'amt']:
            print(f"{field}: {request.POST.get(field, 'NOT PROVIDED')}")
            
        # Basic validation
        required_fields = {
            'Name': name,
            'Email': email,
            'Address': address1,
            'City': city,
            'State': state,
            'ZIP Code': zip_code,
            'Phone': phone
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            error_msg = f"Please fill in all required fields: {', '.join(missing_fields)}"
            print(f"\n--- VALIDATION FAILED ---")
            print(error_msg)
            messages.error(request, error_msg)
            return redirect('checkout')
            
        print("\n--- Form Validation Passed ---")
            
        try:
            amount = int(float(amount_str))
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
        except (ValueError, TypeError) as e:
            print(f"Invalid amount: {amount_str}, error: {str(e)}")
            messages.error(request, "Invalid order amount. Please try again.")
            return redirect('checkout')
        
        # Parse cart items for display
        try:
            cart_items = json.loads(items_json)
            if not isinstance(cart_items, dict) or not cart_items:
                raise ValueError("Invalid cart items")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing cart items: {str(e)}")
            messages.error(request, "Invalid cart items. Please try again.")
            return redirect('checkout')
        
        # Prepare context
        context = {
            'cart_items': cart_items,
            'cart_total': amount,
            'shipping_address': {
                'name': name,
                'street_address': address1,
                'apartment': address2,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'phone': phone,
                'email': email
            },
            'payment_methods': [
                {'id': 'cod', 'name': 'Cash on Delivery', 'description': 'Pay when you receive your order'},
                {'id': 'online', 'name': 'Online Payment', 'description': 'Pay securely with PayTM'}
            ],
            'form_data': {
                'itemsJson': items_json,
                'name': name,
                'email': email,
                'phone': phone,
                'address1': address1,
                'address2': address2,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'amount': amount
            }
        }
        
        # Store order data in session for payment processing
        request.session['order_data'] = context['form_data']
        
        try:
            return render(request, 'order_summary.html', context)
        except Exception as render_error:
            print(f"Error rendering template: {str(render_error)}")
            print(f"Template context: {context}")
            raise render_error
        
    except Exception as e:
        import traceback
        print("\n=== ERROR DETAILS ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nStack trace:")
        traceback.print_exc()
        print("==================\n")
        
        messages.error(request, "An error occurred while processing your order. Please try again.")
        return redirect('checkout')

@require_http_methods(["POST"])
def process_payment(request):
    """Process the payment based on selected method"""
    try:
        # Get payment method from form
        payment_method = request.POST.get('payment_method')
        
        # Get order data from form
        order_data = {
            'name': request.POST.get('name', ''),
            'email': request.POST.get('email', ''),
            'phone': request.POST.get('phone', ''),
            'address1': request.POST.get('address1', ''),
            'address2': request.POST.get('address2', ''),
            'city': request.POST.get('city', ''),
            'state': request.POST.get('state', ''),
            'zip_code': request.POST.get('zip_code', ''),
            'amount': float(request.POST.get('amount', 0)),
            'itemsJson': request.POST.get('itemsJson', '{}')
        }
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'address1', 'city', 'state', 'zip_code', 'amount']
        for field in required_fields:
            if not order_data.get(field):
                messages.error(request, f"Missing required field: {field}")
                return redirect('checkout')
        
        # Create order record
        with transaction.atomic():
            order = Orders.objects.create(
                items_json=order_data['itemsJson'],
                name=order_data['name'],
                amount=order_data['amount'],
                email=order_data['email'],
                address1=order_data['address1'],
                address2=order_data['address2'],
                city=order_data['city'],
                state=order_data['state'],
                zip_code=order_data['zip_code'],
                phone=order_data['phone'],
                paymentstatus='PENDING'
            )
            
            # Create initial order update
            OrderUpdate.objects.create(
                order_id=order.order_id,
                update_desc="Order placed. Payment pending.",
                delivered=False
            )
            
            # Process payment based on method
            if payment_method == 'COD':
                # For Cash on Delivery
                order.paymentstatus = 'COD'
                order.save()
                
                OrderUpdate.objects.create(
                    order_id=order.order_id,
                    update_desc="Order confirmed. Payment will be collected on delivery.",
                    delivered=False
                )
                
                # Clear cart after successful order placement
                if 'cart' in request.session:
                    del request.session['cart']
                
                # Store order ID in session for the success page
                request.session['order_id'] = str(order.order_id)
                
                return render(request, 'payment_success.html', {
                    'order': order,
                    'payment_method': 'Cash on Delivery',
                    'status': 'confirmed'
                })
                
            elif payment_method == 'online':
                # For PayTM Online Payment
                order.paymentstatus = 'PENDING'
                order.save()
                
                # Store order ID in session for callback verification
                request.session['order_id'] = str(order.order_id)
                
                # Prepare parameters for PayTM
                param_dict = {
                    'MID': PAYTM_MERCHANT_ID,
                    'ORDER_ID': str(order.order_id),
                    'CUST_ID': order.email,
                    'TXN_AMOUNT': str(order.amount),
                    'CHANNEL_ID': PAYTM_CHANNEL_ID,
                    'WEBSITE': PAYTM_WEBSITE,
                    'INDUSTRY_TYPE_ID': PAYTM_INDUSTRY_TYPE_ID,
                    'CALLBACK_URL': PAYTM_CALLBACK_URL,
                    'MOBILE_NO': order.phone,
                    'EMAIL': order.email,
                    'PAYMENT_MODE_ONLY': 'NO',
                    'AUTH_MODE': 'USRPWD',
                    'PAYMENT_TYPE_ID': 'PPI',
                }
                
                # Generate checksum
                paytm_params = {k: v for k, v in param_dict.items() if k != 'CHECKSUMHASH'}
                checksum = PaytmChecksum.generateSignature(paytm_params, PAYTM_MERCHANT_KEY)
                param_dict['CHECKSUMHASH'] = checksum
                
                # Store order ID in session for verification in callback
                request.session['order_id'] = order.order_id
                
                # Redirect to PayTM payment page
                return render(request, 'paytm.html', {
                    'param_dict': param_dict,
                    'payment_url': PAYTM_PAYMENT_GATEWAY_URL
                })
                order.save()
                
                # Prepare PayTM parameters
                param_dict = {
                    'MID': PAYTM_MERCHANT_ID,
                    'ORDER_ID': order_id,
                    'TXN_AMOUNT': str(order.amount),
                    'CUST_ID': order.email,
                    'INDUSTRY_TYPE_ID': PAYTM_INDUSTRY_TYPE_ID,
                    'WEBSITE': PAYTM_WEBSITE,
                    'CHANNEL_ID': PAYTM_CHANNEL_ID,
                    'CALLBACK_URL': PAYTM_CALLBACK_URL,
                }
                
                # Generate checksum using PaytmChecksum
                paytm_params = {k: v for k, v in param_dict.items() if k != 'CHECKSUMHASH'}
                checksum = PaytmChecksum.generateSignature(paytm_params, PAYTM_MERCHANT_KEY)
                param_dict['CHECKSUMHASH'] = checksum
                
                # Store order ID in session for verification in callback
                request.session['order_id'] = order_id
                
                # Redirect to PayTM payment page
                return render(request, 'paytm.html', {
                    'param_dict': param_dict,
                    'payment_url': PAYTM_PAYMENT_GATEWAY_URL
                })
            
            else:
                raise ValueError("Invalid payment method")
                
    except Exception as e:
        print(f"Error in process_payment: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}. Please try again.")
        return redirect('checkout')


@csrf_exempt
def handlerequest(request):
    """Handle PayTM payment callback"""
    if request.method != 'POST':
        return redirect('index')
    
    try:
        # Get form data
        response_dict = {}
        for key in request.POST:
            response_dict[key] = request.POST[key]
        
        # Get order ID from response
        order_id = response_dict.get('ORDERID')
        if not order_id:
            return HttpResponseBadRequest("Invalid order ID")
        
        # Get order from database
        try:
            order = Orders.objects.get(order_id=order_id)
        except Orders.DoesNotExist:
            return HttpResponseBadRequest("Order not found")
        
        # Verify checksum
        checksum = response_dict.get('CHECKSUMHASH', '')
        verify = False
        
        if checksum:
            paytm_params = {k: v for k, v in response_dict.items() if k != 'CHECKSUMHASH'}
            try:
                verify = PaytmChecksum.verifySignature(paytm_params, PAYTM_MERCHANT_KEY, checksum)
            except Exception as e:
                print(f"Error verifying checksum: {str(e)}")
                verify = False
        
        if not verify:
            # Log the failed checksum verification
            OrderUpdate.objects.create(
                order_id=order_id,
                update_desc=f"Payment failed: Invalid checksum. Response: {response_dict}",
                delivered=False
            )
            return HttpResponseBadRequest("Invalid checksum")

        # Verify transaction status
        if response_dict.get('RESPCODE') == '01':
            # Transaction successful
            order.paymentstatus = 'Paid'
            order.save()
            
            # Update order status
            OrderUpdate.objects.create(
                order_id=order.order_id,
                update_desc=f"Payment successful. Transaction ID: {response_dict.get('TXNID')}",
                delivered=False
            )
            
            # Clear cart
            if 'cart' in request.session:
                del request.session['cart']
            
            # Store order ID in session for the success page
            request.session['order_id'] = str(order.order_id)
            
            # Redirect to success page with order details
            return render(request, 'payment_success.html', {
                'order': order,
                'payment_method': 'Online Payment',
                'status': 'confirmed',
                'transaction_id': response_dict.get('TXNID')
            })
        else:
            # Transaction failed
            error_msg = response_dict.get('RESPMSG', 'Payment failed')
            
            # Update order status
            OrderUpdate.objects.create(
                order_id=order.order_id,
                update_desc=f"Payment failed: {error_msg}",
                delivered=False
            )
            
            # Store order ID in session for the failed page
            request.session['order_id'] = str(order.order_id)
            
            return render(request, 'payment_failed.html', {
                'order': order,
                'error': error_msg,
                'response': response_dict,
                'payment_method': 'Online Payment'
            })
            
    except Exception as e:
        import traceback
        print(f"Error in handlerequest: {str(e)}\n{traceback.format_exc()}")
        return HttpResponseBadRequest("An error occurred while processing your payment.")

def payment_success(request):
    """Handle successful payment and display order confirmation"""
    try:
        # Get order details from session or request
        order_id = request.GET.get('order_id') or request.session.get('order_id')
        if not order_id:
            messages.warning(request, "No order found. Please check your order history.")
            return redirect('profile')
            
        try:
            order = Orders.objects.get(order_id=order_id)
        except Orders.DoesNotExist:
            messages.error(request, "Order not found. Please contact support.")
            return redirect('profile')
            
        # Get order updates
        updates = OrderUpdate.objects.filter(order_id=order_id).order_by('-timestamp')
        
        # Clear order ID from session if it exists
        if 'order_id' in request.session:
            del request.session['order_id']
            
        # Clear cart if it exists
        if 'cart' in request.session:
            del request.session['cart']
        
        return render(request, 'payment_success.html', {
            'order': order,
            'updates': updates,
            'status': 'confirmed',
            'payment_method': order.paymentstatus,
            'transaction_id': request.GET.get('transaction_id')
        })
        
    except Exception as e:
        print(f"Error in payment_success: {str(e)}")
        messages.error(request, "An error occurred while retrieving your order details.")
        return redirect('index')

def about(request):
    return render(request,"about.html")

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to view your profile")
        return redirect('/cart/login')
    
    try:
        currentuser = request.user.email  # Using email instead of username for consistency
        items = Orders.objects.filter(email=currentuser).order_by('-order_date')
        
        # Get status for each order
        orders_with_status = []
        for order in items:
            try:
                status = OrderUpdate.objects.filter(order_id=order.order_id).order_by('-timestamp').first()
                orders_with_status.append({
                    'order': order,
                    'status': status.update_desc if status else 'Order Placed',
                    'timestamp': status.timestamp if status else order.order_date
                })
            except Exception as e:
                print(f"Error getting status for order {order.order_id}: {str(e)}")
                orders_with_status.append({
                    'order': order,
                    'status': 'Status not available',
                    'timestamp': order.order_date
                })
        
        context = {
            'orders': orders_with_status,
            'has_orders': len(orders_with_status) > 0
        }
        return render(request, 'profile.html', context)
        
    except Exception as e:
        print(f"Error in profile view: {str(e)}")
        messages.error(request, "An error occurred while loading your profile. Please try again.")
        return render(request, 'profile.html', {'orders': [], 'has_orders': False})
    return render(request,"profile.html",context)