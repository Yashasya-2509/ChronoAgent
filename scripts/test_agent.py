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
# TEST QUESTIONS
# ==========================================

questions = [

    # First appearance reasoning
    "Who appeared first in the scene?",

    "Which person appeared first?",


    # Timeline reasoning
    "Show the complete timeline of events",


    # Object counting
    "How many persons appeared?",


    # Temporal reasoning
    "What happened before suitcase appeared?",


    # Object based query
    "When did the suitcase appear?",


    # General semantic query
    "Describe the events in this video"

]


# ==========================================
# RUN QUERIES
# ==========================================

for q in questions:

    print("\n")
    print("=" * 70)
    print("QUESTION:")
    print(q)

    result = agent.answer(q)

    print("\nANSWER:")
    print(result)