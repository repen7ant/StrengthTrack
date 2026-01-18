from core.models import BestSet, BestSetHistory, Exercise


class ProgressService:
    """Handles 1RM progress data for charts."""

    @staticmethod
    def get_progress_charts_data(user):
        """Get charts data for all exercises with history."""
        exercises = Exercise.objects.filter(best_set_history__user=user).distinct()

        charts_data = []
        for exercise in exercises:
            history = BestSetHistory.objects.filter(
                user=user, exercise=exercise
            ).order_by("created_at")

            data_points = [
                {
                    "date": h.created_at.strftime("%Y-%m-%d"),
                    "value": float(h.estimated_1rm),
                }
                for h in history
            ]

            best_set = BestSet.objects.filter(user=user, exercise=exercise).first()

            if best_set:
                data_points.append(
                    {
                        "date": best_set.updated_at.strftime("%Y-%m-%d"),
                        "value": float(best_set.estimated_1rm),
                    }
                )

            data_points.sort(key=lambda x: x["date"])

            charts_data.append(
                {
                    "exercise": exercise.name,
                    "dates": [dp["date"] for dp in data_points],
                    "values": [dp["value"] for dp in data_points],
                }
            )

        return charts_data
