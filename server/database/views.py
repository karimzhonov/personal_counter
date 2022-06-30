import json
from datetime import timedelta
from django.http import JsonResponse
from compare_face.cv2 import base64_to_numpy
from compare_face.compare_face import find_faces
from .models import Visit


def face_recognize(request):
    try:
        data = json.loads(request.body.decode())
        image = base64_to_numpy(data['image'])
        _, personals = find_faces(image)
        data = {"profiles": []}
        for personal in personals:
            personal_visits = Visit.objects.filter(personal_id=personal.id).order_by("-visit_at")
            last_visit = personal_visits[1] if len(personal_visits) > 1 else None
            data["profiles"].append({
                "id": personal.id,
                "fullname": personal.get_fullname(),
                "visit_count": len(personal_visits),
                "last_visit": last_visit.visit_at
                .replace(microsecond=0, tzinfo=None) + timedelta(hours=3) if last_visit is not None else "First visit",
                "image": last_visit.personal.get_image() if last_visit is not None else personal.get_image(),
            })
        return JsonResponse(data)
    except json.JSONDecodeError:
        return JsonResponse({})
