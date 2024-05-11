import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
TMP_FOLDER = os.path.join(os.path.dirname(__file__), "tmp")
CARDS_FILE = os.path.join(DATA_FOLDER, "cards.json")
CARDS_EMBEDDINGS_FILE = os.path.join(DATA_FOLDER, "cards_embedding.json")
GUIDES_FILE = os.path.join(DATA_FOLDER, "guides.json")
GUIDES_EMBEDDINGS_FILE = os.path.join(DATA_FOLDER, "guides_embedding.json")
TECHGUIDE_GITHUB = os.environ.get("TECHGUIDE_GITHUB", "alura/techguide")
BRANCH_NAME = os.environ.get("BRANCH_NAME", "main")
