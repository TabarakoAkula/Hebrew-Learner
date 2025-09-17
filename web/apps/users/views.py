from apps.users import tasks
from apps.users.models import User
from apps.users.serializers import UserSerializer
from rest_framework.views import APIView, Response


class UserGetCreateView(APIView):
    @staticmethod
    def get(request, telegram_id: str):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({"success": False, "message": "User does not exists"})
        serializer = UserSerializer(user)
        return Response({"success": True, "data": serializer.data})

    @staticmethod
    def post(request, telegram_id: str):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            telegram_username = request.data.get("telegram_username", "")
            serializer = UserSerializer(
                data={
                    "telegram_id": telegram_id,
                    "telegram_username": telegram_username,
                }
            )
            if serializer.is_valid():
                serializer.save()
                data = serializer.data
                data["New"] = True
            else:
                return Response(
                    {
                        "success": False,
                        "message": "⚠️ Unknown error on creating new user",
                        "data": serializer.errors,
                    },
                )
        else:
            serializer = UserSerializer(user)
            data = serializer.data
            data["New"] = False
        return Response({"success": True, "data": data})

    @staticmethod
    def put(request, telegram_id: str):
        try:
            request_telegram_id = request.data["telegram_id"]
            user = User.objects.get(telegram_id=telegram_id)
        except KeyError:
            return Response(
                {
                    "success": False,
                    "message": "You must provide telegram_id in request body",
                },
            )
        except User.DoesNotExist:
            return Response({"success": False, "message": "User does not exists"})
        if request_telegram_id != telegram_id:
            return Response(
                {
                    "success": False,
                    "message": "Telegram ids in request and in url are"
                    " different (two equals strings)",
                },
            )
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "message": serializer.errors})


class SendReportAPIView(APIView):
    @staticmethod
    def post(request, telegram_id: str):
        tasks.manager_snitch_logs(
            {
                "telegram_id": telegram_id,
                "telegram_username": request.data.get("telegram_username", ""),
                "message": request.data.get("message", " empty message"),
            }
        )
        return Response({"success": True})
