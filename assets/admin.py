from django.contrib import admin
# Register your models here.
from assets.utils import asset_handler
from assets import models
from django.contrib.admin import helpers


class NewAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_type', 'sn', 'model', 'manufacturer', 'c_time', 'm_time')
    list_filter = ('asset_type', 'manufacturer', 'c_time')
    search_fields = ('sn',)

    actions = ['approve_selected_new_assets']

    def approve_selected_new_assets(self, request, queryset):
        # 获得被checkbox的对应资产对象
        selected = request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME)
        success_upline_number = 0
        for asset_id in selected:

            obj = asset_handler.ApproveAsset(request=request, asset_id=asset_id)

            ret = obj.asset_upline()
            if ret:
                success_upline_number += 1
        self.message_user(request=request, message='成功批准[{}]项资产上线'.format(success_upline_number))

    approve_selected_new_assets.short_description = '将全部选定打钩的资产批准上线'


class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_type', 'name', 'status', 'approved_by', 'c_time', "m_time"]


admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Server)
admin.site.register(models.StorageDevice)
admin.site.register(models.SecurityDevice)
admin.site.register(models.BusinessUnit)
admin.site.register(models.Contract)
admin.site.register(models.CPU)
admin.site.register(models.Disk)
admin.site.register(models.EventLog)
admin.site.register(models.IDC)
admin.site.register(models.Manufacturer)
admin.site.register(models.NetworkDevice)
admin.site.register(models.NIC)
admin.site.register(models.RAM)
admin.site.register(models.Software)
admin.site.register(models.Tag)
admin.site.register(models.NewAssetApprovalZone, NewAssetAdmin)
