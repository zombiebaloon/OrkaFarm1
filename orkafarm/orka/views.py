from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from django.core.mail import send_mail
from .utils import cookieCart, cartData, guestOrder


# Create your views here.
def index(request):
    return render(request,'index.html')

def aboutus(request):
    return render(request,'aboutus.html')

def contact(request):
    error = ''
    msg = ''
    if request.method == 'POST':
        message_name = request.POST['name']
        message_email = request.POST['email']
        s = request.POST['subject']
        message = request.POST['message']
        try:
            print('no error')
            send_mail(message_name,message,message_email,['zombiebaloon@gmail.com'],fail_silently=False)
            contactformemail.objects.create(email=message_email,name=message_name,message=message_email,subject=s)
            error = 'no'
            msg = message_name
        except:
            error ='yes'
    d = {'error':error,'msg':msg}
    return render(request, 'contact.html',d)

def farm(request):
    return render(request,'farm.html')

def productView(request,id):
    data = cartData(request)
    products = Product.objects.get(id=id)
    cartItems = data['cartItems']
    context = {'products':products,'cartItems':cartItems}
    return render(request,'productview.html',context)

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store.html',context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']


    context = {'items':items,"order":order,'cartItems':cartItems}
    return render(request,'cart.html',context)

def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    

    context = {'items':items,"order":order,'cartItems':cartItems}
    return render(request, 'checkout.html',context)    

def terms(request):
    return render(request,'terms.html')

def policy(request):
    return render(request,'policy.html')


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:',action)
    print('productId:',productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer,complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    print('dataaa',data)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)

    else:
        customer, order = guestOrder(request, data)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            # name = data['shipping']['name'],
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zip_code=data['shipping']['zipcode'],
            )
    return JsonResponse('Payment complete!', safe=False)

def Login(request):
    return render(request,'Login.html')


