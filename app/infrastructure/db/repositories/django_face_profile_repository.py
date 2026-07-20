from app.infrastructure.db.models.face_profile_model import (
    FaceProfile,
)


class DjangoFaceProfileRepository:

    def exists(self, user, verified_only=False):
        qs = FaceProfile.objects.filter(user=user)
        if verified_only:
            qs = qs.filter(is_verified=True)
        return qs.exists()
    
    @staticmethod
    def create_face_profile(
        user,
        label_name,
        embeddings,
        is_verified=False,
        image_url=None,
    ):
        return FaceProfile.objects.create(
            user=user,
            label_name=label_name,
            embeddings=embeddings,
            is_verified=is_verified,
            image_url=image_url,
        )

    @staticmethod
    def get_by_user(
        user,
    ):
        return (
            FaceProfile.objects.filter(
                user=user,
            ).first()
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
    def get_home_profiles(
        home,
    ):
        """
        Returns the face profiles of all users
        who belong to the given home.
        Used by the AI engine for recognition.
        """

        return (
            FaceProfile.objects.filter(
                user__home_memberships__home=home,
            )
            .select_related(
                "user",
            )
            .distinct()
        )

    @staticmethod
    def create_or_update_for_user(user, label_name, embeddings, is_verified=True):
        profile = DjangoFaceProfileRepository.get_by_user(user)
        if profile:
            profile.label_name = label_name
            profile.embeddings = embeddings
            profile.is_verified = is_verified
            profile.save(update_fields=["label_name", "embeddings", "is_verified", "updated_at"])
            return profile

        return DjangoFaceProfileRepository.create_face_profile(
            user=user,
            label_name=label_name,
            embeddings=embeddings,
            is_verified=is_verified,
        )

    @staticmethod
    def delete_profile(
        face_profile,
    ):
        face_profile.delete()