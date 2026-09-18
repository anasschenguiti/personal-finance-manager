from pymongo import MongoClient
from datetime import datetime
import uuid
from bson import ObjectId
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self, connection_string='mongodb://localhost:27017/', db_name='finance_app'):
        try:
            self.client = MongoClient(connection_string)
            # Vérifier la connexion
            self.client.admin.command('ping')
            logger.info("Connexion à MongoDB établie avec succès")
            
            # Lister toutes les bases de données disponibles
            db_list = self.client.list_database_names()
            logger.info(f"Bases de données disponibles: {db_list}")
            
            # Utiliser la base de données spécifiée ou la première disponible
            if db_name in db_list:
                self.db = self.client[db_name]
                logger.info(f"Base de données '{db_name}' sélectionnée")
            else:
                # Si la base de données n'existe pas, utiliser la première disponible
                self.db = self.client[db_list[0]]
                logger.info(f"Base de données '{db_list[0]}' sélectionnée (base par défaut)")
            
            # Lister les collections existantes
            existing_collections = self.db.list_collection_names()
            logger.info(f"Collections existantes: {existing_collections}")
            
            # Créer un dictionnaire dynamique des collections basé sur les collections existantes
            self.collections = {}
            for collection_name in existing_collections:
                self.collections[collection_name] = self.db[collection_name]
                count = self.db[collection_name].count_documents({})
                logger.info(f"Collection '{collection_name}': {count} documents")
            
            # Afficher un exemple de document de chaque collection
            for collection_name, collection in self.collections.items():
                sample = collection.find_one()
                if sample:
                    logger.info(f"Exemple de document dans '{collection_name}': {sample}")
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à MongoDB: {str(e)}")
            raise
    
    def _convert_id(self, doc):
        """Convertit les ObjectId en chaînes de caractères"""
        if doc and '_id' in doc:
            doc['_id'] = str(doc['_id'])
        return doc
    
    def get_all(self, collection_name):
        """Récupère tous les documents d'une collection"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return []
            docs = list(self.collections[collection_name].find())
            logger.info(f"Récupération de {len(docs)} documents de la collection '{collection_name}'")
            return [self._convert_id(doc) for doc in docs]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents de '{collection_name}': {str(e)}")
            return []
    
    def get_by_id(self, collection_name, id):
        """Récupère un document par son ID"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return None
            
            # Essayer d'abord avec le champ 'id' (UUID)
            doc = self.collections[collection_name].find_one({'id': str(id)})
            if doc:
                logger.info(f"Document trouvé dans '{collection_name}' avec le champ 'id' {id}")
                return self._convert_id(doc)
            
            # Si pas trouvé avec 'id', essayer avec le champ '_id'
            try:
                # Essayer d'abord comme string
                doc = self.collections[collection_name].find_one({'_id': str(id)})
                if doc:
                    logger.info(f"Document trouvé dans '{collection_name}' avec l'ID string {id}")
                    return self._convert_id(doc)
                
                # Essayer comme ObjectId si c'est un ID MongoDB valide
                if isinstance(id, str) and len(str(id)) == 24:
                    try:
                        object_id = ObjectId(id)
                        doc = self.collections[collection_name].find_one({'_id': object_id})
                        if doc:
                            logger.info(f"Document trouvé dans '{collection_name}' avec l'ObjectId {id}")
                            return self._convert_id(doc)
                    except:
                        pass
                
                # Essayer avec l'ID tel quel
                doc = self.collections[collection_name].find_one({'_id': id})
                if doc:
                    logger.info(f"Document trouvé dans '{collection_name}' avec l'ID {id}")
                    return self._convert_id(doc)
                    
            except Exception as e:
                logger.warning(f"Erreur lors de la recherche avec '_id': {str(e)}")
            
            logger.warning(f"Aucun document trouvé dans '{collection_name}' avec l'ID {id}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du document de '{collection_name}': {str(e)}")
            return None
    
    def get_by_user_id(self, collection_name, user_id):
        """Récupère tous les documents d'un utilisateur"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return []
            
            # Pour les utilisateurs, chercher par 'id'
            if collection_name == 'users':
                docs = list(self.collections[collection_name].find({'id': str(user_id)}))
                if docs:
                    logger.info(f"Récupération de {len(docs)} documents de '{collection_name}' avec l'ID {user_id}")
                    return [self._convert_id(doc) for doc in docs]
            else:
                # Pour les autres collections, chercher par 'user_id'
                # Essayer d'abord avec user_id en string
                docs = list(self.collections[collection_name].find({'user_id': str(user_id)}))
                if docs:
                    logger.info(f"Récupération de {len(docs)} documents de '{collection_name}' pour l'utilisateur {user_id}")
                    return [self._convert_id(doc) for doc in docs]
                
                # Si pas trouvé, essayer avec user_id comme ObjectId ou autre type
                try:
                    docs = list(self.collections[collection_name].find({'user_id': user_id}))
                    if docs:
                        logger.info(f"Récupération de {len(docs)} documents de '{collection_name}' pour l'utilisateur {user_id} (format original)")
                        return [self._convert_id(doc) for doc in docs]
                except:
                    pass
            
            logger.warning(f"Aucun document trouvé dans '{collection_name}' pour l'utilisateur {user_id}")
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents de '{collection_name}': {str(e)}")
            return []
    
    def create(self, collection_name, data):
        """Crée un nouveau document"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return None
            
            # Générer un nouvel ID si nécessaire
            if '_id' not in data:
                new_id = str(uuid.uuid4())
                data['_id'] = new_id
                # Pour les documents qui ont besoin d'un champ 'id' également
                if 'id' not in data:
                    data['id'] = new_id
            
            if 'created_at' not in data:
                data['created_at'] = datetime.now().isoformat()
                
            result = self.collections[collection_name].insert_one(data)
            logger.info(f"Document créé dans '{collection_name}' avec l'ID {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erreur lors de la création du document dans '{collection_name}': {str(e)}")
            return None
    
    def update(self, collection_name, id, data):
        """Met à jour un document"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return False
            
            # Essayer différentes stratégies de mise à jour
            result = None
            
            # Stratégie 1: Essayer avec le champ 'id'
            result = self.collections[collection_name].update_one(
                {'id': str(id)},
                {'$set': data}
            )
            if result.modified_count > 0:
                logger.info(f"Document mis à jour dans '{collection_name}' avec le champ 'id' {id}")
                return True
            
            # Stratégie 2: Essayer avec '_id' comme string
            result = self.collections[collection_name].update_one(
                {'_id': str(id)},
                {'$set': data}
            )
            if result.modified_count > 0:
                logger.info(f"Document mis à jour dans '{collection_name}' avec '_id' string {id}")
                return True
            
            # Stratégie 3: Essayer avec '_id' comme ObjectId si possible
            try:
                if isinstance(id, str) and len(str(id)) == 24:
                    result = self.collections[collection_name].update_one(
                        {'_id': ObjectId(id)},
                        {'$set': data}
                    )
                    if result.modified_count > 0:
                        logger.info(f"Document mis à jour dans '{collection_name}' avec ObjectId {id}")
                        return True
            except:
                pass
            
            logger.warning(f"Aucun document mis à jour dans '{collection_name}' avec l'ID {id}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du document dans '{collection_name}': {str(e)}")
            return False
    
    def delete(self, collection_name, id):
        """Supprime un document"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return False
            
            # Essayer différentes stratégies de suppression
            result = None
            
            # Stratégie 1: Essayer avec le champ 'id'
            result = self.collections[collection_name].delete_one({'id': str(id)})
            if result.deleted_count > 0:
                logger.info(f"Document supprimé de '{collection_name}' avec le champ 'id' {id}")
                return True
            
            # Stratégie 2: Essayer avec '_id' comme string
            result = self.collections[collection_name].delete_one({'_id': str(id)})
            if result.deleted_count > 0:
                logger.info(f"Document supprimé de '{collection_name}' avec '_id' string {id}")
                return True
            
            # Stratégie 3: Essayer avec '_id' comme ObjectId si possible
            try:
                if isinstance(id, str) and len(str(id)) == 24:
                    result = self.collections[collection_name].delete_one({'_id': ObjectId(id)})
                    if result.deleted_count > 0:
                        logger.info(f"Document supprimé de '{collection_name}' avec ObjectId {id}")
                        return True
            except:
                pass
            
            logger.warning(f"Aucun document supprimé de '{collection_name}' avec l'ID {id}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du document de '{collection_name}': {str(e)}")
            return False
    
    def find_one(self, collection_name, query):
        """Trouve un document selon un critère"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return None
            doc = self.collections[collection_name].find_one(query)
            if doc:
                logger.info(f"Document trouvé dans '{collection_name}' avec la requête {query}")
            else:
                logger.warning(f"Aucun document trouvé dans '{collection_name}' avec la requête {query}")
            return self._convert_id(doc)
        except Exception as e:
            logger.error(f"Erreur lors de la recherche dans '{collection_name}': {str(e)}")
            return None
    
    def find(self, collection_name, query):
        """Trouve des documents selon un critère"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return []
            docs = list(self.collections[collection_name].find(query))
            logger.info(f"Récupération de {len(docs)} documents de '{collection_name}' avec la requête {query}")
            return [self._convert_id(doc) for doc in docs]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche dans '{collection_name}': {str(e)}")
            return []
    
    def aggregate(self, collection_name, pipeline):
        """Exécute une agrégation MongoDB"""
        try:
            if collection_name not in self.collections:
                logger.warning(f"Collection '{collection_name}' n'existe pas")
                return []
            docs = list(self.collections[collection_name].aggregate(pipeline))
            logger.info(f"Récupération de {len(docs)} documents de '{collection_name}' via agrégation")
            return [self._convert_id(doc) for doc in docs]
        except Exception as e:
            logger.error(f"Erreur lors de l'agrégation dans '{collection_name}': {str(e)}")
            return [] 