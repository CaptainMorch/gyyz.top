from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from doofen.models import Student

def prelogin(request):
    response = dict()
    data = request.GET
    cls_id = '851001' + str(int(data.get('grade')[-2:])-3) + \
            data.get('cls').zfill(3)
    try:
        student = Student.objects.get(
                classnum__class_id=cls_id,
                name=data.get('name')
                )
    except ObjectDoesNotExist:
        response['success'] = False
    else:
        response['success'] = True
        response['has_pwd'] = student.has_passwd

    return JsonResponse(response)
