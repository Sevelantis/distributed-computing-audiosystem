import random
import uuid

class BrokerUtils:
    
    @classmethod
    def generate_id(cls) -> str:
        return uuid.uuid4().__str__()[1::5]
    
