from django.shortcuts import HttpResponse
import json

def return_json(dict_obj, status=200):
    resp = HttpResponse(json.dumps(dict_obj), status=status, content_type="application/json")
    resp['Access-Control-Allow-Origin'] = "*"
    return resp

