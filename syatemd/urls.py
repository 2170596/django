from django.urls import path
from .views import index, login_view, registration_view, shiiregyosha_view, change_supplier_phone, \
    search_supplier_by_capital, change_password, admin_home, employee_change_password, patient_registration_view, \
    patient_registration_confirm_view, patient_list_view, change_patient_info, patient_home, \
    check_expiration_date, doctor_home, patient2_list_view, search_patient_by_name, prescribe_medicine, \
    prescription_list, cartlist_view, remove_from_cart, confirm_treatment, confirm_procedure, treatment_history, cartlist_search

urlpatterns = [
    path('', index, name='home'),
    path('login/', login_view, name='login'),
    path('registration/', registration_view, name='registration'),  # 管理者↓
    path('shiiregyosha_list/', shiiregyosha_view, name='shiiregyosha_list'),
    path('shiiregyosha_list/change_phone/<int:supplier_id>/', change_supplier_phone, name='change_supplier_phone'),  # 仕入れ先のIDを受け取るためのパス
    path('shiiregyosha_list/search_by_capital/', search_supplier_by_capital, name='search_supplier_by_capital'),
    path('change_password/', change_password, name='change_password'),  # パスワード変更機能のURLパス
    path('admin_home/', admin_home, name='admin_home'),
    path('employee_change_password/', employee_change_password, name='employee_change_password'),
    path('patient_home/', patient_home, name='patient_home'),   # 受付↓
    path('patient_registration/', patient_registration_view, name='patient_registration'),  #患者受付登録入力
    path('patient_registration_confirm/', patient_registration_confirm_view, name='patient_registration_confirm'),  #患者受付登録確認
    path('patient_list/', patient_list_view, name='patient_list'),
    path('patient_list/change_info/<str:patient_id>/', change_patient_info, name='change_patient_info'),
    path('patient_list/search_by_name/', search_patient_by_name, name='search_patient_by_name'),
    path('check_expiration_date/', check_expiration_date, name='check_expiration_date'),
    path('doctor_home/', doctor_home, name='doctor_home'),  # 医師↓
    path('patient2_list/', patient2_list_view, name='patient2_list'),
    path('prescribe_medicine/', prescribe_medicine, name='prescribe_medicine'),
    path('prescription_list/', prescription_list, name='prescription_list'),
    path('cartlist/', cartlist_view, name='cartlist_view'),
    path('remove_from_cart/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),
    path('confirm_procedure/', confirm_procedure, name='confirm_procedure'),
    path('confirm_treatment/', confirm_treatment, name='confirm_treatment'),
    path('treatment_history/', treatment_history, name='treatment_history'),
    path('cartlist_search/', cartlist_search, name='cartlist_search'),
]
