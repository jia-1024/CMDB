from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from assets import models
from assets.utils import asset_handler
from django.shortcuts import get_object_or_404


# Create your views here.

@csrf_exempt
def report(request):
    """
    通过csrf_exempt装饰器，跳过Django的csrf安全机制，让post的数据能被接收，但这又会带来新的安全问题。
    可以在客户端，使用自定义的认证token，进行身份验证。
    :param request:
    :return:
    """
    if request.method == 'POST':
        asset_data = request.POST.get('asset_data')  # asset_data为json字符串，需转换为python字典类型进行处理
        data = json.loads(asset_data)
        # 校验数据
        if not data:
            return HttpResponse('未收到任何数据')
        if not isinstance(data, (dict,)):
            return HttpResponse('数据格式发生错误')
        if 'sn' not in data.keys():
            return HttpResponse('资产序列号不明,请检查数据')

        sn = data['sn']
        new_asset = models.Asset.objects.filter(sn=sn)
        if new_asset:
            # TODO 如果已经存在就将提交的信息更新到数据库
            update_asset = asset_handler.UpdateAsset(request, new_asset[0], data)

            return HttpResponse('已经更新该资产')

        obj = asset_handler.NewAsset(request, data)
        if obj.exist_assets_zone():
            response = obj.exist_assets_zone()
            return HttpResponse(response)
        response = obj.add_to_new_assets_zone()
        return HttpResponse(response)
    return HttpResponse('<h1>用GET请求测试整个逻辑已连通</h1>')


def dashboard(request):
    total = models.Asset.objects.count()
    upline = models.Asset.objects.filter(status=0).count()
    offline = models.Asset.objects.filter(status=1).count()
    unknown = models.Asset.objects.filter(status=2).count()
    breakdown = models.Asset.objects.filter(status=3).count()
    backup = models.Asset.objects.filter(status=4).count()
    up_rate = round(upline / total * 100)
    o_rate = round(offline / total * 100)
    un_rate = round(unknown / total * 100)
    bd_rate = round(breakdown / total * 100)
    bu_rate = round(backup / total * 100)
    server_number = models.Server.objects.count()
    networkdevice_number = models.NetworkDevice.objects.count()
    storagedevice_number = models.StorageDevice.objects.count()
    securitydevice_number = models.SecurityDevice.objects.count()
    software_number = models.Software.objects.count()

    return render(request, 'assets/dashboard.html', locals())


def index(request):
    assets = models.Asset.objects.all()
    return render(request, 'assets/index.html', locals())


def detail(request, asset_id):
    """
    以显示服务器类型资产详细为例，安全设备、存储设备、网络设备等参照此例。
    :param request:
    :param asset_id:
    :return:
    """
    asset = get_object_or_404(models.Asset, pk=asset_id)
    return render(request, 'assets/detail.html', locals())
