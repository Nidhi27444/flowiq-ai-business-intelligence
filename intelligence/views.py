import csv
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from .forms import SignupForm, UploadForm
from .models import Dataset
from .services import ImportValidationError, import_dataset, dataset_metrics, answer_question, ai_summary, automatic_insights, conversational_answer, ai_answer

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'registration/signup.html', {'form':form})

@login_required
def dashboard(request):
    datasets = Dataset.objects.filter(owner=request.user)
    selected = None
    if request.GET.get('dataset'):
        selected = get_object_or_404(datasets, pk=request.GET['dataset'])
    else:
        selected = datasets.first()
    metrics = dataset_metrics(selected) if selected else None
    return render(request, 'intelligence/dashboard.html', {
        'datasets': datasets, 'selected':selected, 'metrics':metrics,
        'auto_insights': automatic_insights(metrics) if metrics else [],
    })

@login_required
def upload(request):
    form = UploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        try:
            ds = import_dataset(request.user, form.cleaned_data['name'], form.cleaned_data['file'])
        except ImportValidationError as exc:
            form.add_error('file', str(exc))
        else:
            messages.success(request, f'Imported {ds.record_count} records successfully.')
            return redirect('dashboard')
    return render(request, 'intelligence/upload.html', {'form':form})

@login_required
@require_GET
def api_datasets(request):
    return JsonResponse({'datasets': list(Dataset.objects.filter(owner=request.user).values('id','name','record_count','uploaded_at'))})

@login_required
@require_GET
def api_metrics(request, pk):
    ds = get_object_or_404(Dataset, owner=request.user, pk=pk)
    return JsonResponse(dataset_metrics(ds))

@login_required
@require_POST
def api_ask(request, pk):
    ds = get_object_or_404(Dataset, owner=request.user, pk=pk)
    try:
        import json
        body = json.loads(request.body)
        question = body.get('question','')
        if not isinstance(question, str):
            return JsonResponse({'error':'Question must be text.'},status=400)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error':'Invalid JSON.'}, status=400)
    return JsonResponse({'answer':conversational_answer(question, ds), 'mode':'deterministic'})

@login_required
@require_POST
def api_ai_summary(request, pk):
    ds = get_object_or_404(Dataset, owner=request.user, pk=pk)
    try:
        summary = ai_summary(dataset_metrics(ds))
    except (ValueError, RuntimeError) as exc:
        return JsonResponse({'error':str(exc)}, status=400)
    return JsonResponse({'summary':summary, 'mode':'llm'})

@login_required
@require_GET
def export_report(request, pk):
    ds = get_object_or_404(Dataset, owner=request.user, pk=pk)
    metrics = dataset_metrics(ds)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="dataset_{ds.pk}_summary.csv"'
    writer = csv.writer(response)
    writer.writerow(['Metric','Value'])
    for key,value in metrics['kpis'].items():
        writer.writerow([key,value])
    for section in ('by_country','by_product','by_customer'):
        writer.writerow([])
        writer.writerow([section,'Revenue'])
        for item in metrics[section]:
            writer.writerow([item['name'],item['revenue']])
    writer.writerow([])
    writer.writerow(['by_year','Revenue'])
    for item in metrics['by_year']:
        writer.writerow([item['year'],item['revenue']])
    return response

@login_required
@require_POST
def delete_dataset(request, pk):
    ds = get_object_or_404(Dataset, owner=request.user, pk=pk)
    ds.delete()
    messages.success(request, 'Dataset deleted.')
    return redirect('dashboard')


@login_required
@require_POST
def api_ai_ask(request, pk):
    ds = get_object_or_404(Dataset, owner=request.user, pk=pk)
    try:
        import json
        body = json.loads(request.body)
        question = body.get('question','')
        if not isinstance(question,str):
            return JsonResponse({'error':'Question must be text.'},status=400)
        result = ai_answer(question,ds)
    except (ValueError, UnicodeDecodeError, RuntimeError) as exc:
        return JsonResponse({'error':str(exc)},status=400)
    return JsonResponse({'answer':result,'mode':'llm'})

@login_required
@require_GET
def api_insights(request,pk):
    ds = get_object_or_404(Dataset, owner=request.user, pk=pk)
    return JsonResponse({'insights':automatic_insights(dataset_metrics(ds)), 'mode':'computed'})
