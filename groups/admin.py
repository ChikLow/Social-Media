from django.contrib import admin
from .models import Group, GroupMembership

class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    readonly_fields = ("user", "role", "joined_at")

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "allow_public_posts", "member_count", "created_at")
    search_fields = ("name", "description", "slug")
    list_filter = ("allow_public_posts",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (GroupMembershipInline,)
    readonly_fields = ("member_count",)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "Members"

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "role", "joined_at")
    search_fields = ("user__username", "group__name")