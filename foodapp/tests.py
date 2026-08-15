from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from foodapp.models import (
    Category,
    CustomUser,
    Customer,
    InviteStaff,
    MenuItem,
    Notification,
    Resturant,
)
from foodapp.serializers import MenuItemSerializer
from foodapp.views import CreateMenuItemView, ListInviteStaffView, create_notification_for_user


class NotificationRecipientTest(TestCase):
    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            username="manager_user",
            email="manager@example.com",
            password="pass1234",
            role="manager",
        )
        self.customer_user = CustomUser.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="pass1234",
            role="customer",
        )
        self.customer = Customer.objects.create(user=self.customer_user)
        self.restaurant = Resturant.objects.create(
            owner=self.manager,
            name="Test Restaurant",
            description="A restaurant for tests.",
            location="Test City",
            email="restaurant@example.com",
            opening_time="09:00:00",
            closing_time="22:00:00",
        )
        self.staff_user = CustomUser.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="pass1234",
            role="customer",
        )
        self.invite = InviteStaff.objects.create(
            Resturant=self.restaurant,
            invited_by=self.manager,
            Staff=self.staff_user,
            status="accepted",
            role="waiter",
            message="Welcome aboard.",
        )

    def test_create_notification_from_customer_user(self):
        notification = create_notification_for_user(
            self.customer,
            message="Customer notification",
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.customer_user)
        self.assertTrue(Notification.objects.filter(user=self.customer_user).exists())

    def test_create_notification_from_invite_staff(self):
        notification = create_notification_for_user(
            self.invite,
            message="Staff notification",
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.staff_user)
        self.assertTrue(Notification.objects.filter(user=self.staff_user).exists())

    def test_create_notification_skips_missing_user(self):
        self.assertIsNone(create_notification_for_user(None, message="Ignored"))

    def test_list_invite_staff_for_staff_user(self):
        request = RequestFactory().get("/api/list_invitestaff/")
        request.user = self.staff_user

        view = ListInviteStaffView()
        view.request = request

        queryset = view.get_queryset()
        self.assertIn(self.invite, queryset)

    def test_create_menu_item_without_chef_field(self):
        manager = CustomUser.objects.create_user(
            username="menu_manager",
            email="menu_manager@example.com",
            password="pass1234",
            role="manager",
        )
        restaurant = Resturant.objects.create(
            owner=manager,
            name="Menu Restaurant",
            description="Menu tests",
            location="Nowhere",
            email="menu@example.com",
            opening_time="09:00:00",
            closing_time="22:00:00",
        )
        category = Category.objects.create(
            resturant=restaurant,
            name="Main",
            description="Main dishes",
        )

        serializer = MenuItemSerializer(
            data={
                "name": "Burger",
                "description": "Tasty burger",
                "price": "15.50",
                "preparation_time": "00:15:00",
                "category": category.pk,
                "is_available": True,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        view = CreateMenuItemView()
        view.request = SimpleNamespace(user=manager)
        view.perform_create(serializer)

        self.assertTrue(MenuItem.objects.filter(name="Burger", resturant=restaurant).exists())
