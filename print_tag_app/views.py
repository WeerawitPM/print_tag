from django.shortcuts import render, redirect
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Tag, RefTag

@csrf_exempt
def index(request):
    data = []
    if request.method == 'POST':
        try:
            fccode = request.POST.get('fccode')  # Default value for testing
            po_no = request.POST.get('po_no')
            cust_sup = request.POST.get('cust_sup')
            lot_mat = request.POST.get('lot_mat')
            lot_prod = request.POST.get('lot_prod')
            model = request.POST.get('model')
            mc = request.POST.get('mc')
            date = request.POST.get('date')
            qty = request.POST.get('qty')
            print(f"Attempting to connect to the remote database with FCCODE: {fccode}")
                
            with connections['formula_aaa'].cursor() as cursor:
                query = "SELECT TOP 10 FCCODE, FCNAME FROM [Formula].[dbo].[PROD] WHERE FCCODE LIKE %s"
                cursor.execute(query, [f'%{fccode}%'])
                data = cursor.fetchall()
                    
                # Clean up the data by stripping leading and trailing whitespace
                cleaned_data = []
                for row in data:
                    cleaned_row = [field.strip() if isinstance(field, str) else field for field in row]
                    cleaned_data.append(cleaned_row)
                    
                print(f"Cleaned Data: {cleaned_data}")
                data = cleaned_data
                return render(request, 'home/index.html', 
                              {'fccode':fccode, 
                               'data': data, 
                               'po_no':po_no,
                               'cust_sup':cust_sup, 
                               'lot_mat':lot_mat, 
                               'lot_prod':lot_prod,
                               'model':model,
                               'mc':mc, 
                               'date':date, 
                               'qty':qty
                               })
        except Exception as e:
            print(f"Failed to connect to the remote database: {str(e)}")
    else :
        return render(request, 'home/index.html')

def autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        with connections['formula_aaa'].cursor() as cursor:
            cursor.execute("SELECT TOP 10 FCCODE FROM [Formula].[dbo].[PROD] WHERE FCCODE LIKE %s", [f'%{term}%'])
            results = cursor.fetchall()
            part_codes = [row[0].strip() for row in results]
        return JsonResponse(part_codes, safe=False)
    return JsonResponse([], safe=False)

@csrf_exempt
def save_selected(request):
    if request.method == 'POST':
        selected_indices = request.POST.getlist('selected')
        ref_tag = RefTag.objects.create()

        for index in selected_indices:
            index = int(index)  # Convert to 1-based index
            po_no = request.POST.get(f'po_no_{index}')
            cust_sup = request.POST.get(f'cust_sup_{index}')
            part_name = request.POST.get(f'part_name_{index}')
            part_no = request.POST.get(f'part_no_{index}')
            lot_mat = request.POST.get(f'lot_mat_{index}')
            lot_prod = request.POST.get(f'lot_prod_{index}')
            model = request.POST.get(f'model_{index}')
            mc = request.POST.get(f'mc_{index}')
            date = request.POST.get(f'date_{index}')
            qty = request.POST.get(f'qty_{index}')
            qr_code = f"{part_no}${qty}${po_no}${cust_sup}"
        
            Tag.objects.create(
                qr_code=qr_code,
                po_no=po_no,
                cust_sup=cust_sup,
                part_name=part_name,
                part_no = part_no,
                lot_mat=lot_mat,
                lot_prod=lot_prod,
                model=model,
                mc=mc,
                date=date,
                qty=qty,
                ref_tag=ref_tag
            )
        return redirect('/')
    return redirect('/')
