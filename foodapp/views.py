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
    perimission_classes = [AllowAny]

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
    serializer_classes = ResturantSerializer
    permission_classes = [IsAuthenticated]

    def perfrom_distroy(self, serializer):
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

    def post(self, request, id):
        invite = get_object_or_404(InviteStaff, id=id)
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

    def post(self, request, id):
        invite = get_object_or_404(InviteStaff, id=id)
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
        serializer.save(self.request.user)


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
    permission_classes  = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def post(self,request,id):
        order = get_object_or_404(Order,id=id)
        if self.request.user == order.customer and order.status != "pending":
            Notification.objects.create(
            user=order.waiter,
            message=f"a cancle request has been sent for the order {order.order_number} at table {order.table} in {order.table.resturant} resturant by there customer {order.customer}"
            )
            raise PermissionDenied("you can't cancel any order that's not pending your request as be sent to the waiter but the waiter can't cancle a ready food")
        if self.request.user == order.waiter or self.request.user == order.table.resturant.owner:
            if order.status not in ["pending","preparing"]:
                Notification.objects.create(
                    user=order.customer,
                    message=f"Hello customer {order.customer} the waiter and the manager tried to cancel your order for you but your order was {order.status}"
                )
                raise PermissionDenied(f"you can't cancel a {order.status} order we have notified your customer about it ")
        Notification.objects.create(
            user=order.customer,
            message=f"you have successfully cancelled your order {order.number} on {order.table} at {order.table.resturant}  warinig: if your are not the one that cancelled it please please send your report to {order.table.resturant}"
        )
        if order.waiter != None:
            Notification.objects.create(
                user=order.waiter,
                message=f"your customer {order.customer} on {order.table} order has been cancelled"
            )
            Notification.objects.create(
                user=order.table.resturant.owner,
                message=f"your customer {order.customer} on {order.table} order {order.order_number}has been cancelled"
                )
        else:
            Notification.objects.create(
                user=order.table.resturant.owner,
                message=f"your customer {order.customer} on {order.table} order has been cancelled"
                )
        return order

class deliverrOderView(APIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self,request,id):
        order = get_object_or_404(Order,id=id)
        if self.request.user != order.waiter or self.request.user != order.table.resturant.owner:
            raise PermissionDenied("only the resturant manager or waiter can send a deliver massage")
        if order.status != "ready":
            raise ValidationError("you can only deliver a ready order")
        order.status = "delivered"
        order.save()
        if order.waiter != None:
            Notification.objects.create(
                user=order.waiter,
                message=f"the order has successfully be delivered to the customer {order.customer}"
            )
            Notification.objects.create(
                user=order.table.resturant.owner,
                message=f"the order has successfully be delivered to the customer {order.customer}"
            )
        else:
            Notification.objects.create(
                user=order.table.resturant.owner,
                message=f"the order has successfully be delivered to the customer {order.customer}"
            )