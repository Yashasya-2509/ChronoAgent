from app.retrieval.langchain_retriever import LangChainRetriever


print("="*60)
print(" CHRONOAGENT RAG TEST ")
print("="*60)


retriever = LangChainRetriever()


query = "Who entered first?"


print("\nQUERY:")
print(query)


results = retriever.retrieve(
    query,
    k=5
)


print("\nRETRIEVED EVENTS:")


for i, result in enumerate(results):

    print("\nRESULT", i+1)

    print(result)


print("\n")
print("="*60)
print(" RAG TEST COMPLETE ")
print("="*60)