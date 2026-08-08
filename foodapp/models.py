from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class CustomUser(AbstractUser):
    ROLES = [
        ("manager","Manager"),
        ("customer","Customer"),
        ("admin","Admin")
    ]
    id = models.UUIDField(primary_key=True,unique=True,editable=True)
    role = models.CharField(max_length=50,choices=ROLES,default="customer")
    phone_number = models.CharField(max_length=30,blank=True,null=True)

    def save(self, *args, **kwargs):
        if self.is_superuser == True:
            self.role = "admin"
        return super().save(*args, **kwargs)


class Resturant(models.Model):
    owner = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    logo = models.ImageField(upload_to="rest/", blank=True, null=True)
    location = models.CharField(max_length=100)
    email = models.EmailField()
    opening_time= models.TimeField()
    closing_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if self.owner.role != "manager" and self.owner.role != "admin":
            raise PermissionError("you are not permitted to perform this action")
        return super().save(*args, **kwargs)

class InviteStaff(models.Model):
    STATUS = [
        ("pending","Pending"),
        ("accepted","Accepted"),
        ("rejected","Rejected")
    ]
    ROLE = [
        ("chef","Chef"),
        ("waiter","Waiter"),
        ("cashier","Cashier"),
        ("assistant","Assistant")
    ]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, unique=True)
    Resturant =models.ForeignKey(Resturant, on_delete=models.CASCADE, related_name="resturant")
    invited_by = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name="manager")
    Staff = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name="staff")
    status = models.CharField(choices=STATUS,max_length=40,default="pending")
    role = models.CharField(choices=ROLE,max_length=40,default="waiter")
    accepted_at = models.DateTimeField()
    expiring = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

class Table(models.Model):
    TABLE_STATE = [
        ("occupied","Occupied"),
        ("available","Available"),
        ("cleaning","Cleaning"),
        ("reserved","Reserved")
    ]
    resturant = models.ForeignKey(Resturant,on_delete=models.CASCADE)
    table_number = models.IntegerField()
    capacity  = models.IntegerField()
    state = models.CharField(choices=TABLE_STATE, default="cleaning",max_length=50)

class Category(models.Model):
    resturant = models.ForeignKey(Resturant, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.TextField()

class MenuItem(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    image = models.ImageField(upload_to="menu/")
    preparation_time = models.TimeField()
    is_avaiable =models.BooleanField(default=False)

class Customer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    email = models.EmailField()
    point = models.IntegerField()

    def save(self,*args, **kwargs):
        try:
            if self.user != None:
                self.username = self.user.username
                self.email = self.user.email
        except Exception:
            raise ValueError("you have register as a customer first")
        return super().save(*args, **kwargs)
    
    
class Reservation(models.Model):
    STATUS =[
        ("pending","Pending"),
        ("confirmed","Confirmed"),
        ("cancelled","Cancelled"),
        ("completed","Completed")   
    ]
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    table = models.ForeignKey(Table,on_delete=models.CASCADE)
    reservation_time = models.DateTimeField()
    number_of_people = models.IntegerField()
    guest_name = models.CharField(max_length=50)
    special_requests = models.TextField(blank=True, null=True)
    status = models.CharField(choices=STATUS, default="pending", max_length=50)

class Order(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled")
        ]
    ORDER_TYPE = [
        ("dine-in", "Dine-in"),
        ("takeaway", "Takeaway"),
        ("delivery", "Delivery")
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL,blank=True,null=True)
    waiter = models.ForeignKey(InviteStaff, on_delete=models.SET_NULL,blank=True,null=True)
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS, default="pending", max_length=50)
    order_type = models.CharField(max_length=50, choices=ORDER_TYPE, default="dine-in")

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

class Payment(models.Model):
    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("credit_card", "Credit Card"),
        ("mobile_payment", "Mobile Payment")
    ]
    STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed")
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=50, choices=STATUS, default="pending")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

class KitchenOrder(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled")
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    chef = models.ForeignKey(InviteStaff, on_delete=models.CASCADE, limit_choices_to={'role': 'chef','status':'accepted'})
    status = models.CharField(choices=STATUS, default="pending", max_length=50)
    preparation_time = models.TimeField()
    completion_time = models.TimeField(blank=True, null=True)

class Inventory(models.Model):
    resturant = models.ForeignKey(Resturant, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now=True)

class InventoryTransaction(models.Model):
    TRANSACTION_TYPE = [
        ("addition", "Addition"),
        ("removal", "Removal")
    ]
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE)
    quantity = models.IntegerField()
    transaction_time = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role':'manager'})

class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    resturant = models.ForeignKey(Resturant, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    review_time = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    resturant = models.ForeignKey(Resturant,on_delete=models.CASCADE)
    reason = models.TextField()
    reslove = models.TextField()