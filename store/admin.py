from django.contrib import admin
from django.contrib.auth.models import User
from .models import Address, Category, Product, Cart, Order, UserHistoryViewProduct , Review , Vendor
from django.contrib.auth.models import Group
# Register your models here.


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    list_per_page = 10
    search_fields = ('locality', 'city', 'state')


class UserHistory(admin.ModelAdmin):
    list_display = ('id' ,'user', 'product', 'added')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'content')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category_image',
                    'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title", )}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'product_image',
                    'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'category', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'category', 'short_description')
    prepopulated_fields = {"slug": ("title", )}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def has_change_permission(self, request, obj=None):
        if not obj:
            # Allow adding new products
            return True
        # Check if the user is the creator of the product
        return obj.user == request.user or request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        if not obj:
            # No deletion permission for new products
            return False
        # Check if the user is the creator of the product or a superuser
        return obj.user == request.user or request.user.is_superuser
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_editable = ('quantity',)
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'ordered_date')
    list_editable = ('quantity', 'status')
    list_filter = ('status', 'ordered_date')
    list_per_page = 20
    search_fields = ('user', 'product')

class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'email')
    actions = ['make_staff']

    def make_staff(self, request, queryset):
        group = Group.objects.get(name='Vendor')  # Replace 'YourGroupName' with the name of your group
        for vendor in queryset:
            # Check if the vendor is already a staff member
            if not vendor.user.groups.filter(name=group.name).exists():
                vendor.user.groups.add(group)
                vendor.user.is_staff = True
                vendor.user.save()

        self.message_user(request, "Selected vendors are now staff members.")

    make_staff.short_description = "Make selected vendors staff"



admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(UserHistoryViewProduct, UserHistory)
admin.site.register(Vendor , VendorAdmin)
