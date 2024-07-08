from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.utils import timezone
from .models import Employee, shiiregyosha, paitent, medicine, Treatment
from django.contrib import messages
from django.db.models import Q
import re
from datetime import datetime


def index(request):
    return render(request, 'login_screen.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            employee = Employee.objects.get(empid=username, emppasswd=password)
            request.session['empid'] = employee.empid  # empidをセッションに保持
            if employee.emprole == 0:  # ユーザーが管理者の場合
                return render(request, 'home_screen/administrator.html')  # 管理者メニュー画面へのURLを指定
            elif employee.emprole == 1:
                return render(request, 'home_screen/employee_reception.html')  # 受付メニュー画面へのURLを指定
            elif employee.emprole == 2:
                return render(request, 'home_screen/employee_doctor.html')  # 医師メニュー画面へのURLを指定
        except Employee.DoesNotExist:
            error_message = "ユーザーが見つかりませんでした。"
            return render(request, 'error/login_error.html', {'error_message': error_message})

    return render(request, 'login_screen.html')  # ログアウト時の画面へのURLを指定


def registration_view(request):
    if request.method == 'POST':
        empid = request.POST['empid']
        empfname = request.POST['empfname']
        emplname = request.POST['emplname']
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']
        emprole = request.POST['emprole']

        # Convert emprole to an integer
        try:
            emprole = int(emprole)
        except ValueError:
            error_message = "無効なロールが選択されました。"
            return render(request, 'administrator/employee_registration.html', {'error_message': error_message})

        if password != confirmPassword:
            error_message = "パスワードが一致しません。"
            return render(request, 'administrator/employee_registration.html', {'error_message': error_message})

        if Employee.objects.filter(empid=empid).exists():
            error_message = "このユーザーIDは既に登録されています。"
            return render(request, 'administrator/employee_registration.html', {'error_message': error_message})

        if emprole == 0 and Employee.objects.filter(emprole=0).count() > 4:
            error_message = "管理者は5人までです。"
            return render(request, 'administrator/employee_registration.html', {'error_message': error_message})

        # Validate emprole
        if emprole not in [0, 1, 2]:
            error_message = "無効なロールが選択されました。"
            return render(request, 'administrator/employee_registration.html', {'error_message': error_message})

        Employee.objects.create(
            empid=empid,
            empfname=empfname,
            emplname=emplname,
            emppasswd=password,
            emprole=emprole
        )

        success_message = "従業員が正常に登録されました。"
        return render(request, 'administrator/employee_registration.html', {'success_message': success_message})

    return render(request, 'administrator/employee_registration.html')


def is_admin(user):
    return user.groups.filter(name='管理者').exists()


def shiiregyosha_view(request):
    shiiregyosha_data = shiiregyosha.objects.all()
    return render(request, 'administrator/company_TBL_screen.html', {'shiiregyosha_data': shiiregyosha_data})


def change_supplier_phone(request, supplier_id):
    supplier = get_object_or_404(shiiregyosha, shiireid=supplier_id)
    if request.method == 'POST':
        new_phone = request.POST.get('supplier_phone')
        # 修正された正規表現パターン
        if not re.match(r'^\(?\d{2,5}\)?-?\d{4}-?\d{4}$', new_phone):
            error_message = "電話番号は10~12桁で正しい形式で入力してください。例：(03)-1234-5678, 03-1234-5678, 0-0000-0000"
            return render(request, 'administrator/company_number_change_screen.html', {'supplier_id': supplier_id, 'error_message': error_message})

        supplier.shiiretel = new_phone
        try:
            supplier.save()
            confirmation_message = "電話番号が変更されました。"
            return render(request, 'administrator/company_number_change_screen.html', {'supplier_id': supplier_id, 'confirmation_message': confirmation_message})
        except Exception as e:
            error_message = f"電話番号の変更中にエラーが発生しました: {str(e)}"
            return render(request, 'administrator/company_number_change_screen.html', {'supplier_id': supplier_id, 'error_message': error_message})
    else:
        return render(request, 'administrator/company_number_change_screen.html', {'supplier_id': supplier_id})

def search_supplier_by_capital(request):
    if request.method == 'POST':
        capital_input = request.POST.get('capital', '').strip()

        # 全角数字、全角カンマ、全角￥を半角に変換
        capital_input = capital_input.translate(str.maketrans('０１２３４５６７８９，￥', '0123456789,¥'))

        # 半角カンマ、半角￥、半角バックスラッシュを削除
        capital_input = capital_input.replace(',', '').replace('¥', '').replace('\\', '')

        # 入力が空の場合はエラーメッセージを表示
        if not capital_input:
            messages.error(request, "資本金を入力してください。")
            return redirect('search_supplier_by_capital')

        # 正規表現で数字以外の文字が含まれているかチェック
        if not re.match(r'^\d+$', capital_input):
            messages.error(request, "資本金は数字で入力してください。")
            return redirect('search_supplier_by_capital')

        try:
            capital = int(capital_input)
            suppliers = shiiregyosha.objects.filter(shihonkin__gte=capital)
            if not suppliers.exists():
                messages.error(request, "検索結果が0件。")
                return redirect('search_supplier_by_capital')
            return render(request, 'administrator/company_TBL_screen.html',
                          {'shiiregyosha_data': suppliers, 'capital': capital})
        except ValueError:
            messages.error(request, "指定以外の文字が含まれています。")
            return redirect('search_supplier_by_capital')
    else:
        return render(request, 'administrator/company_TBL_screen.html')

def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # パスワードの一致を確認
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'administrator/employee_password_change.html')

        # パスワードが空欄かどうかを確認
        if not new_password:
            messages.error(request, "新しいパスワードを入力してください。")
            return render(request, 'administrator/employee_password_change.html')

        # 管理者か従業員かで処理を分岐
        if is_admin(request.user):
            # 管理者の場合はユーザーIDを取得して変更
            user_id = request.POST.get('user_id')  # HTMLフォームからユーザーIDを取得する必要があります
            try:
                employee = Employee.objects.get(empid=user_id)
                employee.emppasswd = new_password
                employee.save()
                messages.success(request, "変更しました。")
            except Employee.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            # 従業員の場合は自身のパスワードを変更
            empid = request.session['empid']
            try:
                employee = Employee.objects.get(empid=empid)
                employee.emppasswd = new_password
                employee.save()
                messages.success(request, "変更しました。")  #成功時のメッセージ
            except Employee.DoesNotExist:
                messages.error(request, "User not found.")
        return redirect('change_password')  # 任意のリダイレクト先を指定
    return render(request, 'administrator/employee_password_change.html')


def admin_home(request):
    return render(request, 'home_screen/administrator.html')


def employee_change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        # パスワードの一致を確認
        if new_password != confirm_password:
            messages.error(request, "新しいパスワードが一致しません。")
            return render(request, 'employee1/reception/employee_change_screen.html')
        # パスワードが空欄かどうかを確認
        if not new_password:
            messages.error(request, "新しいパスワードを入力してください。")
            return render(request, 'employee1/reception/employee_change_screen.html')
        # パスワードを変更する
        empid = request.session['empid']
        try:
            employee = Employee.objects.get(empid=empid)
            employee.emppasswd = new_password
            employee.save()
            messages.success(request, "変更しました。")
            return render(request, 'employee1/reception/employee_change_screen.html')
        except Employee.DoesNotExist:
            messages.error(request, "User not found.")
    return render(request, 'employee1/reception/employee_change_screen.html')


#受付
def patient_home(request):
    return render(request, 'home_screen/employee_reception.html')


def patient_registration_view(request):
    if request.method == 'POST':
        patid = request.POST.get('patid')
        patfname = request.POST.get('patfname')
        patlneme = request.POST.get('patlneme')
        hokenmei = request.POST.get('hokenmei')
        hokenexp = request.POST.get('hokenexp')

        # バリデーションチェック
        errors = {}

        # 患者IDの重複チェック
        if paitent.objects.filter(patid=patid).exists():
            errors['patid'] = 'この患者IDは既に登録されています。別のIDを使用してください。'

        # 保険名の桁数チェック
        if len(hokenmei) != 10:
            errors['hokenmei'] = '保険名は10桁でなければなりません。'

        # エラーがある場合は入力画面に戻る
        if errors:
            return render(request, 'employee1/reception/patient_registration.html', {
                'errors': errors,
                'patid': patid,
                'patfname': patfname,
                'patlneme': patlneme,
                'hokenmei': hokenmei,
                'hokenexp': hokenexp,
            })

        # エラーがなければ確認画面に遷移
        return render(request, 'employee1/reception/patient_registration_confirm.html', {
            'patid': patid,
            'patfname': patfname,
            'patlneme': patlneme,
            'hokenmei': hokenmei,
            'hokenexp': hokenexp,
        })

    # GETリクエストの場合は入力画面を表示
    return render(request, 'employee1/reception/patient_registration.html')

def patient_registration_confirm_view(request):
    if request.method == 'POST':
        patid = request.POST.get('patid')
        patfname = request.POST.get('patfname')
        patlneme = request.POST.get('patlneme')
        hokenmei = request.POST.get('hokenmei')
        hokenexp = request.POST.get('hokenexp')

        # 患者IDの重複チェック（実際には重複しないようにシステム側で管理が必要）
        if paitent.objects.filter(patid=patid).exists():
            error_message = "この患者IDは既に登録されています。"
            return render(request, 'employee1/reception/patient_registration.html', {'error_message': error_message})

        # 保険名の重複チェック（実際には重複しないようにシステム側で管理が必要）
        if paitent.objects.filter(hokenmei=hokenmei).exists():
            error_message = "この保険証記号番号は既に登録されています。"
            return render(request, 'employee1/reception/patient_registration.html', {'error_message': error_message})

        # データベースに登録
        paitent.objects.create(
            patid=patid,
            patfname=patfname,
            patlneme=patlneme,
            hokenmei=hokenmei,
            hokenexp=hokenexp,
        )

        # 登録成功メッセージを表示して入力画面に戻る
        success_message = "患者が正常に登録されました。"
        return render(request, 'employee1/reception/patient_registration.html', {'success_message': success_message})

    # POSTリクエスト以外の場合は入力画面にリダイレクト
    return redirect('patient_registration')

def is_receptionist(user):
    return user.groups.filter(name='受付').exists()


def patient_list_view(request):
    paitent_data = paitent.objects.all()
    current_user_role = None

    if 'empid' in request.session:
        try:
            current_user = Employee.objects.get(empid=request.session['empid'])
            current_user_role = current_user.emprole
        except Employee.DoesNotExist:
            pass

    return render(request, 'employee1/reception/paitent_list.html',
                  {'paitent_data': paitent_data, 'current_user_role': current_user_role})


def change_patient_info(request, patient_id):
    patient = get_object_or_404(paitent, patid=patient_id)  # Patientモデルに対するget_object_or_404の利用

    if request.method == 'POST':
        new_hokenmei = request.POST.get('hokenmei')
        new_hokenexp_str = request.POST.get('hokenexp')

        if new_hokenmei:
            patient.hokenmei = new_hokenmei

        if new_hokenexp_str:
            try:
                new_hokenexp = datetime.strptime(new_hokenexp_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "日付の形式が正しくありません。YYYY-MM-DD形式で入力してください。")
                return render(request, 'employee1/reception/paitent_hoken_change.html', {'patient_id': patient_id})

            if new_hokenexp < patient.hokenexp:
                messages.error(request, "新しい有効期限は現在の有効期限よりも古い日付にすることはできません。")
                return render(request, 'employee1/reception/paitent_hoken_change.html', {'patient_id': patient_id})
            elif new_hokenexp == patient.hokenexp:
                messages.error(request, "新しい有効期限と現在の有効期限を同じ日付にすることはできません。")
                return render(request, 'employee1/reception/paitent_hoken_change.html', {'patient_id': patient_id})
            else:
                patient.hokenexp = new_hokenexp

        else:
            # 日付が入力されていない場合のエラー処理
            messages.error(request, "有効期限を入力してください。")
            return render(request, 'employee1/reception/paitent_hoken_change.html', {'patient_id': patient_id})

        patient.save()
        messages.success(request, "保険証情報が変更されました。")
        return redirect('change_patient_info', patient_id=patient_id)

    else:
        return render(request, 'employee1/reception/paitent_hoken_change.html', {'patient_id': patient_id})

def search_patient_by_name(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name').strip()

        # 入力された患者名がスペースで区切られている場合、姓と名に分割する
        names = patient_name.split()
        if len(names) == 2:
            first_name, last_name = names
            paitent_data = paitent.objects.filter(
                Q(patfname__icontains=first_name) & Q(patlneme__icontains=last_name)
            ) | paitent.objects.filter(
                Q(patfname__icontains=last_name) & Q(patlneme__icontains=first_name)
            )
        else:
            paitent_data = paitent.objects.filter(
                Q(patfname__icontains=patient_name) | Q(patlneme__icontains=patient_name)
            )

        current_user_role = None
        if 'empid' in request.session:
            try:
                current_user = Employee.objects.get(empid=request.session['empid'])
                current_user_role = current_user.emprole
            except Employee.DoesNotExist:
                pass

        if not paitent_data.exists():
            messages.error(request, "該当する患者が見つかりません。")

        return render(request, 'employee1/reception/paitent_list.html',
                      {'paitent_data': paitent_data, 'current_user_role': current_user_role, 'query': patient_name})
    else:
        return HttpResponse("無効なリクエストです。")


def check_expiration_date(request):
    today = timezone.now().date()
    expired_patients = paitent.objects.filter(hokenexp__lt=today)
    return render(request, 'employee1/reception/paitent_Check_expiration_date.html',
                  {'expired_patients': expired_patients})


#医師
def doctor_home(request):
    return render(request, 'home_screen/employee_doctor.html')


def is_receptionist(user):
    return user.groups.filter(name='医師').exists()


def patient2_list_view(request):
    paitent_data = paitent.objects.all()
    return render(request, 'employee1/reception/paitent_list.html', {'paitent_data': paitent_data})


def prescribe_medicine(request):
    if request.method == 'POST':
        patid = request.POST.get('patid')
        medicineid = request.POST.get('medicineid')
        dosage = request.POST.get('dosage')
        empid = request.POST.get('empid')

        if not patid or not medicineid or not dosage:
            messages.error(request, '全てのフィールドを入力してください。')
            return redirect('prescribe_medicine')

        try:
            patient_data = paitent.objects.get(patid=patid)
            medicine_data = medicine.objects.get(medicineid=medicineid)
        except paitent.DoesNotExist:
            error_message = '指定された患者が見つかりません。'
            medicines = medicine.objects.all()
            return render(request, 'employee1/doctor/prescribe_medicine.html', {'error_message': error_message,
                'medicines': medicines})
        except medicine.DoesNotExist:
            error_message = '指定された薬が見つかりません。'
            return render(request, 'employee1/doctor/prescribe_medicine.html', {'error_message': error_message})

        # カートに追加するデータをセッションに保存
        cart_item = {
            'patid': patid,
            'patlneme': patient_data.patlneme,
            'patfname': patient_data.patfname,
            'medicinid': medicineid,
            'medicinename': medicine_data.medicinename,
            'dosage': dosage,
            'medicineid': medicineid,
            'empid': empid,
        }
        # セッションからカートリストを取得し、新しいアイテムを追加
        cart = request.session['cartlist']
        cart.append(cart_item)

        # 更新されたカートリストをセッションに保存
        request.session['cartlist'] = cart

        return redirect('cartlist_view')

    medicines = medicine.objects.all()
    return render(request, 'employee1/doctor/prescribe_medicine.html', {'medicines': medicines})


def prescription_list(request):
    treatment_list = Treatment.objects.all()
    return render(request, 'employee1/doctor/prescription_list.html', {'treatment_list': treatment_list})

def cartlist_view(request):
    cart = request.session.get('cartlist', [])
    for index, item in enumerate(cart):
        item['cart_id'] = index  # カートアイテムに一意の cart_id を割り当てる
    request.session['cartlist'] = cart
    return render(request, 'employee1/doctor/cartlist.html', {'cart': cart})

def remove_from_cart(request, cart_id):
    cart = request.session.get('cartlist', [])
    updated_cart = [item for item in cart if item['cart_id'] != cart_id]
    request.session['cartlist'] = updated_cart
    return redirect('cartlist_view')

def confirm_procedure(request):
    cart = request.session.get('cartlist', [])
    request.session['cartlist'] = cart
    return render(request, 'employee1/doctor/confirm_treatment.html', {'cart': cart})

def confirm_treatment(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            # カートのリストを空にする
            request.session['cartlist'] = []
            messages.success(request, "カートのリストを空にしました。")
            return redirect('cartlist_view')  # 薬剤選択画面にリダイレクトする

        # カートの処置を確定する処理
        cart = request.session.get('cartlist', [])
        if cart:
            for item in cart:
                try:
                    patient = paitent.objects.get(patid=item['patid'])
                    employee = Employee.objects.get(empid=request.session.get('empid'))
                    medicine_data = medicine.objects.get(medicineid=item['medicineid'])
                    Treatment.objects.create(
                        patid=patient,
                        medicineid=medicine_data,
                        dosage=item['dosage'],
                        empid=employee
                    )
                except (paitent.DoesNotExist, Employee.DoesNotExist, medicine.DoesNotExist) as e:
                    messages.error(request, "処置を確定できませんでした。{}".format(str(e)))
                    return redirect('cartlist_view')

            # カートを空にする
            request.session['cartlist'] = []
            messages.success(request, "処置が確定されました。")
            return redirect('cartlist_view')
        else:
            messages.error(request, "カートが空です。処置を追加してください。")
            return redirect('cartlist_view')

    # ポストリクエスト以外の場合は、単にカートの内容を表示するだけです。
    cart_items = request.session.get('cartlist', [])
    return render(request, 'employee1/doctor/confirm_treatment.html', {'cart_items': cart_items})

def treatment_history(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')

        if not patient_id:
            return render(request, 'employee1/doctor/treatment_history.html', {'error_message': '患者IDを入力してください。'})

        try:
            patient = paitent.objects.get(patid=patient_id)
        except paitent.DoesNotExist:
            return render(request, 'employee1/doctor/treatment_history.html', {'error_message': '登録されていない患者IDです。'})

        treatments = Treatment.objects.filter(patid=patient)

        if not treatments.exists():
            return render(request, 'employee1/doctor/treatment_history.html', {'error_message': '該当する処置履歴がありません。', 'patient': patient})

        return render(request, 'employee1/doctor/treatment_history.html', {'patient': patient, 'treatments': treatments})

    return render(request, 'employee1/doctor/treatment_history.html')

def cartlist_search(request):
    search_query = request.GET.get('search', '').strip()
    cart_items = request.session.get('cartlist', [])  # キーを 'cartlist' に修正

    if search_query:
        filtered_cart = []
        for item in cart_items:
            # 患者IDまたは姓、名のどちらかを含む場合にフィルタリングする例
            if (str(item.get('patid')) == search_query or
                    search_query in item.get('patlneme', '') or
                    search_query in item.get('patfname', '')):
                filtered_cart.append(item)
    else:
        filtered_cart = cart_items

    # フィルタリング結果が空の場合のメッセージを設定
    if not filtered_cart:
        error_message = "該当する患者はいません。"
    else:
        error_message = ""

    context = {
        'cart': filtered_cart,
        'search_query': search_query,
        'error_message': error_message,
    }
    return render(request, 'employee1/doctor/cartlist.html', context)