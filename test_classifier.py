from app.query.query_classifier import QueryClassifier



def main():

    classifier = QueryClassifier()


    questions = [

        "Who appeared first?",

        "When did the person appear?",

        "What happened before the person disappeared?",

        "What happened after the person entered?",

        "How many people appeared?",

        "Give timeline of events",

        "Show sequence of events",

        "Which object appeared last?",

        "Where is the person?"

    ]


    print("=" * 60)
    print(" CHRONOAGENT QUERY CLASSIFIER TEST ")
    print("=" * 60)



    for q in questions:


        result = classifier.classify(q)


        print("\nQUESTION:")
        print(q)


        print("CLASSIFIED INTENT:")

        print(result)


        print("-" * 60)




if __name__ == "__main__":

    main()