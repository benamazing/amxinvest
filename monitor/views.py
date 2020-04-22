from django.shortcuts import render

# Create your views here.

from django.views import View
from django.http import HttpResponse, Http404, JsonResponse
from django.core import serializers
from .models import StockMonitor
import json

class MonitorListView(View):
    def get(self, request):
        data = {}
        try:
            objs = StockMonitor.objects.all()
            data['data'] = [{'code': s.code, 'name': s.code, 'hold': s.hold, 'raise_ratio': s.raise_ratio, 'drop_ratio': s.drop_ratio} for s in objs]
            data['result'] = 'ok'
            return JsonResponse(data, safe=False)
        except Exception as e:
            data['result'] = 'err'
            data['err_msg'] = str(e)
            return JsonResponse(data, safe=False)



