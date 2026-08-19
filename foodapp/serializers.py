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
    InviteStaff,
    Customer,
    Report,
)
from django.contrib.auth.hashers import check_password


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "role",
            "email",
            "password",
            "phone_number",
            "confirm_password",
        ]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        Customer.objects.create(user=user)
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
        if not check_password(password, user.password):
            raise serializers.ValidationError("invalid password")
        return attrs


class ResturantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resturant
        fields = [
            "owner",
            "name",
            "description",
            "logo",
            "location",
            "email",
            "opening_time",
            "closing_time",
        ]

    def validate(self, attrs):
        owner = attrs.get("owner")
        if owner is None:
            raise serializers.ValidationError({"owner": "Owner is required."})

        if getattr(owner, "role", None) != "manager":
            raise serializers.ValidationError(
                {"owner": "Only managers can perform this action."}
            )
        return attrs


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["resturant", "table_number", "capacity", "state"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["resturant", "name", "description"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "name",
            "description",
            "price",
            "image",
            "preparation_time",
            "category",
            "is_available",
        ]
        read_only_fields = ["resturant", "chef"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["menu_item", "quantity"]
        read_only_fields = ["price", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    orderItem = OrderItemSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Order
        fields = [
            "customer",
            "table",
            "waiter",
            "total_price",
            "status",
            "order_type",
            "orderItem",
        ]
        read_only_fields = [
            "order_number",
            "status",
            "total_price",
            "order_time",
        ]

    def validate(self, attrs):
        waiter = attrs.get("waiter")
        table = attrs.get("table")

        if not waiter:
            raise serializers.ValidationError({"waiter": "A waiter is required."})

        if not table:
            raise serializers.ValidationError({"table": "A table is required."})

        # Check table availability
        if table.state != "available":
            raise serializers.ValidationError(
                {"table": "Table is not available at the moment."}
            )

        # Check waiter
        if waiter.role != "waiter":
            raise serializers.ValidationError(
                {"waiter": "The selected user is not a waiter."}
            )

        if waiter.status != "accepted":
            raise serializers.ValidationError(
                {"waiter": "The waiter has not been accepted."}
            )

        if waiter.Resturant != table.resturant:
            raise serializers.ValidationError(
                {"waiter": "The waiter is not assigned to this restaurant."}
            )

        return attrs

    def create(self, validated_data):
        items = validated_data.pop("orderItem", [])

        total = sum(item["menu_item"].price * item["quantity"] for item in items)

        order = Order.objects.create(**validated_data, total_price=total)

        for item in items:
            price = item["menu_item"].price
            quantity = item["quantity"]

            OrderItem.objects.create(
                order=order,
                menu_item=item["menu_item"],
                quantity=quantity,
                price=price,
                subtotal=price * quantity,
            )

        order.table.state = "occupied"
        order.table.save(update_fields=["state"])

        return order


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["sender", "status", "resturant", "transaction_id"]


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
        read_only_fields = ["resturant"]


class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = "__all__"

    def validate(self, attrs):
        person = attrs.get("performed_by")
        if person.role != "manager":
            raise serializers.ValidationError(
                "only cashiers and managers can perform this tasks "
            )
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["customer", "resturant"]


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
        if inviter.role != "manager":
            raise serializers.ValidationError("only managers can invite staff")
        return attrs


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
