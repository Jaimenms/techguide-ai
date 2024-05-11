"""
Esse módulo permite baixar e processar os dados do repositório techguide do GitHub.
Como resultado teremos os cards e os paths em uma estrutura de dados a ser utilizada
posteriormente pelo TechGuideAI. Além disso, é feito o embedding dos cards e dos guides.
"""

import os
from urllib.request import urlopen
import yaml
from yaml.scanner import ScannerError
from google.api_core.exceptions import DeadlineExceeded
import json
import logging

from io import BytesIO
from zipfile import ZipFile
import google.generativeai as genai
from retry import retry

from parameters import API_KEY, DATA_FOLDER, TMP_FOLDER, TECHGUIDE_GITHUB, BRANCH_NAME

logging.basicConfig(level=logging.INFO)


class TechGuideCollector:
    """
    Classe para coletar dados do repositório techguide do GitHub.
    """

    def __init__(
        self,
        techguide_github=TECHGUIDE_GITHUB,
        branch=BRANCH_NAME,
        tmp_folder=TMP_FOLDER,
        data_folder=DATA_FOLDER,
    ):
        """

        :param techguide_github: String that represents the GitHub repository in the format owner/repo
        :param branch: Git branch to download
        :param tmp_folder: Temporary folder to download the repository
        :param data_folder: Data folder to store the processed data
        """

        # Isolaring owner and repo
        owner, repo = techguide_github.split("/")

        # Creating the temporary folder
        os.makedirs(tmp_folder, exist_ok=True)

        # Repository URL that permits the download of Zip file
        self.url = (
            f"https://github.com/{techguide_github}/archive/refs/heads/{branch}.zip"
        )
        self.tmp_folder = tmp_folder
        self.download_folder = os.path.join(tmp_folder, f"{repo}-{branch}")
        self.data_folder = data_folder

    def download_repo(self, force=False):
        """
        Download the repository from GitHub
        :param force: Force download even if the folder already exists
        :return:
        """
        if force or os.path.exists(self.download_folder):
            logging.warning(
                f"Folder {self.download_folder} already exists. Skipping download_repo."
            )
            return
        http_response = urlopen(self.url)
        with ZipFile(BytesIO(http_response.read())) as zipfile:
            zipfile.extractall(path=self.tmp_folder)

    def collecting_guides(self, force=False):
        """

        :param languages:
        :param force:
        :return:
        """

        path = os.path.join(self.download_folder, f"_data/guides")
        for language in os.listdir(path):
            if language != "pt_BR":
                continue
            data = {}
            destination = os.path.join(self.data_folder, "guides.json")
            if not force and os.path.exists(destination):
                logging.warning(
                    f"Guides file {destination} already exists. Skipping collecting."
                )
                continue

            for file in os.listdir(os.path.join(path, language)):
                try:
                    with open(os.path.join(path, language, file), "r") as f:
                        guide = yaml.load(f, Loader=yaml.FullLoader)
                except ScannerError:
                    logging.error(f"Error processing card {file}")
                    continue

                logging.info(f"Processing guide {file}")

                guide_id = file.rsplit(".", 1)[0]
                data[guide_id] = guide

            with open(destination, "w") as f:
                json.dump(data, f)

    @retry(DeadlineExceeded, tries=3, delay=15)
    def embed_card(self, card: dict, model: str):
        name = card.get("name", "")
        key_objectives = card.get("key-objectives", [])
        if not key_objectives:
            return
        key_objectives_str = "\n".join(key_objectives)
        content = f"{name}\n{key_objectives_str}"
        output = genai.embed_content(
            model=model, content=content, task_type="classification"
        )
        return output["embedding"]

    @retry(DeadlineExceeded, tries=3, delay=15)
    def embed_guide(self, cards: dict, model: str):
        items = []
        for card_id, card in cards.items():
            name = card.get("name", "")
            items.append(name)
            items += card.get("key-objectives", [])
        content = "\n".join(items)
        output = genai.embed_content(
            model=model, content=content, task_type="classification"
        )
        return output["embedding"]

    def collecting_cards(self, languages=("pt_BR",), force=False):

        path = os.path.join(self.download_folder, f"_data/cards")
        for language in os.listdir(path):
            if language not in languages:
                continue

            data = {}
            destination = os.path.join(self.data_folder, "cards.json")
            if not force and os.path.exists(destination):
                logging.warning(
                    f"Card file {destination} already exists. Skipping collecting."
                )
                continue

            logging.info(f"Processing language {language}")
            for file in os.listdir(os.path.join(path, language)):
                try:
                    with open(os.path.join(path, language, file), "r") as f:
                        card = yaml.load(f, Loader=yaml.FullLoader)
                except ScannerError:
                    logging.error(f"Error processing card {file}")
                    continue

                logging.info(f"Processing card {file}")
                data[file.rsplit(".", 1)[0]] = card

            with open(destination, "w") as f:
                json.dump(data, f)
            logging.info(f"Processing language {language}: done.")

    def embedding_cards(self, model="models/embedding-001", force=False):

        for language in os.listdir(self.data_folder):
            destination = os.path.join(
                self.data_folder, "cards_embedding.json"
            )
            if not force and os.path.exists(destination):
                logging.warning(
                    f"Embedding file {destination} already exists. Skipping embedding."
                )
                continue

            with open(os.path.join(self.data_folder, language, "cards.json"), "r") as f:
                cards = json.load(f)

            data = {}
            for key, card in cards.items():
                logging.info(f"Processing card {key}")
                data[key] = self.embed_card(card, model)

            with open(destination, "w") as f:
                json.dump(data, f)

            logging.info(f"Processing language {language}: done.")

    def embedding_guides(self, model="models/embedding-001", force=False):

        for language in os.listdir(self.data_folder):
            destination = os.path.join(
                self.data_folder, "guides_embedding.json"
            )
            if not force and os.path.exists(destination):
                logging.warning(
                    f"Embedding file {destination} already exists. Skipping embedding."
                )
                continue

            with open(os.path.join(self.data_folder, language, "cards.json"), "r") as f:
                cards = json.load(f)

            with open(
                os.path.join(self.data_folder, language, "guides.json"), "r"
            ) as f:
                guides = json.load(f)

            data = {}
            for guide_key, guide in guides.items():
                logging.info(f"Processing guide {guide_key}")
                data[guide_key] = {}

                for component in ("expertise", "collaboration"):
                    data[guide_key][component] = []

                    for i, guide_item in enumerate(guide[component]):
                        expertise_cards = {}
                        for guide_card in guide_item["cards"]:
                            card_id = list(guide_card.keys())[0]
                            if card_id in cards:
                                expertise_cards[card_id] = cards[card_id]
                        embedding = self.embed_guide(expertise_cards, model)
                        data[guide_key][component].append(embedding)

            with open(destination, "w") as f:
                json.dump(data, f)

            logging.info(f"Processing language {language}: done.")

def collector():
    genai.configure(api_key=API_KEY)
    c = TechGuideCollector()
    c.download_repo()
    c.collecting_guides()
    c.embedding_guides()
    c.collecting_cards()
    c.embedding_cards()

if __name__ == "__main__":
    collector()
