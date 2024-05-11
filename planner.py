"""TechGuide AI Plan"""
from argparse import ArgumentParser
from ai import TechGuideAI
from paths import TechGuidePaths
from cards import TechGuideCards


def plan(job_description, depth=4, availability=8):
    """
    Plan a study based on a job description
    :param job_description:
    :param depth:
    :param availability:
    :return:
    """

    # Read TechGuide data
    cards = TechGuideCards.construct()
    paths = TechGuidePaths.construct()

    # Intantiate TechGuide AI
    tga = TechGuideAI()

    # Collects similar expertises from job_description based on embedding
    similar_expertises = tga.search_similar_expertises(
        content=job_description, paths=paths, quantity=depth
    )

    # Filters cards
    filtered_cards = cards.filter_cards_by_id_and_priority(similar_expertises)

    # Collects similar cards from job_description based on embedding
    similar_cards = tga.search_similar_cards(
        content=job_description, cards=filtered_cards, quantity=availability
    )

    # Use Gemini to redescribe job descrition
    response_job = tga.rewrite_job_description(job_description=job_description)
    print(response_job)

    # Use Gemini to present the candidate objectives
    response_objectives = tga.rewrite_objectives(cards=similar_cards)
    print(response_objectives)

    # Use Gemini to offer Alura trainings
    response_courses = tga.rewrite_courses(cards=similar_cards)
    print(response_courses)


if __name__ == "__main__":

    parser = ArgumentParser("TechGuide AI - Candidate Plan")
    parser.add_argument(
        "--job_description",
        type=str,
        help="Give a description of you experience",
        required=True,
    )
    parser.add_argument(
        "--depth",
        type=int,
        help="Number of expertise layers",
        default=4,
    )
    parser.add_argument(
        "--availability", type=int, help="Number of cards", default=8
    )
    args = parser.parse_args()

    plan(
        job_description=args.job_description,
        depth=args.depth,
        availability=args.availability,
    )
