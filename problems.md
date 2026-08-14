# Project Problems and Fixes Needed

## 1. Missing Django secret key
- The project cannot start because Django raises:
  `django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.`
- This must be configured in `food_store/settings.py` before the app can run.

## 2. URL file is incomplete
- The app has many view classes defined in `foodapp/views.py`, but the route list in `foodapp/urls.py` was missing several endpoints.
- Required sections included table, reservation, report, payment, kitchen, inventory, and review routes.

## 3. View class names are inconsistent and misspelled
Examples:
- `RetriveResturantView` should be `RetrieveResturantView`
- `RetriveInviteStaffView` should be `RetrieveInviteStaffView`
- `DestoryCategoryView` should be `DestroyCategoryView`
- `DestroyReservationView` should be a proper destroy view class name
- `cancelOrderView` is inconsistent with the naming pattern used elsewhere

## 4. Some view logic is incorrect
Examples from `foodapp/views.py`:
- `CreateOrderView` contains a bad assignment:
  `chef = serializer.validated_data.get("waiter").role = "chef"`
- This is not valid logic and overwrites the waiter role incorrectly.

- In `UpdateOrderView`, the permission check is wrong:
  `if (self.request.user != waiter.Staff or self.request.user != table.resturant.owner):`
  This references fields that do not match the model definitions consistently.

- In `RetrieveOrderView`, the method signature is not standard:
  `def get_queryset(self, serializer):` 
  Django expects `get_queryset(self)` without extra arguments.

## 5. Wrong serializer / attribute references
- Several views access attributes like `waiter.Staff`, `table.resturant`, and `order.number` that may not exist as intended.
- There are mismatches between model field names and attribute names used in conditions and notifications.

## 6. Some model and field names are inconsistent
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
