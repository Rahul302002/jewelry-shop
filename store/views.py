from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product, UserHistoryViewProduct, Review
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm, EmailPostForm, ReviewForm
from django.contrib import messages
from django.views import View
import decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator  # for Class Based Views
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.views.generic import View
from .preutils import html_to_pdf
from django.shortcuts import reverse
# import recommendation from utils
from .utils import recommend, user_recommendation
from django.core.mail import send_mail
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView, TemplateView
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.


def generate_pdf(response, id):
    order = Order.objects.get(id=id)
    data = {
        "user": order.user,
        "address": order.address,
        "product": order.product,
        "quantity": order.quantity,
        "total": order.product.price * order.quantity,
        "order_date": order.ordered_date,
        "status": order.status
    }
    pdf = html_to_pdf('store/result.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


# def post_share(request, post_id):
#     # Retrieve post by id
#     post = get_object_or_404(Product, id=post_id)
#     sent = False
#     if request.method == 'POST':
#         # Form was submitted
#         form = EmailPostForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             post_url = request.build_absolute_uri(
#                 post.get_absolute_url())
#             subject = f"{cd['name']} recommends you read " \
#                 f"{post.title}"
#             message = f"Read {post.title} at {post_url}\n\n" \
#                 f"{cd['name']}\'s comments: {cd['comments']}"
#             send_mail(subject, message, 'your_account@gmail.com',
#                       [cd['to']])
#             sent = True

#     else:
#     form = EmailPostForm()
#     return render(request, 'blog/post/share.html', {'post': post,
#                                                     'form': form})




def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    # if request.user.is_authenticated:
    #     user_history = UserHistoryViewProduct.objects.filter(
    #         user=request.user).order_by('-added').values_list('product_id', flat=True)[:4]
    #     recommend_id = user_recommendation(user_history)
    #     related_products = Product.objects.filter(
    #         is_active=True, id__in=recommend_id)
    #     print(recommend_id)
    #     context = {
    #         'categories': categories,
    #         'products': products,
    #         'recommend': related_products[:8]
    #     }
    #     return render(request, 'store/index.html', context)
    context = {
        'categories': categories,
        'products': products,
    }

    return render(request, 'store/index.html', context)


def vendorlogin(request):
    return render(request, 'account/vendorlogin.html')


from .forms import VendorForm

@login_required
def vendor_registration(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            # Save the vendor data to the database
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()

            # Send notification to admin
            # admin_email = settings.ADMIN_EMAIL # You need to define ADMIN_EMAIL in your settings.py
            # subject = 'New Vendor Registration Request'
            # message = 'A new vendor has registered. Please review their details.'
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])

            return redirect('store:home')
    else:
        form = VendorForm()
    return render(request, 'account/vendorlogin.html', {'form': form})

@login_required             
def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    review = ReviewForm()
    all_review = Review.objects.filter(product=product)
    if request.method == 'POST':
        form = ReviewForm(request.POST or None)
        if form.is_valid():
            cd = form.cleaned_data
            content = cd['content']
            rating = cd['rating']
            rate = Review(user=request.user, product=product,
                          content=content, rating=rating)
            rate.save()
        return HttpResponseRedirect(reverse('store:all-categories'))
    if request.user:
        history = UserHistoryViewProduct(user=request.user, product=product)
        history.save()
    liked = False
    data = {}
    if product.likes.filter(id=request.user.id).exists():
        liked = True
    data['number_of_likes'] = product.number_of_likes()
    data['post_is_liked'] = liked
    # recommend_product = recommend(product.id)
    # related_products = Product.objects.filter(
    #     is_active=True)
    context = {
        'product': product,
        # 'related_products': related_products,
        "data": data,
        "form": review,
        "all_review" : all_review

    }
    return render(request, 'store/detail.html', context)

# def detail(request, slug):
#     product = get_object_or_404(Product, slug=slug)
#     related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
#     context = {
#         'product': product,
#         'related_products': related_products,

#     }
#     return render(request, 'store/detail.html', context)


def product_Like(request, pk):
    post = get_object_or_404(Product, id=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect('store:all-categories')


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories': categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    q = request.GET.get('q', None)
    if q:
        products = Product.objects.filter(title__icontains=q)
    categories = Category.objects.filter(is_active=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(products, per_page=5)
    try:
        page_object = paginator.page(page)
    except PageNotAnInteger:
        page_object = paginator.page(1)
    except EmptyPage:
        page_object = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'products': page_object,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)

def all_products(request):
    products = Product.objects.filter(is_active=True)
    q = request.GET.get('q', None)
    if q:
        products = products.filter(title__icontains=q)
    page = request.GET.get('page', 1)
    paginator = Paginator(products, per_page=5)
    try:
        page_object = paginator.page(page)
    except PageNotAnInteger:
        page_object = paginator.page(1)
    except EmptyPage:
        page_object = paginator.page(paginator.num_pages)
    categories = Category.objects.filter(is_active=True)
    context = {
        'object_list': page_object,
         'categories': categories,
    }
    return render(request, 'store/all_products.html', context)

class ListAllProduct( ListView):
    model = Product
    paginate_by = 5
    template_name = 'store/all_products.html'

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        object_list = self.model.objects.all()
        if q:
            object_list = object_list.filter(title__icontains=q)
        return object_list


# Authentication Starts Here
@login_required
def user_products(request):
    user = request.user
    products = Product.objects.filter(user=user)
    context = {
        'products': products
    }
    return render(request, 'store/user_products.html', context)

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(
                request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})


@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses': addresses, 'orders': orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()

    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user == user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')

    address = Address.objects.get(id=address_id)
    cart = Cart.objects.filter(user=user)
    if request.method == 'POST':
        subjesct = "you have just brought these products"
        message = f"you have ordered :- "
        for c in cart:
            # Saving all the products from Cart to Order
            Order(user=user, address=address,
                  product=c.product, quantity=c.quantity).save()
            message += f" {c.product.title} with quantity : {c.quantity} "
            # And Deleting from Cart
            c.delete()
        # send_mail(subject=subjesct , message=message , from_email="vishwajeetv2003@gmail.com" , recipient_list=[user.email] )
        return redirect('store:orders')
    return render(request, "store/checkout.html")


@login_required
def orders(request):
    all_orders = Order.objects.filter(
        user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})


def shop(request):
    return render(request, 'store/shop.html')


def test(request):
    return render(request, 'store/test.html')



def error_404_view(request, exception):
    return render(request, '404.html')


@login_required
def product_and_review(request):
    if not request.user.is_staff:
        messages.warning(request, "You are not authorized to access this page.")
        return redirect('store:home')

    if request.user.is_superuser:
        products = Product.objects.all()
    else:
        products = Product.objects.filter(user = request.user)
        if not products:
            messages.warning(request, "You have not added any products yet.")
            return redirect('store:home')
    return render(request, 'store/product_and_review.html', {'products': products})