import numpy as np


class RatingAnalyzer:
    def __init__(self):
        pass

    def analyze_ratings(self, ratings_data):
        """Analyze ratings from different sources"""
        try:
            analysis = {
                "average_rating": 0.0,
                "rating_distribution": {},
                "source_comparison": {},
                "recommendation": "No data",
            }

            if not ratings_data:
                return analysis

            # Extract numeric ratings
            numeric_ratings = []
            source_ratings = {}

            for source, data in ratings_data.items():
                if isinstance(data, dict):
                    rating = data.get("rating", 0)
                    if isinstance(rating, (int, float)) and rating > 0:
                        numeric_ratings.append(rating)
                        source_ratings[source] = rating

            if numeric_ratings:
                analysis["average_rating"] = np.mean(numeric_ratings)
                analysis["source_comparison"] = source_ratings

                # Simple recommendation based on average
                avg = analysis["average_rating"]
                if avg >= 7.5:
                    analysis["recommendation"] = "Highly Recommended"
                elif avg >= 6.0:
                    analysis["recommendation"] = "Recommended"
                elif avg >= 4.0:
                    analysis["recommendation"] = "Mixed Reviews"
                else:
                    analysis["recommendation"] = "Not Recommended"

            return analysis

        except Exception as e:
            return {"error": str(e), "average_rating": 0.0}