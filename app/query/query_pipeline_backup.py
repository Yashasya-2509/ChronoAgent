from pathlib import Path
import json

from app.retrieval.langchain_retriever import LangChainRetriever



class QueryPipeline:


    def __init__(
        self,
        graph_path,
        memory_path
    ):


        print("[QUERY] Initializing RAG Query Pipeline")


        self.graph_path = Path(graph_path)

        self.memory_path = Path(memory_path)



        self.retriever = LangChainRetriever()



        # load graph

        if self.graph_path.exists():

            with open(self.graph_path) as f:

                self.graph = json.load(f)

        else:

            self.graph = {}



        # load memory

        if self.memory_path.exists():

            with open(self.memory_path) as f:

                data=json.load(f)


                if "memories" in data:

                    self.memories=data["memories"]

                else:

                    self.memories=data


        else:

            self.memories=[]



        print("[QUERY] Knowledge loaded")







    def ask(self, question):


        print(
            "\n[QUERY]",
            question
        )



        question_lower = question.lower()



        # ===================================
        # RAG RETRIEVAL
        # ===================================


        retrieved = self.retriever.retrieve(

            question,

            k=10

        )



        if not retrieved:


            return {

                "answer":
                "No relevant events found"

            }




        # ===================================
        # WHO ENTERED FIRST
        # ===================================


        if "first" in question_lower or "entered" in question_lower:


            first_event=min(

                retrieved,

                key=lambda x:
                x["metadata"].get(
                    "timestamp",
                    999999
                )

            )


            return {


                "answer":
                first_event["content"],


                "event_id":
                first_event["metadata"].get(
                    "event_id"
                ),


                "timestamp":
                first_event["metadata"].get(
                    "timestamp"
                ),


                "evidence":
                first_event

            }




        # ===================================
        # COUNT PERSONS
        # ===================================


        if "how many" in question_lower and "person" in question_lower:


            persons=set()



            for m in self.memories:


                if m.get("object")=="person":


                    persons.add(

                        m.get("object_id")

                    )



            return {


                "answer":
                f"{len(persons)} persons appeared in the video.",


                "persons":
                list(persons)

            }







        # ===================================
        # WHEN DID PERSON APPEAR
        # ===================================


        if "when" in question_lower and "appear" in question_lower:


            event=min(

                retrieved,

                key=lambda x:
                x["metadata"].get(
                    "timestamp",
                    999999
                )

            )


            return {


                "answer":
                event["content"],


                "timestamp":
                event["metadata"].get(
                    "timestamp"
                ),


                "evidence":
                event

            }






        # ===================================
        # EVENT DESCRIPTION
        # ===================================


        if "describe" in question_lower:


            events=[]


            for r in retrieved:


                events.append(

                    r["content"]

                )



            return {


                "events":
                events,


                "evidence":
                retrieved

            }







        # ===================================
        # TIMELINE
        # ===================================


        if "timeline" in question_lower:


            timeline=[]



            sorted_events=sorted(

                retrieved,

                key=lambda x:
                x["metadata"].get(
                    "timestamp",
                    999999
                )

            )



            for e in sorted_events:



                timeline.append({

                    "event":
                    e["content"],


                    "timestamp":
                    e["metadata"].get(
                        "timestamp"
                    )

                })



            return {


                "timeline":
                timeline

            }







        # ===================================
        # DEFAULT RAG ANSWER
        # ===================================


        return {


            "answer":

            [

                r["content"]

                for r in retrieved

            ],


            "evidence":

            retrieved

        }