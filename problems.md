# Project Problems and Fixes Needed

## FIXED ISSUES (Completed)
✅ Missing Django SECRET_KEY - now using os.getenv() in settings.py
✅ URL file incomplete - all routes added and aligned
✅ View class name typos - fixed RetriveAPIView, DestoryAPIView
✅ CreateOrderView logic - variable ordering fixed
✅ UpdateOrderView - added missing serializer.save()
✅ RetrieveOrderView - fixed get_queryset(self) signature
✅ Cancel_Order_View - fixed order.order_number reference
✅ URLs syntax error - added missing comma

## REMAINING ISSUES

## 1. Some model and field names are inconsistent
Examples:
- `Resturant` is used throughout, but the app sometimes uses `Restaurant` naming in discussion and route naming.
- `InviteStaff` field names `Resturant`, `Staff`, and `invited_by` are inconsistently capitalized and may not match expected conventions.
- `CustomUser` roles are missing some common roles that might be needed later, but this is not necessarily blocking.

## 7. Some create/update actions are built on weak validation
- Several permission checks rely on comparing the request user to model values without proper validation for user roles and ownership.
- This makes some endpoints vulnerable to incorrect authorization logic.

## 8. Some API route patterns do not align cleanly with view names
- Some routes use names like `retrive_...`, `Delete_...`, and `cancel_order/<int:id>/` but the underlying methods are not consistently organized or named.
- This makes the API harder to maintain and less predictable.

## 9. Some `get_queryset` methods are incomplete or incorrect
- Some methods return queryset filters but do not handle non-authorized users properly.
- Some classes have `get_queryset` but do not use `self.request.user` in a consistent way.

## 10. Some views are still not fully aligned with the project structure
- The project appears to be a prototype/early build, and many endpoints were written quickly without standard Django REST Framework patterns.
- The code needs cleanup to follow consistent naming, validation, and queryset conventions.

## 11. Migration / project readiness concerns
- The project has a `foodapp/migrations/0001_initial.py` file, but there may still be issues if code and model fields are inconsistent with the intended API behavior.
- Database migration and runtime validation should be checked after the settings issue is fixed.

## 12. Several endpoints were added without checking their exact route names against the view names
- This caused broken or mismatched API routes until the URL file was corrected.
- The route file should be treated as part of the API contract and kept aligned with the views.
