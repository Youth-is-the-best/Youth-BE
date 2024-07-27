from rest_framework.views import APIView
from .permissions import IsAdminOrReadOnly
from .models import Information, InformationImage

# Create your views here.
class InformationView(APIView):
    queryset = Information.objects.all()