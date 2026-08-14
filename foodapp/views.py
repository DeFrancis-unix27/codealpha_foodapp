from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib.auth import authenticate
from rest_framework import generics
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

# Create your views here.


class registerView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"message": "no such user found"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": f"welcome {user.username} to foodbank",
                "refresh": str(refresh),
                "access_token": str(refresh.access_token),
            }
        )


class CreateResturantView(generics.CreateAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != "manager":
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class UpdateResturantView(generics.UpdateAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.role != "manager":
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class ListResturantView(generics.ListAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permission_classes = [AllowAny]


class RetriveResturantView(generics.RetrieveAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permission_classes = [IsAuthenticated]

    def perform_retrieve(self, serializer):
        if self.request.user.role != "manager":
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class DeleteResturantView(generics.DestroyAPIView):
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, serializer):
        if self.request.user.role != "manager":
            raise PermissionDenied(
                "action can only be performed by the manger of the resturant"
            )
        serializer.save(owner=self.request.user)


class CreateInviteStaffView(APIView):
    queryset = InviteStaff.objects.all()
    serializer_class = InviteStaffSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if (
            self.request.user.role != "manager"
            and InviteStaff.objects.filter(Resturant__owner=self.request.user).exists()
            == False
        ):
            raise PermissionDenied(
                "action can only be performed by the manger of the resturant"
            )
        serializer = InviteStaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(invited_by=self.request.user)
            Notification.objects.create(
                user=serializer.validated_data.get("staff"),
                message=f"Hello you have be invited to join {serializer.validated_data.get('Resturant').name} as there {serializer.validated_data.get('role')}. please check your invite status".capitalize(),
            )
            Notification.objects.create(
                user=serializer.validated_data.get("invited_by"),
                message=f"hello {self.request.user.username} your invite message has been sent to {serializer.validated_data.get('staff')}".capitalize(),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetriveInviteStaffView(generics.RetriveAPIView):
    queryset = InviteStaff.objects.all()
    serializer_class = InviteStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "manager":
            return InviteStaff.object.filter(invited_by=self.request.user)
        return InviteStaff.object.filter(staff=self.request.user)


class ListInviteStaffView(generics.ListAPIView):
    queryset = InviteStaff.objects.all()
    serializer_class = InviteStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "manager":
            return InviteStaff.object.filter(invited_by=self.request.user)
        return InviteStaff.object.filter(staff=self.request.user)


class accept_inviteView(APIView):
    queryset = InviteStaff.objects.all()
    serializer_class = InviteStaffSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, rest_id):
        invite = get_object_or_404(InviteStaff, id=rest_id)
        if (
            invite.Staff != self.request.user
            or invite.status != "pending"
            or invite.expiring < timezone.now()
        ):
            raise PermissionDenied(
                "you have been denied from having access to this invite"
            )
        invite.status = "accepted"
        invite.accepted_at = timezone.now()
        invite.save()
        Notification.objects.create(
            user=self.request.user,
            message=f"Congrates {self.request.user.username} you are now a {invite.role} at {invite.Resturant}",
        )
        Notification.objects.create(
            user=invite.invited_by,
            message=f"Hello {invite.invited_by} your request for {invite.role} at {invite.Resturant} has been accepted by {invite.staff}",
        )
        return invite


class reject_inviteView(APIView):
    queryset = InviteStaff.objects.all()
    serializer_class = InviteStaffSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, rest_id):
        invite = get_object_or_404(InviteStaff, id=rest_id)
        if (
            invite.Staff != self.request.user
            or invite.status != "pending"
            or invite.expiring < timezone.now()
        ):
            raise PermissionDenied(
                "you have been denied from having access to this invite"
            )
        invite.status = "rejected"
        # invite.accepted_at = timezone.now()
        invite.save()
        Notification.objects.create(
            user=self.request.user,
            message=f"Hello {self.request.user.username} you have successfully rejected  {invite.role} role at {invite.Resturant} ",
        )
        Notification.objects.create(
            user=invite.invited_by,
            message=f"Hello {invite.invited_by} your request for {invite.role} at {invite.Resturant} has been rejected by {invite.staff} ",
        )
        return invite

class  DeleteInviteStaff(generics.DestroyAPIView):
    queryset = InviteStaff.objects.all()
    serializer_class = InviteStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InviteStaff.objects.filter(Resturant__owner=self.request.user)

class CreateCategoryView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class UpdateCategoryView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class ListCategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class RetriveCategoryView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class DestroyCategoryView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class CreateMenuItemView(generics.CreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        chef = serializer.validated_data["chef"]
        chef_rest = serializer.validated_data["chef"].Resturant
        resturant = serializer.validated_data["category"].resturant

        if self.request.user != resturant.owner or chef.role != "chef":
            if chef != None and chef_rest != resturant:
                raise PermissionDenied("Your are not approved to perform this action")
        serializer.save(chef=self.request.user)


class ListMenuItemView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]


class RetriveMenuItemView(generics.RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]


class UpdateMenuItemView(generics.UpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        chef = serializer.validated_data["chef"]
        chef_rest = serializer.validated_data["chef"].Resturant
        resturant = serializer.validated_data["category"].resturant

        if self.request.user != resturant.owner or chef.role != "chef":
            if chef != None and chef_rest != resturant:
                raise PermissionDenied("Your are not approved to perform this action")
        serializer.save(chef=self.request.user)


class DestroyMenuItemView(generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, serializer):
        chef = serializer.validated_data["chef"]
        chef_rest = serializer.validated_data["chef"].Resturant
        resturant = serializer.validated_data["category"].resturant

        if self.request.user != resturant.owner or chef.role != "chef":
            if chef != None and chef_rest != resturant:
                raise PermissionDenied("Your are not approved to perform this action")
        serializer.save(chef=self.request.user)


class CreateOrderView(APIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        waiter = serializer.validated_data.get("waiter")
        chef = serializer.validated_data.get("waiter").role = "chef"
        table = serializer.validated_data.get("table")
        manager = serializer.validated_data.get("waiter").invited_by
        if table.resturant == waiter.Resturant or table.resturant == manager.Resturant:
            # check if table is available
            if table.state != "available":
                raise ValidationError(f"table is at {table.state} state")
        else:
            raise PermissionDenied("Only waiters working \
             at the resturant can create an other \
            ")
        if chef.Resturant == table.resturant:
            Notification.objects.create(
                user=chef,
                message=f" hello Chef an Order has been placed at {table.resturant} by a customer called {serializer.validated_data.get('customer').username} go to your order_items to view more details",
            )
            Notification.objects.create(
                user=serializer.validated_data.get("customer"),
                message=f"Hello {serializer.validated_data.get('customer').username} your order at {table.resturant} has been placed",
            )
        serializer.save(chef=self.request.user)


class UpdateOrderView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def perform_update(self, serializer):
        waiter = serializer.validated_data.get("waiter")
        table = serializer.validated_data.get("table")
        if (
            self.request.user != waiter.Staff
            or self.request.user != table.resturant.owner
        ):
            raise ValidationError("you are nor allowed to perform this action")
        serializer.save(self.request.user)


class cancelOrderView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def post(self, request, id):
        order = get_object_or_404(Order, id=id)
        if self.request.user == order.customer and order.status != "pending":
            Notification.objects.create(
                user=order.waiter,
                message=f"a cancle request has been sent for the order {order.order_number} at table {order.table} in {order.table.resturant} resturant by there customer {order.customer}",
            )
            raise PermissionDenied(
                "you can't cancel any order that's not pending your request as be sent to the waiter but the waiter can't cancle a ready food"
            )
        if (
            self.request.user == order.waiter
            or self.request.user == order.table.resturant.owner
        ):
            if order.status not in ["pending", "preparing"]:
                Notification.objects.create(
                    user=order.customer,
                    message=f"Hello customer {order.customer} the waiter and the manager tried to cancel your order for you but your order was {order.status}",
                )
                raise PermissionDenied(
                    f"you can't cancel a {order.status} order we have notified your customer about it "
                )
        Notification.objects.create(
            user=order.customer,
            message=f"you have successfully cancelled your order {order.number} on {order.table} at {order.table.resturant}  warinig: if your are not the one that cancelled it please please send your report to {order.table.resturant}",
        )
        if order.waiter != None:
            Notification.objects.create(
                user=order.waiter,
                message=f"your customer {order.customer} on {order.table} order has been cancelled",
            )
            Notification.objects.create(
                user=order.table.resturant.owner,
                message=f"your customer {order.customer} on {order.table} order {order.order_number}has been cancelled",
            )
        else:
            Notification.objects.create(
                user=order.table.resturant.owner,
                message=f"your customer {order.customer} on {order.table} order has been cancelled",
            )
        return order


class deliverOrderView(APIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        order = get_object_or_404(Order, id=id)
        if (
            self.request.user != order.waiter
            or self.request.user != order.table.resturant.owner
        ):
            raise PermissionDenied(
                "only the resturant manager or waiter can send a deliver massage"
            )
        if order.status != "ready":
            raise ValidationError("you can only deliver a ready order")
        order.status = "delivered"
        order.save()
        if order.waiter != None:
            Notification.objects.create(
                user=order.waiter,
                message=f"the order has successfully be delivered to the customer {order.customer}",
            )
            Notification.objects.create(
                user=order.table.resturant.owner,
                message=f"the order has successfully be delivered to the customer {order.customer}",
            )
        else:
            Notification.objects.create(
                user=order.table.resturant.owner,
                message=f"the order has successfully be delivered to the customer {order.customer}",
            )
        return order


class ListOrderView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self):
        if self.request.user.role == "customer":
            return Order.objects.filter(customer=self.request.user.customer)
        elif self.request.user.role == "waiter":
            return Order.objects.filter(waiter__staff=self.request.user)
        elif self.request.user.role == "manager":
            return Order.objects.filter(table__resturant__owner=self.request.user)
        else:
            raise PermissionDenied("you are not allowed to view this orders")
        return super().get_queryset()


class RetrieveOrderView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self, serializer):
        if self.request.user.role == "customer":
            return Order.objects.filter(customer=self.request.user.customer)
        elif self.request.user.role == "waiter":
            return Order.objects.filter(waiter__staff=self.request.user)
        elif self.request.user.role == "manager":
            return Order.objects.filter(table__resturant__owner=self.request.user)
        else:
            raise PermissionDenied("you are not allowed to view this orders")
        return super().get_queryset(serializer)


class CreateTableView(generics.CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class UpdateTableView(generics.UpdateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class ListTableView(generics.ListAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]


class RetrieveTableView(generics.RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]


class DestroyTableView(generics.DestroyAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class CreateReservationView(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [AllowAny]


class ListReservationView(generics.ListAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(customer=self.request.user)


class RetrieveReservationView(generics.RetrieveAPIView):
    queryset = Reservation.objects.all()
    serailizer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(customer=self.request.user)


class DestroyReservationView(generics.DestoryAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]


class CreateReportView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]


class ListReportView(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(resturant__owner=self.request.user)


class RetrieveReportView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(resturant__owner=self.request.user)


class ResolveReportView(APIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        report = get_object_or_404(Report, id=id)
        if report.resolved_by != report.resturant.owner:
            raise PermissionDenied("only the resturant owner can resolve this report")
        report.resolved_by = self.request.user
        report.resolution = request.data.get("resolution")
        report.resolved_date = timezone.now()
        report.is_resolved = True
        report.save()


class ListNotificationView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class RetrieveNotificationView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class Is_readNotificationView(APIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def post(self,request,id):
        notification = get_object_or_404(Notification,id=id)

        if self.request.user != notification.user:
            raise PermissionDenied("you are not permitted to view this")
        notification.is_read = True
        notification.save()

class CreatePaymentView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.validated_data.get("order")
        if self.request.user != order.customer.user:
            raise PermissionDenied("you are not allowed to make payment for this order")
        if order.status != "delivered":
            raise ValidationError("you can only make payment for delivered orders")
        serializer.save(sender=self.request.user, resturant=order.table.resturant)
        serializer.save(customer=self.request.user.customer)


class ListPaymentView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "customer":
            return Payment.objects.filter(customer=self.request.user.customer)
        elif self.request.user.role == "manager":
            return Payment.objects.filter(
                order__table__resturant__owner=self.request.user
            )
        else:
            raise PermissionDenied("you are not allowed to view this payments")


class RetrivePaymentView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "customer":
            return Payment.objects.filter(customer=self.request.user.customer)
        elif self.request.user.role == "manager":
            return Payment.objects.filter(
                order__table__resturant__owner=self.request.user
            )
        else:
            raise PermissionDenied("you are not allowed to view this payments")


class CreateKitchenView(generics.CreateAPIView):
    queryset = KitchenOrder.objects.all()
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.validated_data.get("order")
        chef = serializer.validated_data.get("chef")
        if self.request.user != chef.staff:
            raise PermissionDenied("you are not allowed to create this kitchen order")
        if order.status != "pending":
            raise ValidationError(
                "you can only create kitchen order for pending orders"
            )
        serializer.save(chef=self.request.user)


class ListKitchenView(generics.ListAPIView):
    queryset = KitchenOrder.objects.all()
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "chef":
            return KitchenOrder.objects.filter(chef__staff=self.request.user)
        elif self.request.user.role == "manager":
            return KitchenOrder.objects.filter(
                order__table__resturant__owner=self.request.user
            )
        else:
            raise PermissionDenied("you are not allowed to view this kitchen orders")


class RetrieveKitchenView(generics.RetrieveAPIView):
    queryset = KitchenOrder.objects.all()
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "chef":
            return KitchenOrder.objects.filter(chef__staff=self.request.user)
        elif self.request.user.role == "manager":
            return KitchenOrder.objects.filter(
                order__table__resturant__owner=self.request.user
            )
        else:
            raise PermissionDenied("you are not allowed to view this kitchen orders")


class DestroyKitchenView(generics.DestroyAPIView):
    queryset = KitchenOrder.objects.all()
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, serializer):
        if (
            self.request.user.role != "chef"
            and serializer.validated_data["order"].table.resturant.owner
            != self.request.user
        ):
            raise PermissionDenied(
                "action can only be performed by chefs or resturant managers"
            )
        serializer.save(owner=self.request.user)


class CancelKitchenView(generics.UpdateAPIView):
    queryset = KitchenOrder.objects.all()
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        status = serializer.validated_data.get("status")
        if status == "cancelled":
            raise ValidationError("kitchen is already cancelled")
        if (
            self.request.user.role != "chef"
            and serializer.validated_data["order"].table.resturant.owner
            != self.request.user
        ):
            raise PermissionDenied(
                "action can only be performed by chefs or resturant managers"
            )
        serializer.save(status="cancelled", chef=self.request.user)


class ReadyKitchenView(generics.UpdateAPIView):
    queryset = KitchenOrder.objects.all()
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        status = serializer.validated_data.get("status")
        if status == "ready":
            raise ValidationError("kitchen is already ready")
        if (
            self.request.user.role != "chef"
            and serializer.validated_data["order"].table.resturant.owner
            != self.request.user
        ):
            raise PermissionDenied(
                "action can only be performed by chefs or resturant managers"
            )
        serializer.save(status="ready", chef=self.request.user)


class PreparingKitchenView(generics.UpdateAPIView):
    queryset = KitchenOrder.objects.all()
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        status = serializer.validated_data.get("status")
        if status == "preparing":
            raise ValidationError("kitchen is already preparing")
        if (
            self.request.user.role != "chef"
            and serializer.validated_data["order"].table.resturant.owner
            != self.request.user
        ):
            raise PermissionDenied(
                "action can only be performed by chefs or resturant managers"
            )
        serializer.save(status="preparing", chef=self.request.user)


class CreateInventoryView(generics.CreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class ListInventoryView(generics.ListAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "manager":
            return Inventory.objects.filter(resturant__owner=self.request.user)
        else:
            raise PermissionDenied("you are not allowed to view this inventory")


class RetrieveInventoryView(generics.RetrieveAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "manager":
            return Inventory.objects.filter(resturant__owner=self.request.user)
        else:
            raise PermissionDenied("you are not allowed to view this inventory")


class UpdateInventoryView(generics.UpdateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class DestroyInventoryView(generics.DestroyAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["resturant"].owner != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(owner=self.request.user)


class CreateInventoryTransactionView(generics.CreateAPIView):
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if (
            self.request.user.role != "manager"
            and serializer.validated_data["inventory"].resturant.owner
            != self.request.user
        ):
            raise PermissionDenied("action can only be performed by managers")
        serializer.save(performed_by=self.request.user)


class ListInventoryTransactionView(generics.ListAPIView):
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "manager":
            return InventoryTransaction.objects.filter(
                inventory__resturant__owner=self.request.user
            )
        else:
            raise PermissionDenied(
                "you are not allowed to view this inventory transaction"
            )


class RetrieveInventoryTransactionView(generics.RetrieveAPIView):
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "manager":
            return InventoryTransaction.objects.filter(
                inventory__resturant__owner=self.request.user
            )
        else:
            raise PermissionDenied(
                "you are not allowed to view this inventory transaction"
            )


class CreateReviewView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


class ListReviewView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


class RetrieveReviewView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


class DestroyReviewView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs["pk"])
        if self.request.user != review.resturant.owner:
            raise PermissionDenied("you are not allowed to delete this review")
        return Review.objects.filter(customer=self.request.user.customer)


