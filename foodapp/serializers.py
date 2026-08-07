from rest_framework import serializers
from .models import (
    CustomUser,
    Resturant,
    Table,
    Category,
    MenuItem,
    Order,
    OrderItem,
    KitchenOrder,
    Payment,
    Inventory,
    InventoryTransaction,
    Review,
    Reservation,
    Notification,
    InviteStaff
)
from django.contrib.auth.hashers import check_password

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "phone_number",
            "role",
            "confirm_password",
        ]

    def create(self, validated_data):
        if validated_data.get("confirm_password") == validated_data.get("password"):
            validated_data.pop("confirm_password")
            password = validated_data.pop("password")
            user = CustomUser(**validated_data)
            user.set_password(password)
            user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No such user")
        if not check_password(password,user.password):
            raise serializers.ValidationError("invalid password")
        return attrs
        

class ResturantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resturant
        fields = "__all__"

    def validate(self, attrs):
        if attrs.get("owner").role != "manager":
            raise serializers.ValidationError("only manager's can create Resturant")
        return attrs

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields ="__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
    def validate(self, attrs):
        waiter = attrs.get("waiter")
        if waiter.role != "waiter" and waiter.status != "accepted":
            raise serializers.ValidationError("this role is required by only waiters")
        return attrs

class OrdeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class KitchenOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitchenOrder
        fields = "__all__"
    def validate(self, attrs):
        chef = attrs.get("chef")
        if chef.role != "chef" and chef.status != "accepted":
            raise serializers.ValidationError("this role is only assigend to chef's")
        return attrs

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"

class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = "__all__"
    
    def validate(self, attrs):
        person = attrs.get("performed_by")
        if person.role != "manager":
            raise serializers.ValidationError("only cashiers and managers can perform this tasks ")
        return attrs

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

class InviteStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteStaff
        fields = "__all__"
    def validate(self, attrs):
        inviter = attrs.get("invited_by")
        if inviter.role != "manager" or inviter.role != "admin":
            raise serializers.ValidationError("only managers and admins can invite staff")
        return attrs