import json
from typing import List
import numpy as np
from parameters import CARDS_FILE, CARDS_EMBEDDINGS_FILE


class TechGuideContent:

    def __init__(self, _type: str, title: str, link: str):
        self.type = _type
        self.title = title
        self.link = link

    def __str__(self):
        return f"[{self.type}] {self.title} - {self.link}"


class TechGuideCard:

    def __init__(
        self,
        card_id: str,
        name: str = "",
        short_description: str = "",
        key_objectives: List[str] = None,
        aditional_objectives: List[str] = None,
        contents: List[TechGuideContent] = None,
        alura_contents: List[TechGuideContent] = None,
        embedding: List[float] = None,
    ):
        self.card_id = card_id
        self.name = name
        self.short_description = short_description
        self.key_objectives = key_objectives
        self.aditional_objectives = aditional_objectives
        self.contents = contents if contents else []
        self.alura_contents = alura_contents if alura_contents else []
        self.embedding = embedding
        self.key_objectives_str = "; ".join(key_objectives) if key_objectives else ""

    def __str__(self):
        return f"CARD: {self.name} - {self.key_objectives_str}"

    def __repr__(self):
        return f"CARD: {self.name} - {self.key_objectives_str}"

    def generate_content_prompt(self):

        prompt_array = [f"Trata-se da área de conhecimento {self.name}."]
        if self.short_description:
            prompt_array.append(f"Pode ser descrita como {self.short_description}")
        if self.key_objectives:
            prompt_array.append(f"Para dominar essa área você deve:")
            for key_objective in self.key_objectives:
                prompt_array.append(f"- {key_objective}")
        if self.aditional_objectives:
            prompt_array.append(f"Além disso, é importante:")
            for aditional_objective in self.aditional_objectives:
                prompt_array.append(f"- {aditional_objective}")

        for i, content in enumerate(self.alura_contents):
            if i == 0:
                prompt_array.append(
                    "Para esses temas a Alura oferece os seguintes cursos:"
                )
            if content.type == "COURSE":
                prompt_array.append(f"- {content.title} - {content.link}")
        for i, content in enumerate(self.alura_contents + self.contents):
            if i == 0:
                prompt_array.append("Recomenda-se também ver as seguintes referências:")
            if content.type != "COURSE":
                prompt_array.append(f"- {content.title} - {content.link}")

        return "\n".join(prompt_array)


class TechGuideCards:

    def __init__(self, cards: List[TechGuideCard]):
        self.cards = cards
        self.embeddings = np.array([card.embedding for card in cards])

    def __str__(self):
        return "\n\n".join([str(card) for card in self.cards])

    def generate_content_prompt(self):

        names_str = "; ".join([card.name for card in self.cards])
        prompt_array = [f"Trata-se das áreas de conhecimento: {names_str}."]
        short_description_str = "; ".join(
            [card.short_description for card in self.cards if card.short_description]
        )
        prompt_array.append(f"Podem ser descritas como: {short_description_str}")

        for i, card in enumerate(self.cards):
            if i == 0:
                prompt_array.append(
                    "Os principais objetivos que deve atingir para estar capacidade para essa vaga são:"
                )
            for key_objective in card.key_objectives:
                prompt_array.append(f"- {key_objective}")

        for i, card in enumerate(self.cards):
            if i == 0:
                prompt_array.append(
                    "Para esses temas a Alura oferece os seguintes cursos:"
                )
            for content in card.alura_contents:
                if content.type == "COURSE":
                    prompt_array.append(f"- {content.title} - {content.link}")

        return "\n".join(prompt_array)

    @staticmethod
    def construct(file: str = CARDS_FILE, embeddings_file: str = CARDS_EMBEDDINGS_FILE):
        with open(file, "r") as f:
            card_data = json.load(f)

        with open(embeddings_file, "r") as f:
            embeddings = json.load(f)

        cards = []
        for card_id, item in card_data.items():

            contents = (
                [
                    TechGuideContent(
                        _type=content.get("type", ""),
                        title=content.get("title", ""),
                        link=content.get("link", ""),
                    )
                    for content in item.get("contents", [])
                ]
                if item.get("contents", [])
                else []
            )

            alura_contents = (
                [
                    TechGuideContent(
                        _type=content.get("type", ""),
                        title=content.get("title", ""),
                        link=content.get("link", ""),
                    )
                    for content in item.get("alura-contents")
                ]
                if item.get("alura-contents", [])
                else []
            )

            card = TechGuideCard(
                card_id=card_id,
                name=item.get("name", ""),
                short_description=item.get("short-description", ""),
                key_objectives=item.get("key-objectives", ""),
                aditional_objectives=item.get("aditional-objectives", ""),
                contents=contents,
                alura_contents=alura_contents,
                embedding=embeddings.get(card_id, []),
            )
            cards.append(card)
        return TechGuideCards(cards)

    def filter_cards_by_id_and_priority(self, similar_expertises, max_cards=25):
        similar_expertises_cards = []
        for similar_expertise in similar_expertises:
            for card in similar_expertise.cards:
                similar_expertises_cards.append(card)

        similar_expertises_cards.sort(
            key=lambda x: int(x["priority"] if "priority" in x else 0), reverse=True
        )
        filtered_cards_ids = set(
            [list(card.keys())[0] for card in similar_expertises_cards[:max_cards]]
        )
        return TechGuideCards(
            [card for card in self.cards if card.card_id in filtered_cards_ids]
        )
