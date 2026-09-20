from app.agent.chrono_agent import ChronoAgent



VIDEO_ID = "VID_adaf6b39"



agent = ChronoAgent(
    VIDEO_ID
)



questions = [

    "Who appeared first in the scene?",

    "Show the complete timeline of events",

    "How many persons appeared?"

]



for q in questions:


    print("\n")
    print("="*60)

    result = agent.answer(q)


    print(result)
