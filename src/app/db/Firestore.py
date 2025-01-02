import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from google.cloud import secretmanager


def get_firebase_credentials(env: str, project_id: str):
    if env == 'dev':
        with open("./resources/secrets/firebase-credentials.json", 'r') as creds:
            return creds.read()
    else:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/firebase-credentials/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode('UTF-8')


class Firestore:

    def __init__(self, env: str, tenant_id: str):
        # Load credentials from your services account key JSON file
        # You can download this file from Firebase Console -> Project Settings -> Service Accounts
        cred_json = get_firebase_credentials(env, tenant_id)
        cred_dict = json.loads(cred_json)
        self.cred = credentials.Certificate(cred_dict)
        self.client = None
        self.initialize_firestore()

    def initialize_firestore(self):
        """
        Initialize connection to Firestore database
        """
        # Initialize the app
        firebase_admin.initialize_app(self.cred)

        # Create Firestore client
        self.client = firestore.client()

    def add_document(self, collection_name, data):
        """
        Add a document to a collection

        Args:
            collection_name: Name of the collection
            data: Dictionary containing document data
        """
        doc_ref = self.client.collection(collection_name).document()
        doc_ref.set(data)
        return doc_ref.id

    def get_document(self, collection_name, document_id):
        """
        Retrieve a document from a collection

        Args:
            collection_name: Name of the collection
            document_id: ID of the document to retrieve
        """
        doc_ref = self.client.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def query_documents(self, collection_name, field, operator, value):
        """
        Query documents based on conditions

        Args:
            collection_name: Name of the collection
            field: Field to query on
            operator: Comparison operator ('==', '>', '<', '>=', '<=')
            value: Value to compare against
        """
        docs = self.client.collection(collection_name).where(field, operator, value).stream()
        return [doc.to_dict() for doc in docs]
