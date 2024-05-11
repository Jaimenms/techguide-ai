import numpy as np
import google.generativeai as genai
from cards import TechGuideCards
from decouple import config


class TechGuideAI:
    """
    TechGuide AI Class
    """

    def __init__(
        self, embedding_model="models/embedding-001", generative_model="gemini-1.0-pro"
    ):
        """
        Constructor
        :param embedding_model:
        :param generative_model:
        """
        API_KEY = config("API_KEY")

        genai.configure(api_key=API_KEY)
        self.embedding_model = embedding_model
        self.model = genai.GenerativeModel(generative_model)

    def embed_content(self, content):
        """
        Embed content
        :param content:
        :return:
        """
        return genai.embed_content(
            model=self.embedding_model, content=content, task_type="classification"
        )["embedding"]

    def search_similar_cards(self, cards, content, quantity=3):
        """
        Search similar cards
        :param cards:
        :param content:
        :param quantity:
        :return:
        """
        content_embedding = self.embed_content(content)
        product = np.dot(cards.embeddings, content_embedding)
        indexes = np.argsort(product)[::-1]
        near_indexes = indexes[:quantity]

        return TechGuideCards([cards.cards[i] for i in near_indexes])

    def search_similar_expertises(self, paths, content, quantity=3):
        """

        :param paths:
        :param content:
        :param quantity:
        :return:
        """
        content_embedding = self.embed_content(content)
        product = np.dot(paths.expertises_embeddings, content_embedding)
        indexes = np.argsort(product)[::-1]
        near_indexes = indexes[:quantity]
        expertises = [paths.expertises[i] for i in near_indexes]
        return expertises

    def plan_study_per_card(self, job_description, card):
        """

        :param job_description:
        :param card:
        :return:
        """

        contents = "Considerando a oportunidade de trabalho " + job_description + ", faça uma descrição sucinta da área de conhecimento descrita a seguir e depois um passo-a-passo para um candidato. Inclua nesse plano as referências e hyperlinks citados:"

        contents += card.generate_content_prompt()

        response = self.model.generate_content(contents=contents)

        return response.text

    def plan_study(self, job_description, cards):
        """

        :param job_description:
        :param cards:
        :return:
        """

        contents = "Considere a oportunidade de trabalho \"" + job_description + "\", faça uma descrição sucinta da área de conhecimento descrita a seguir e depois um passo-a-passo para um candidato.\n\n"
        contents += cards.generate_content_prompt()

        contents += "\n\nDescreva todos os objetivos que deverão ser atingidos antes de se candidatar."
        contents += "\n\nInclua nesse plano as referências dos cursos da Alura e informe os hiperlinks dos cursos nesse plano"

        response = self.model.generate_content(contents=contents)

        return response.text

    def rewrite_job_description(self, job_description):
        """

        :param job_description:
        :return:
        """

        contents = "Faça uma breve descrição da seguinte vaga:"

        contents += '\n\n"' + job_description + '"\n\n'

        response = self.model.generate_content(contents=contents)

        return response.text

    def rewrite_objectives(self, cards):
        """

        :param cards:
        :return:
        """

        contents = "A análise dessa vaga indica que o candidato deve ter conhecimento nas seguintes áreas:"
        for card in cards.cards:
            contents += "\n- {card.name}"

        contents = """\n\nEspera-se que o candidato cumpra os seguintes objetivos:"""
        for card in cards.cards:
            for key_objective in card.key_objectives:
                contents += "\n- " + key_objective

        contents += """\n\nRescreva essas áreas e objetivos de modo ao candidato poder identificar o que ele precisa alcançar."""

        response = self.model.generate_content(contents=contents)

        return response.text

    def rewrite_courses(self, cards):

        contents = """A Alura possui um conjunto de ofertas de treinamento podem ajudar os candidatos a atigirem
        esses objetivos. A seguir, uma lista de cursos que podem ser úteis para o candidato:"""
        for card in cards.cards:
            for content in card.alura_contents:
                if content.type == "COURSE":
                    contents += "\n- " + content.title +" - " + content.link

        contents += """\n\nPromova esses treinamentos por meio de um plano de estudos e indique os hiperlinks."""

        response = self.model.generate_content(contents=contents)

        return response.text
