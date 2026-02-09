from rest_framework import serializers
from .models import Bill, BillItem, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'

class BillItemSerializer(serializers.ModelSerializer):
    product=ProductSerializer()
    class Meta:
        model=BillItem
        fields='__all__'

class BillSerializer(serializers.ModelSerializer):
    items=BillItemSerializer(many=True,read_only=True)
    class Meta:
        model=Bill
        fields='__all__'