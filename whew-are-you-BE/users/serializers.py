from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework import serializers
from .models import CustomUser, Verif
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

# 회원가입 시리얼라이저
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, validators=[validate_password]) # 적절한 비밀번호인지 체크(너무 쉬운 비밀번호 방지)
    username = serializers.CharField(required=True)
    hash = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    university = serializers.CharField(required=True)
    college = serializers.CharField(required=False)
    major = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['password', 'username', 'hash', 'first_name', 'university', 'college', 'major']

    def save(self, request):
        email_hash = self.validated_data['hash']
        verif_object = Verif.objects.filter(hash=email_hash, is_fulfilled=True)
        assert(verif_object.count() == 1)
        email = verif_object.get().email

        user = CustomUser.objects.create(
            username=self.validated_data['username'],
            email=email,
            first_name=self.validated_data['first_name'],
            university=self.validated_data['university'],
            college = self.validated_data.get('college', None),
            major = self.validated_data.get('major', None)
        )

        # 비밀번호를 암호화
        user.set_password(self.validated_data['password'])
        user.save()

        return user
    

# 로그인 시리얼라이저
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)

        user = CustomUser.get_user_or_none_by_username(username=username)

        if user is None:
            raise serializers.ValidationError("user account not exist")
        else:
            if not user.check_password(raw_password=password):
                raise serializers.ValidationError("wrong password")
            
        token = RefreshToken.for_user(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        data = {
            "user": user,
            "refresh_token": refresh_token,
            "access_token": access_token,
        }

        return data
    
class VerifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verif
        fields = "__all__"