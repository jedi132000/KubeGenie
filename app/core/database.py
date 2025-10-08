"""
Simple database module for development (no actual database)
"""

# Mock database objects for development
class MockBase:
    metadata = None

class MockEngine:
    def __init__(self):
        pass
    
    def connect(self):
        return self
    
    def execute(self, query):
        return []

# Export mock objects  
Base = MockBase()
engine = MockEngine()
metadata = {}

def get_db():
    """Mock database session"""
    return {"mock": "session"}