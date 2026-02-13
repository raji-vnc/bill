from django.db import models

class Product(models.Model):
    name=models.CharField(max_length=200)
    price=models.FloatField()
    stock=models.IntegerField()
    def __str__(self):
        return self.name



class Bill(models.Model):
    bill_no=models.CharField(max_length=100,blank=True,null=True)
    customer_name=models.CharField(max_length=200)
    total=models.FloatField(default=0.0)
    total_price=models.FloatField(default=0.0)
    tax = models.FloatField(default=0)
    gst = models.FloatField(default=0)
    phone=models.CharField(max_length=15,blank=True,null=True)
    item_name=models.CharField(max_length=200,blank=True,null=True)
    quantity=models.IntegerField(default=0)
    date=models.DateTimeField(auto_now_add=True)   
    created_by=models.CharField(max_length=200)

    def update_total(self):
        items = self.items.all()
        total = sum(item.quantity * item.price for item in items)
        tax=5
        gst=18
        tax=total*tax/100
        gst=total*gst/100
        self.total=total
        self.total_price=total
        self.tax=tax
        self.gst=gst

        self.save()

    

    @property
    def grand_total(self):
        return self.total + self.tax + self.gst
    def __str__(self):  
        return f"Bill {self.id} - {self.customer_name}"
    
class BillItem(models.Model):
    bill=models.ForeignKey(Bill,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    price=models.FloatField(default=0.0)
 
    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Bill {self.bill.id}"
    
class BillingSetting(models.Model):
    tax_rate=models.FloatField(default=0.0)
    gst_rate=models.FloatField(default=0.0)

    def __str__(self):
        return f"Billing Setting - Tax: {self.tax_rate}%, GST: {self.gst_rate}%"