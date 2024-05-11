from typing import List
import json
import numpy as np
from cards import TechGuideCards
from parameters import GUIDES_FILE, GUIDES_EMBEDDINGS_FILE


class TechGuideColumnLayer:

    def __init__(
        self,
        identifier,
        cards: TechGuideCards = None,
        priorities: List[int] = None,
        embedding: List[float] = None,
    ):
        self.identifier = identifier
        self.cards = cards
        self.priorities = priorities
        self.embedding = embedding


class TechGuidePath:

    def __init__(
        self,
        path_id,
        name: str = "",
        tags: List[str] = None,
        expertises: List[TechGuideColumnLayer] = None,
        collaborations: List[TechGuideColumnLayer] = None,
    ):
        self.path_id = path_id
        self.name = name
        self.tags = tags
        self.expertises = expertises
        self.collaborations = collaborations
        self.expertises_embeddings = np.array(
            [expertise.embedding for expertise in expertises]
        )
        self.collaborations_embeddings = np.array(
            [collaboration.embedding for collaboration in collaborations]
        )


class TechGuidePaths:

    def __init__(self, paths: List[TechGuidePath]):
        self.paths = paths
        self.expertises = []
        self.collaborations = []
        for path in paths:
            self.expertises.extend(path.expertises)
            self.collaborations.extend(path.collaborations)
        self.expertises_embeddings = np.concatenate(
            [path.expertises_embeddings for path in paths]
        )
        self.collaborations_embeddings = np.concatenate(
            [path.collaborations_embeddings for path in paths]
        )

    @staticmethod
    def construct(
        file: str = GUIDES_FILE, embeddings_file: str = GUIDES_EMBEDDINGS_FILE
    ):

        with open(file, "r") as f:
            path_data = json.load(f)

        with open(embeddings_file, "r") as f:
            embeddings = json.load(f)

        paths = []
        for path_id, item in path_data.items():
            expertises = []
            _data = item.get("expertise", [])
            _embeddings = embeddings.get(f"{path_id}", {}).get("expertise", [])
            for i, expertise_item in enumerate(_data):
                layer = TechGuideColumnLayer(
                    identifier=expertise_item.get("name", ""),
                    cards=expertise_item.get("cards", []),
                    embedding=_embeddings[i],
                )
                expertises.append(layer)

            collaborations = []
            _data = item.get("collaboration", [])
            _embeddings = embeddings.get(f"{path_id}", {}).get("collaboration", [])
            for i, collaboration_item in enumerate(_data):
                layer = TechGuideColumnLayer(
                    identifier=collaboration_item.get("name", ""),
                    cards=collaboration_item.get("cards", []),
                    embedding=_embeddings[i],
                )
                collaborations.append(layer)

            path = TechGuidePath(
                path_id=path_id,
                name=item.get("name", ""),
                tags=item.get("tags", []),
                expertises=expertises,
                collaborations=collaborations,
            )
            paths.append(path)

        return TechGuidePaths(paths)
