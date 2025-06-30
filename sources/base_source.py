from abc import ABC, abstractmethod

class BaseSource(ABC):
    """
    Abstract base class for all news sources.
    """
    @abstractmethod
    def fetch_news(self):
        """
        Fetch new articles from the source.
        This method should be implemented by each specific source.
        """
        pass 
