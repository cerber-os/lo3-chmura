from chmura.subst import loadSubstiution, checkIfDateInFuture, SubstitutionException
# from chmura.timetable import loadTimeTable
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def webapi(request):
    api_type = request.GET.get('type', None)
    api_key = request.GET.get('api_key', None)
    api_version = request.GET.get('api_version', None)

    if not checkApiKey(api_key):
        raise Http404

    if api_version == '0.1dev':
        if api_type == 'substitution':
            answer = api_substitution(request)
        # elif api_type == 'timetable':
        #     answer = api_timetable(request)
        else:
            raise Http404

    return JsonResponse(answer)


def checkApiKey(api_key):
    return True if api_key == 'android_dev_app' else False


def api_substitution(request):
    date = request.GET.get('date', None)
    if date is None or not checkIfDateInFuture(date):
        raise Http404

    try:
        answer = {'substitution': loadSubstiution(date)}
    except SubstitutionException as e:
        answer = {'error': e.message}
    return answer
