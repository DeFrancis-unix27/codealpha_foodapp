from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.registerView.as_view()),
    path("login/", views.LoginView.as_view()),

    # Resturant
    path("create_resturant/", views.CreateResturantView.as_view()),
    path("list_resturant/", views.ListResturantView.as_view()),
    path("update_resturant/<int:pk>/", views.UpdateResturantView.as_view()),
    path("retrive_resturant/<int:pk>/", views.RetriveResturantView.as_view()),
    path("delete_resturant/<int:pk>/", views.DeleteResturantView.as_view()),

    # InviteStaff
    path("create_invitestaff/", views.CreateInviteStaffView.as_view()),
    path("list_invitestaff/", views.ListInviteStaffView.as_view()),
    path("retrive_invitestaff/<int:pk>/", views.RetriveInviteStaffView.as_view()),
    path("delete_invitestaff/<int:pk>/", views.DeleteInviteStaff.as_view()),
    path("accept_invite/<int:rest_id>/", views.accept_inviteView.as_view()),
    path("reject_invite/<int:rest_id>/", views.reject_inviteView.as_view()),

    # Category
    path("create_category/", views.CreateCategoryView.as_view()),
    path("update_category/<int:pk>/", views.UpdateCategoryView.as_view()),
    path("list_category/", views.ListCategoryView.as_view()),
    path("retrive_category/<int:pk>/", views.RetriveCategoryView.as_view()),
    path("delete_category/<int:pk>/", views.DestroyCategoryView.as_view()),

    # Menu item
    path("create_menu_item/", views.CreateMenuItemView.as_view()),
    path("list_menu_item/", views.ListMenuItemView.as_view()),
    path("retrive_menu_item/<int:pk>/", views.RetriveMenuItemView.as_view()),
    path("update_menu_item/<int:pk>/", views.UpdateMenuItemView.as_view()),
    path("delete_menu_item/<int:pk>/", views.DestroyMenuItemView.as_view()),

    # Order
    path("create_order/", views.CreateOrderView.as_view()),
    path("list_order/", views.ListOrderView.as_view()),
    path("retrive_order/<int:pk>/", views.RetrieveOrderView.as_view()),
    path("update_order/<int:pk>/", views.UpdateOrderView.as_view()),
    path("cancel_order/<int:id>/", views.cancelOrderView.as_view()),
    path("deliver_order/<int:id>/", views.deliverOrderView.as_view()),

    # Table
    path("create_table/", views.CreateTableView.as_view()),
    path("list_table/", views.ListTableView.as_view()),
    path("retrive_table/<int:pk>/", views.RetrieveTableView.as_view()),
    path("update_table/<int:pk>/", views.UpdateTableView.as_view()),
    path("delete_table/<int:pk>/", views.DestroyTableView.as_view()),

    # Reservation
    path("create_reservation/", views.CreateReservationView.as_view()),
    path("list_reservation/", views.ListReservationView.as_view()),
    path("retrive_reservation/<int:pk>/", views.RetrieveReservationView.as_view()),
    path("delete_reservation/<int:pk>/", views.DestroyReservationView.as_view()),

    # Report
    path("create_report/", views.CreateReportView.as_view()),
    path("list_report/", views.ListReportView.as_view()),
    path("retrive_report/<int:pk>/", views.RetrieveReportView.as_view()),
    path("resolve_report/<int:id>/", views.ResolveReportView.as_view()),

    # Notification
    path("list_notification/", views.ListNotificationView.as_view()),
    path("retrive_notification/<int:pk>/", views.RetrieveNotificationView.as_view()),
    path("read_notification/<int:id>/", views.Is_readNotificationView.as_view()),

    # Payment
    path("create_payment/", views.CreatePaymentView.as_view()),
    path("list_payment/", views.ListPaymentView.as_view()),
    path("retrive_payment/<int:pk>/", views.RetrivePaymentView.as_view()),

    # Kitchen
    path("create_kitchen/", views.CreateKitchenView.as_view()),
    path("list_kitchen/", views.ListKitchenView.as_view()),
    path("retrive_kitchen/<int:pk>/", views.RetrieveKitchenView.as_view()),
    path("delete_kitchen/<int:pk>/", views.DestroyKitchenView.as_view()),
    path("cancel_kitchen/<int:pk>/", views.CancelKitchenView.as_view()),
    path("ready_kitchen/<int:pk>/", views.ReadyKitchenView.as_view()),
    path("preparing_kitchen/<int:pk>/", views.PreparingKitchenView.as_view()),

    # Inventory
    path("create_inventory/", views.CreateInventoryView.as_view()),
    path("list_inventory/", views.ListInventoryView.as_view()),
    path("retrive_inventory/<int:pk>/", views.RetrieveInventoryView.as_view()),
    path("update_inventory/<int:pk>/", views.UpdateInventoryView.as_view()),
    path("delete_inventory/<int:pk>/", views.DestroyInventoryView.as_view()),

    # Inventory transaction
    path("create_inventory_transaction/", views.CreateInventoryTransactionView.as_view()),
    path("list_inventory_transaction/", views.ListInventoryTransactionView.as_view()),
    path("retrive_inventory_transaction/<int:pk>/", views.RetrieveInventoryTransactionView.as_view()),

    # Review
    path("create_review/", views.CreateReviewView.as_view()),
    path("list_review/", views.ListReviewView.as_view()),
    path("retrive_review/<int:pk>/", views.RetrieveReviewView.as_view()),
    path("delete_review/<int:pk>/", views.DestroyReviewView.as_view()),
]