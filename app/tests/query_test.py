from app.pipeline.chrono_pipeline import ChronoPipeline



# ==========================================
# INITIALIZE CHRONOAGENT
# ==========================================

pipeline = ChronoPipeline()



# ==========================================
# PROCESSED VIDEO
# ==========================================

video_id = "VID_dad243f7"



print("=" * 60)
print(" CHRONOAGENT QUERY SYSTEM ")
print("=" * 60)



print(
    "Video:",
    video_id
)



# ==========================================
# QUESTIONS
# ==========================================

questions = [

    "Who entered first?",

    "Which person appeared first in the scene?",

    "How many persons appeared?",

    "When did the person appear?",

    "Describe the events in this video",

    "Show the timeline of events"

]



# ==========================================
# EXECUTE QUERY
# ==========================================

for question in questions:


    print("\n")

    print("-" * 60)


    print(
        "QUESTION:"
    )


    print(
        question
    )



    try:


        answer = pipeline.ask(
            question
        )


        print("\nANSWER:")


        print(
            answer
        )



    except Exception as e:


        print("\nQUERY FAILED:")


        print(
            type(e).__name__,
            ":",
            e
        )




print("\n")

print("=" * 60)

print(" QUERY COMPLETE ")

print("=" * 60)