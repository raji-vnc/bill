from django.urls import path
from. views import protected_view,save_bill
from django.contrib.auth import views as auth_views
from .import views

urlpatterns=[
    path('api/login/',views.admin_login,name='admin_login'),
    path('api/logout/',views.admin_logout,name='admin_logout'),
    path('dashboard/',views.dashboard,name='dashboard'),

    path('api/protected/', protected_view, name='protected'),
    path('api/save-bill/', save_bill, name='save_bill'),
    path('api/products/', views.product_list, name='product_list'),
    path('api/create-bill/', views.create_bill, name='create_bill'),
    path('api/edit-product/<int:id>/', views.edit_product, name='edit_product'),
    path('api/delete-product/<int:id>/', views.delete_product, name='delete_product'),
    path('api/bill-pdf/<int:bill_id>/', views.bill_pdf, name='bill_pdf'),
    path('api/add-product/', views.add_product, name='add_product'),
    path('api/bills/', views.get_bills, name='get_bills'),
    path('api/list-bill/<int:id>/', views.list_bill, name='list_bill'),
    path('api/bill-detail/<int:id>/', views.bill_detail, name='bill_detail'),
    path('api/view-bills/<int:id>/', views.view_bill, name='view_bill'),




    path('login_page/', views.login_page, name='login_page'),
    path('create-bill/', views.create_bill_page, name='create_bill_page'),
    path('view-bills/', views.view_bills_page, name='view_bills_page'),
    path('view-bills/<int:id>/', views.view_bills_page, name='view_bill'),

    
    
]