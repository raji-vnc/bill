from urllib import request

from django.shortcuts import redirect, render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Bill, BillItem, Product
from .serializers import BillSerializer, BillItemSerializer, ProductSerializer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from rest_framework import status
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response(({
        "message":"Welcome to Billing API",
        "user":request.user.username
    }))
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product(request):

    customer_name = request.data.get("customer_name")
    product_data = request.data.get("product")

    if not customer_name:
        return Response({"error": "customer_name is required"}, status=400)

    if not product_data:
        return Response({"error": "product data is required"}, status=400)

    serializer = ProductSerializer(data=product_data)

    if serializer.is_valid():
        product = serializer.save()

        return Response({
            "status": "Product Created",
            "added_by": customer_name,
            "product": serializer.data
        }, status=201)

    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_bill(request):

    customer_name = request.data.get("customer_name")
    items_data = request.data.get("items")

    if not customer_name:
        return Response({"error": "customer_name is required"}, status=400)

    if not items_data or not isinstance(items_data, list):
        return Response({"error": "items must be a list"}, status=400)

    # STEP 1 — Create Bill
    bill = Bill.objects.create(
    customer_name=request.data['customer_name'],
    bill_no=f"BILL-{Bill.objects.count()+1}",
    phone=request.data.get("phone"),   # ✅ ADD THIS
    total=request.data['total'],
    total_price=request.data['total_price'],
    tax=request.data['tax'],
    gst=request.data['gst'],
    created_by=request.user.username
)

    total_amount = 0

   
    for item in items_data:
        product_id = item.get("product_id")  
        quantity = item.get("quantity")
        price = item.get("price")

        if product_id is None or quantity is None or price is None:
            bill.delete()
            return Response({"error": f"Invalid item: {item}"}, status=400)

        try:
            product = Product.objects.get(id=product_id)  

            BillItem.objects.create(
                bill=bill,
                product=product,
                quantity=quantity,
                price=price
            )

            total_amount += quantity * price

        except Product.DoesNotExist:
            bill.delete()
            return Response(
                {"error": f"Product '{product_id}' does not exist"},
                status=400
            )

    # STEP 3 — Update totals
    tax_amount = total_amount * 0.05   # 5% tax
    gst_amount = total_amount * 0.18   # 18% GST

    bill.total = total_amount
    bill.total_price = total_amount
    bill.tax = tax_amount
    bill.gst = gst_amount
    bill.save()


    serializer = BillSerializer(bill)
    return Response(serializer.data, status=201)

 
@api_view(["GET"])
def bill_detail(request, id):
    bill = get_object_or_404(Bill, id=id)
    serializer = BillSerializer(bill)
    return Response(serializer.data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    products = Product.objects.all()
    data = [{"id": p.id, "name": p.name, "price": p.price} for p in products]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_bill(request):

    customer_name = request.data.get("customer_name")
    items_data = request.data.get("items")
    created_by = request.user.username

    if not customer_name:
        return Response({"error": "customer_name is required"}, status=400)

    if not items_data or not isinstance(items_data, list):
        return Response({"error": "items must be a list"}, status=400)

    # ---- STEP 1: Create empty bill first ----
    bill = Bill.objects.create(
        customer_name=customer_name,
        phone=request.data.get("phone"),  # ✅ ADD PHONE
        created_by=created_by,
        bill_no=f"BILL-{Bill.objects.count() + 1}",
        total=0,
        total_price=0,
        tax=0,   # will be updated later
    gst=0,
         
    )

    total_amount = 0

    # ---- STEP 2: Add items and calculate total ----
    for item in items_data:

        product_id = item.get("product_id")
        quantity = item.get("quantity")
        price = item.get("price")

        if not product_id or not quantity or not price:
            return Response(
                {"error": "Each item must have product_id, quantity and price"},
                status=400
            )

        try:
            product = Product.objects.get(id=product_id)

            BillItem.objects.create(
                bill=bill,
                product=product,
                quantity=quantity,
                price=price
            )

            # 👉 IMPORTANT: calculate total here
            total_amount += quantity * price  

        except Product.DoesNotExist:
            return Response(
                {"error": f"Product with id {product_id} does not exist"},
                status=400
            )
        tax_rate = float(request.data.get("tax", 0))      # 0.5
        gst_rate = float(request.data.get("gst", 0))      # 0.5

    # ---- STEP 3: Update bill totals (MOST IMPORTANT) ----
    tax_amount = total_amount * (tax_rate / 100)
    gst_amount = total_amount * (gst_rate / 100)

    bill.total = total_amount
    bill.total_price = total_amount

    bill.tax = tax_amount      # ✅ SAVE AMOUNT, NOT RATE
    bill.gst = gst_amount      # ✅ SAVE AMOUNT, NOT RATE

    bill.save()

  # 👉 WITHOUT THIS, totals WILL REMAIN 0

    serializer = BillSerializer(bill)
    return Response(serializer.data, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bills(request):
    bills = Bill.objects.all()
    serializer = BillSerializer(bills, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_product(request,id):
    try:
        product=Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"error":"Product not found"},status=404)
    serializer=ProductSerializer(product,data=request.data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)    
    return Response(serializer.errors,status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, id):
    try:
        product = Product.objects.get(id=id)
        product.delete()
        return Response({"status": "Product Deleted"})
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_pdf(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id)
        items = BillItem.objects.filter(bill=bill)
    except Bill.DoesNotExist:
        return Response({"error": "Bill not found"}, status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{bill_id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "BILL INVOICE")

    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Bill ID: {bill.id}")
    p.drawString(50, 740, f"Customer: {bill.customer_name}")
    p.drawString(50, 720, f"Date: {bill.date}")
    p.drawString(50, 700, "-------------------------------------------")

    y = 680
    for item in items:
        line = f"{item.product.name} x {item.quantity} = {item.quantity * item.price}"
        p.drawString(50, y, line)
        y -= 20

    p.drawString(50, y-20, "-------------------------------------------")
    p.drawString(50, y-40, f"Total: {bill.total}")

    p.showPage()
    p.save()
    return response


@api_view(['POST'])
def  admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

   
    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Login successful",
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "dashboard_url": "/dashboard/"
    })

@api_view(['POST'])
def admin_logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@login_required
def dashboard(request):
    bills=Bill.objects.all().order_by('-id')[:10]
    return render(request, 'dashboard.html', {'bills': bills})

# End of src/bill/api/views.py

# start of frontend views.py
from django.shortcuts import render

def login_page(request):
    return render(request, 'login.html')
@login_required
def create_bill_page(request):
    return render(request, 'createbill.html')




