# from chmura.subst import get_substitution
# # from chmura.timetable import get_timetable
# from datetime import datetime
# from django.http import JsonResponse, Http404
# from django.views.decorators.csrf import csrf_exempt
#
#
# @csrf_exempt
# def webapi(request):
#     api_type = request.POST.get('type', None)
#     api_key = request.POST.get('api_key', None)
#
#     if api_key != 'android_dev_app':
#         raise Http404
#
#     if api_type == 'substitution':
#         answer = api_substitution(request)
#     # elif api_type == 'timetable':
#     # answer = api_timetable(request)
#     else:
#         raise Http404
#
#     return JsonResponse(answer)
#
#
# def api_substitution(request):
#     now = datetime.now()
#     now = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
#     reqDate = request.POST.get('date', now)
#
#     answer = {'substitution': get_substitution(reqDate),
#               'date':         reqDate, }
#     return answer
