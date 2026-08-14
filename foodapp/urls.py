from django.urls import path
from . import views
urlpatterns = [
    path("register/",views.registerView.as_view()),
    path("login/",views.LoginView.as_view()),
    # Resturant
    path("create_resturant/",views.CreateResturantView.as_view()),
    path("list_resturant/",views.ListResturantView.as_view()),
    path("update_resturant/<int:id>/",views.UpdateResturantView.as_view()),
    path("retrive_resturant/<int:id>/",views.RetriveResturantView.as_view()),
    path("delete_resturant/<int:id>/",views.DeleteResturantView.as_view()),
    # InviteStaff
    path("create_invitestaff/",views.CreateInviteStaffView),
    path("list_invitestaff/",views.ListInviteStaffView.as_view()),
    path("delete_invitestaff/<int:id>/",views.DeleteInviteStaff.as_view()),
    path("accept_invite/<int:rest_id>/",views.accept_inviteView.as_view()),
    path("reject_invite/<int:rest_id>/",views.reject_inviteView.as_view()),

    # Category

    path("create_category/",views.CreateCategoryView.as_view()),
    path("update_category/<int:id>/",views.UpdateCategoryView.as_view()),
    path("list_category/",views.ListCategoryView.as_view()),
    path("retrive_category/<int:id>/",views.RetriveCategoryView.as_view()),
    path("Delete_category/<int:id>/",views.DestoryCategoryView.as_view())    
]