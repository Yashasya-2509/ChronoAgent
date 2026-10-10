from app.retrieval.langchain_retriever import LangChainRetriever


retriever = LangChainRetriever()


query = "Who entered first?"


results = retriever.retrieve(
    query
)


print("="*50)

print("QUERY:")
print(query)


print("\nRESULTS:")


for r in results:

    print("\n")

    print(r)