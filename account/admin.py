from django.contrib import admin

from account.models import (
    SubscriptionPermission,
    Profile,
    CollageDetails,
    CollegeWiseUser,
    UserReferenceCode,
    UserWiseReference
)


class SubscriptionPermissionAdmin(admin.ModelAdmin):
    model = SubscriptionPermission
    list_display = ("user", "product", "valid_to", "purchase_order", "c_on")


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ("user", "mobile", "is_wa_number", "state", "u_on")


admin.site.register(SubscriptionPermission, SubscriptionPermissionAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CollageDetails)
admin.site.register(CollegeWiseUser)
admin.site.register(UserReferenceCode)
admin.site.register(UserWiseReference)
