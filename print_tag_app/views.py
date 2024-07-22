from django.shortcuts import render
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def index(request):
    data = []
    if request.method == 'POST':
        try:
            fccode = request.POST.get('fccode')  # Default value for testing
            supplier = request.POST.get('supplier')
            model = request.POST.get('model')
            packing = request.POST.get('packing')
            print(f"Attempting to connect to the remote database with FCCODE: {fccode}")
                
            with connections['formula_aaa'].cursor() as cursor:
                query = "SELECT TOP 10 FCSKID, FCCODE, FCNAME, FCSNAME FROM [Formula].[dbo].[PROD] WHERE FCCODE LIKE %s"
                cursor.execute(query, [f'%{fccode}%'])
                data = cursor.fetchall()
                    
                # Clean up the data by stripping leading and trailing whitespace
                cleaned_data = []
                for row in data:
                    cleaned_row = [field.strip() if isinstance(field, str) else field for field in row]
                    cleaned_data.append(cleaned_row)
                    
                print(f"Cleaned Data: {cleaned_data}")
                data = cleaned_data
                return render(request, 'home/index.html', {'fccode':fccode, 'data': data, 'supplier': supplier, 'model': model, 'packing': packing})
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