from rest_framework import serializers
from .models import CustomUser, SavedFile
from rest_framework import status
from django.contrib.auth import authenticate

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [ 'full_name', 'email', 'farm_location']    

class SavedFileSerailizer(serializers.ModelSerializer):
    class Meta:
        model = SavedFile
        fields = ['user', 'confidence', 'crop_name', 'top_class', 'file_data', 'timestamp']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [ 'full_name', "username", 'email', 'farm_location', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)   

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)  # ✅ Correct usage
        if not user:
            raise serializers.ValidationError(
                {"error": "Invalid username or password"}, 
                code=status.HTTP_401_UNAUTHORIZED
            )

        data["user"] = user
        return data
    
class SavedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedFile
        # We include 'user' in fields so we can see it in responses,
        # but read_only=True ensures we don't need to send it in POST requests.
        fields = ['id', 'user', 'confidence', 'crop_name', 'top_class', 'file_data', 'timestamp']
        read_only_fields = [ 'timestamp']


class FirebaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'farm_location']