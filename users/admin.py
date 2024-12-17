from django.contrib import admin
from users.models import CustomUser,Post,Comment,Like
admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
# Register your models here.
