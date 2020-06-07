from django.shortcuts import render
from django.http import HttpResponse
from shop.models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum

MERCHANT_KEY = 'SdQCIs94430859173152'

# Create your views here.
def index(request):
    # products = Product.objects.all()
    # product_details = Product.objects.all()
    # n = len(products)
    # n = len(product_details)
    # nSlide = n//4 + ceil((n/4)-(n//4))
    # params = {'no_of_slides':nSlide,'range':range(1,nSlide),'product_details':products}
    # allProds = [[product_details,range(1,nSlide),nSlide],
                # [product_details,range(1,nSlide),nSlide]]
    # print(allProds)
    # params = {'allProds' : allProds}
    allProds = []
    catProds = Product.objects.values('category','id')
    cats = { item['category'] for item in catProds }
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlide = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1,nSlide),nSlide])
    params = {'allProds' : allProds}
    return render(request,"shop/index.html",params)

def searchMatch(query,item):
    '''return true only if query matches the item'''
    if query in item.product_name.lower() or query in item.category.lower() or query in item.subcategory.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catProds = Product.objects.values('category','id')
    cats = { item['category'] for item in catProds }
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nSlide = n//4 + ceil((n/4)-(n//4))
        if len(prod) != 0:
            allProds.append([prod,range(1,nSlide),nSlide])
    params = {'allProds' : allProds}
    if len(allProds):
        pass
    return render(request,"shop/index.html",params)

def about(request):
    return render(request,"shop/about.html")

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        contact = Contact(name = name, email = email, phone = phone, desc = desc)
        contact.save()
    return render(request,"shop/contact.html")

def tracker(request):
    if request.method == 'POST':
        orderId = request.POST.get('orderId','')
        email = request.POST.get('email','')
        # return HttpResponse(f"{orderId} and {email}")
        try:
            order = Orders.objects.filter(order_id = orderId,email = email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id = orderId).order_by('-timestamp')
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc,'time':item.timestamp})
                    response = json.dumps([updates,order[0].item_json],default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    return render(request,"shop/tracker.html")



def productview(request,myid):
    # fetch the product using the id
    product = Product.objects.filter(id=myid)
    params = {'product':product[0]}
    return render(request,"shop/prodView.html",params)

def checkout(request):
    if request.method == 'POST':
        itemJson = request.POST.get('itemsJson','')
        amount = request.POST.get('amount','')
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        address = request.POST.get('address1','')
        address2 = request.POST.get('address2','')
        phone = request.POST.get('phone','')
        city = request.POST.get('city','')
        state = request.POST.get('state','')
        zip_code = request.POST.get('zip_code','')
        order = Orders(item_json = itemJson ,name = name, email = email,address=address,
        address2=address2, phone = phone, city=city,state=state,zip_code=zip_code,amount=amount)
        order.save()
        update = OrderUpdate(order_id = order.order_id,update_desc = "The order has been placed..")
        update.save()
        thank = True
        id = order.order_id
        # return render(request,"shop/checkout.html",{'thank':thank,'id':id})
        # Request paytm to transfer the amount to your account after payment by user.
        param_dict = {

                'MID': MERCHANT_KEY,
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request,'shop/paytm.html',{'param_dict':param_dict})    
    return render(request,"shop/checkout.html")

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here.
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    verify = Checksum.verify_checksum(response_dict,MERCHANT_KEY,checksum)
    if verify:
        if response_dict['RESPONSE'] == '01':
            print('Order successful')
        else:
            print('Order was not successful because' + response_dict['RESPMSG'])
    return render(request,'shop/paymentstatus.html',{'response':response_dict})

