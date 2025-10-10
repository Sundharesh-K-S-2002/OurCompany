from django.shortcuts import render, redirect
from .models import reg
from .forms import *
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.http import HttpResponseBadRequest
import json

def register_page(request):
    data = {
        'form': RegistrationForm()
    }
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')

    return render(request, 'register.html', data)

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = reg.objects.get(username=username, password=password)
            if user:
                return redirect('home')
        except reg.DoesNotExist:
            return render(request, 'index.html', {'error': 'Invalid credentials'})
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

def add_product(request):
    data1 = {
        'product': productForm()
    }
    if request.method == 'POST':
        product = productForm(request.POST, request.FILES)
        print(request.POST)
        if product.is_valid():
            product.save()
            product = productForm()
    else:
        product = productForm()

    return render(request,'add_product.html', data1)


def order(request):
    datas = {
         'products': Products.objects.all()
    }

    return render(request, 'orders.html',datas)


def calculate_total(request):
    if request.method == 'POST':
        total_price = 0
        product_ids = request.POST.getlist('product_ids')
        cart = []

        for pid in product_ids:
            try:
                count = int(request.POST.get(f'count_{pid}', 0))
                if count > 0:
                    product = Products.objects.get(id=pid)
                    subtotal = product.price * count
                    total_price += subtotal
                    cart.append({
                        'product': product,
                        'count': count,
                        'subtotal': subtotal
                    })
            except Products.DoesNotExist:
                continue

        # Save total_price in session for payment view
        request.session['total_price'] = total_price

        return render(request, 'cart_summary.html', {
            'cart': cart,
            'total_price': total_price,
            'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
        })

    # On GET, just show cart or redirect to cart page but NOT payment
    return render(request, 'cart_summary.html')  # or your cart page


    # return render(request, 'error.html', {'message': 'Invalid request'})

# def create_order(request):
#     if request.method == "POST":
#         import json
#         data = json.loads(request.body)  
#         amount = int(float(data['amount']) * 100)  

#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         order = client.order.create({
#             "amount": amount,
#             "currency": "INR",
#             "payment_capture": 1
#         })
#         return JsonResponse(order)


# @csrf_exempt
# def create_order(request):
#     if request.method == "POST":
#         import json
#         data = json.loads(request.body)
#         amount = int(float(data['amount']))  # Already in paise from frontend

#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         order = client.order.create({
#             "amount": amount,
#             "currency": "INR",
#             "payment_capture": 1
#         })
#         return JsonResponse(order)

# @csrf_exempt
# def create_order(request):
#     if request.method == "POST":
#         import json
#         data = json.loads(request.body)
#         amount = data.get('amount')

#         razorpay_order = razorpay_client.order.create({
#             "amount": amount,
#             "currency": "INR",
#             "payment_capture": 1
#         })

#         return JsonResponse(razorpay_order)


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# def payment(request):
#     """
#     Show the payment page with Razorpay payment button.
#     """
#     amount = 50000  
#     currency = 'INR'

#     razorpay_order = razorpay_client.order.create({
#         "amount": amount,
#         "currency": currency,
#         "payment_capture": 1
#     })

#     razorpay_order_id = razorpay_order['id']
#     callback_url = '/razorpay/'

#     context = {
#         'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#         'order_id': razorpay_order_id,
#         'amount': amount,
#         'callback_url': callback_url,
#     }

#     return render(request, 'payment.html', context)

# @csrf_exempt
# def create_order(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         amount = data.get("amount")
#         currency = "INR"
#         razorpay_order = razorpay_client.order.create({
#             "amount": amount,
#             "currency": currency,
#             "payment_capture": 1,
#         })
#         return JsonResponse(razorpay_order)
#     return JsonResponse({"error": "Invalid method"}, status=400)
@csrf_exempt
def create_order(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        amount = int(float(data.get("amount")) * 100)  # Convert rupees to paise
        currency = "INR"
        razorpay_order = razorpay_client.order.create({
            "amount": amount,
            "currency": currency,
            "payment_capture": 1,
        })
        Order.objects.create(
            razorpay_order_id=razorpay_order["id"],
            amount=float(data.get("amount")),
            status='created'
        )
        return JsonResponse({
            "id": razorpay_order["id"],
            "amount": razorpay_order["amount"]
        })
    return JsonResponse({"error": "Invalid method"}, status=400)


def payment(request):
    """
    Show the payment page with Razorpay payment button.
    """
    total_price = request.session.get('total_price')

    if not total_price:
        return redirect('calculate_total')  # fallback if total is missing

    amount = float(total_price) # ₹ to paise
    currency = 'INR'

    razorpay_order = razorpay_client.order.create({
        "amount": amount,
        "currency": currency,
        "payment_capture": 1
    })

    context = {
    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    'order_id': razorpay_order['id'],
    'amount': amount,  # in paise
    'amount_rupees': total_price,  # in rupees
    'callback_url': '/razorpay/',
}

    return render(request, 'home.html', context)




# @csrf_exempt
# def razorpay_payment(request):
#     """
#     Handle the payment success/failure callback from Razorpay.
#     """
#     if request.method == "POST":
#         try:
#             params_dict = {
#                 'razorpay_order_id': request.POST.get('razorpay_order_id'),
#                 'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
#                 'razorpay_signature': request.POST.get('razorpay_signature')
#             }

#             result = razorpay_client.utility.verify_payment_signature(params_dict)

#             if result is None:
#                 return redirect('success')
#             else:
#                 return redirect('error')

#         except:
#             return redirect('error')
#     else:
#         return HttpResponseBadRequest("Invalid request")

@csrf_exempt
def razorpay_payment(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)

        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            order = Order.objects.get(razorpay_order_id=params_dict['razorpay_order_id'])
            order.razorpay_payment_id = params_dict['razorpay_payment_id']
            order.razorpay_signature = params_dict['razorpay_signature']
            order.status = 'paid'
            order.save()
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'error'})


def success(request):
    return render(request, 'payment_success.html')

def error(request):
    return render(request, 'error.html')
   