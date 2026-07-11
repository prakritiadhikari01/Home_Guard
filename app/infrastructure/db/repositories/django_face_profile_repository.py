from app.infrastructure.db.models.face_profile_model import FaceProfile


class DjangoFaceProfileRepository:

    @staticmethod
    def create_face_profile(
        home_member,
        label_name,
        embeddings,
        is_verified=False,
        image_url=None,
    ):
        return FaceProfile.objects.create(
            home_member=home_member,
            label_name=label_name,
            embeddings=embeddings,
            is_verified=is_verified,
            image_url=image_url,
        )

    @staticmethod
    def update_embeddings(
        face_profile,
        embeddings,
    ):
        face_profile.embeddings = embeddings
        face_profile.save(
            update_fields=[
                "embeddings",
                "updated_at",
            ]
        )
        return face_profile

    @staticmethod
    def verify(
        face_profile,
    ):
        face_profile.is_verified = True
        face_profile.save(
            update_fields=[
                "is_verified",
                "updated_at",
            ]
        )
        return face_profile

    @staticmethod
    def get_by_home_member(
        home_member,
    ):
        return (
            FaceProfile.objects.filter(
                home_member=home_member
            ).first()
        )

    @staticmethod
    def get_home_profiles(
        home,
    ):
        return (
            FaceProfile.objects.filter(
                home_member__home=home
            )
            .select_related(
                "home_member",
                "home_member__user",
            )
        )

    @staticmethod
    def get_user_profiles(
        user,
    ):
        return (
            FaceProfile.objects.filter(
                home_member__user=user
            )
            .select_related(
                "home_member",
                "home_member__home",
            )
        )

    @staticmethod
    def delete_profile(
        face_profile,
    ):
        face_profile.delete()