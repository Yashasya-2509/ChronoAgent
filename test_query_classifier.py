from app.query.query_classifier import QueryClassifier


classifier = QueryClassifier()


questions = [

    "Who appeared first?",

    "What happened before skateboard appeared?",

    "What happened after person entered?",

    "How many persons appeared?",

    "Give complete timeline"

]


for question in questions:

    result = classifier.classify(
        question
    )

    print(
        question
    )

    print(
        result
    )

    print(
        "-"*40
    )