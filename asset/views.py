import json
from asset.dashboard import AssetDashboard
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from asset import core, models, asset_handle, utils, admin, table
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@csrf_exempt
@utils.token_required
def asset_report(request):
    print(request.GET)
    if request.method == 'POST':
        ass_handler = core.Asset(request)
        if ass_handler.data_is_valid():
            print("----asset data valid:")
            ass_handler.data_inject()
        return HttpResponse(json.dumps(ass_handler.response))
    return HttpResponse('--test--')


@csrf_exempt
def asset_with_no_asset_id(request):
    if request.method == 'POST':
        ass_handler = core.Asset(request)
        res = ass_handler.get_asset_id_by_sn()
        return HttpResponse(json.dumps(res))


def new_assets_approval(request):
    if request.method == 'POST':
        request.POST = request.POST.copy()
        approved_asset_list = request.POST.getlist('approved_asset_list')
        approved_asset_list = models.NewAssetApprovalZone.objects.filter(id__in=approved_asset_list)

        response_dic = {}
        for obj in approved_asset_list:
            request.POST['asset_data'] = obj.data
            ass_handler = core.Asset(request)
            if ass_handler.data_is_valid_without_id():
                ass_handler.data_inject()
                obj.approved = True
                obj.save()

            response_dic[obj.id] = ass_handler.response
        return render(request, 'assets/new_assets_approval.html',
                      {'new_assets': approved_asset_list, 'response_dic': response_dic})
    else:
        ids = request.GET.get('ids')
        id_list = ids.split(',')
        new_assets = models.NewAssetApprovalZone.objects.filter(id__in=id_list)
        return render(request, 'assets/new_assets_approval.html', {'new_assets': new_assets})


def asset_report_test(request):
    return render(request, 'assets/asset_report_test.html')


@login_required
def acquire_asset_id_test(request):
    return render(request, 'assets/acquire_asset_id_test.html')


@login_required
def get_asset_list(request):
    asset_dic = asset_handle.fetch_asset_list()
    print(asset_dic)

    return HttpResponse(json.dumps(asset_dic, default=utils.json_date_handler))


@login_required
def asset_category(request):
    category_type = request.GET.get("category_type")
    if not category_type:
        category_type = 'server'
    if request.is_ajax():
        categories = asset_handle.AssetCategroy(request)
        data = categories.serialize_data()
        return HttpResponse(data)
    else:
        return render(request,
                      'assets/asset_category.html',
                      {'category_type': category_type})


@login_required
def asset_event_logs(request, asset_id):
    if request.method == "GET":
        log_list = asset_handle.fetch_asset_event_logs(asset_id)
        return HttpResponse(json.dumps(log_list, default=utils.json_datetime_handler))


@login_required
def asset_detail(request, asset_id):
    if request.method == "GET":
        try:
            asset_obj = models.Asset.objects.get(id=asset_id)

        except ObjectDoesNotExist as e:
            return render(request, 'assets/asset_detail.html', {'error': e})
        return render(request, 'assets/asset_detail.html', {"asset_obj": asset_obj})


@login_required
def get_dashboard_data(request):
    # 返回主页面数据

    dashboard_data_obj = AssetDashboard(request)
    dashboard_data_obj.searilize_page()
    return HttpResponse(json.dumps(dashboard_data_obj.data))
