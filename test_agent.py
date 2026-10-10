from app.agent.chrono_agent import ChronoAgent



# ==========================================
# VIDEO TO QUERY
# ==========================================

VIDEO_ID = "VID_f6241814"



# ==========================================
# INITIALIZE AGENT
# ==========================================

agent = ChronoAgent(
    VIDEO_ID
)



# ==========================================
# TEST QUERIES
# ==========================================

questions = [

    "Who appeared first in the scene?",


    "Which person appeared first?",


    "Show the complete timeline of events",


    "How many persons appeared?",


    "Which object appeared first?",


    "What happened before suitcase appeared?",


    "When did the suitcase appear?",


    "Describe the first event in the video"

]



# ==========================================
# RUN TESTS
# ==========================================

for q in questions:


    print("\n")
    print("=" * 70)

    print("QUESTION:")
    print(q)


    result = agent.answer(q)


    print("\nANSWER:")

    print(result)



print("\n")
print("=" * 70)
print("ChronoAgent testing completed.")