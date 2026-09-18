from abc import ABC, abstractmethod
import uuid
import datetime

class BaseModel(ABC):
    """Classe abstraite de base pour tous les modèles."""
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now().isoformat()
        self.is_active = True
    
    @abstractmethod
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """Crée un objet à partir d'un dictionnaire."""
        pass
    
    def validate(self):
        """Valide les données du modèle."""
        pass
    
    def save(self, data_manager):
        """Sauvegarde le modèle dans le gestionnaire de données."""
        pass
    
    def delete(self, data_manager):
        """Supprime le modèle du gestionnaire de données."""
        pass 