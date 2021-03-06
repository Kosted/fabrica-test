from django.contrib import admin

# Register your models here.
from users.models import AnonUser, CustomToken

admin.site.register(CustomToken)
admin.site.register(AnonUser)