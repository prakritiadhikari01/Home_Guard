from app.infrastructure.db.models.face_profile_model import FaceProfile


class DjangoFaceProfileRepository:

    @staticmethod
    def create_face_profile(**kwargs):
        return FaceProfile.objects.create(**kwargs)

    @staticmethod
    def get_home_profiles(home):
        return FaceProfile.objects.filter(
            home_member__home=home
        )

    @staticmethod
    def get_user_profiles(user):
        return FaceProfile.objects.filter(home_member__user=user)