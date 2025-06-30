import openai
from config import OPENAI_API_KEY

class Analyzer:
    """
    Analyzes news articles using an LLM.
    """
    def __init__(self):
        openai.api_key = OPENAI_API_KEY

    def analyze(self, articles):
        print("Analyzing articles...")
        analyzed_articles = []
        for article in articles:
            # In a real implementation, you would make a call to an LLM here.
            # response = openai.Completion.create(...)
            
            # Placeholder: Add dummy analysis data
            article['impact'] = "Medium"
            article['affected_sectors'] = ["Technology", "Finance"]
            analyzed_articles.append(article)
            print(f" - Analyzed: {article.get('title') or article.get('text')}")

        print("Done analyzing.")
        return analyzed_articles 
