from app.constants.constants import ListingSources


class ValidationsUtils:
    @staticmethod
    def validate_source(source: str) -> bool:
        """Validate if the given listing source is valid"""
        valid_sources = [
            ListingSources.AMAZON,
            ListingSources.FLIPKART,
        ]
        return source in valid_sources
