from core.models import BestSet


class ProfileService:
    """Handles profile data retrieval."""

    @staticmethod
    def get_user_best_sets(user):
        """Get user's best sets with exercise."""
        return BestSet.objects.filter(user=user).select_related("exercise")
