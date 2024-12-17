from rest_framework import serializers
from users.models import CustomUser


class RegularUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'phone', 'bio', 'dob', 'profile_picture','is_active']



class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'bio', 'dob', 'profile_picture']
    
    def update(self, instance, validated_data):
        """
        Update and return an existing user instance with validated data.
        """
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.dob = validated_data.get('dob', instance.dob)
        profile_picture = validated_data.get('profile_picture', None)
        if profile_picture:
            instance.profile_picture = profile_picture
        
        instance.save()
        return instance
    
class ToggleActiveStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_active']