from pathlib import Path
import json


from app.retrieval.langchain_retriever import LangChainRetriever





class QueryPipeline:



    def __init__(
        self,
        graph_path,
        memory_path=None
    ):


        print(
            "[QUERY] Initializing RAG Query Pipeline"
        )



        self.graph_path = Path(graph_path)



        # ==================================
        # AUTO FIND MEMORY
        # ==================================


        if memory_path:

            self.memory_path = Path(
                memory_path
            )

        else:

            memories = list(
                Path("data/memory")
                .glob("*_event_memory.json")
            )


            if memories:

                self.memory_path = memories[-1]

            else:

                self.memory_path = None





        # ==================================
        # LANGCHAIN RETRIEVER
        # ==================================


        self.retriever = LangChainRetriever()



        # ==================================
        # LOAD GRAPH
        # ==================================


        if self.graph_path.exists():


            with open(
                self.graph_path
            ) as f:


                self.graph=json.load(f)


        else:


            self.graph={}







        # ==================================
        # LOAD MEMORY
        # ==================================


        self.memories=[]



        if self.memory_path and self.memory_path.exists():


            with open(
                self.memory_path
            ) as f:


                data=json.load(f)



                if isinstance(data,dict):


                    self.memories=data.get(
                        "memories",
                        []
                    )

                else:

                    self.memories=data





        print(
            "[QUERY] Knowledge loaded"
        )









    # =================================================
    # REMOVE DUPLICATES
    # =================================================


    def remove_duplicates(
        self,
        events
    ):


        unique={}


        for e in events:


            eid=e.get(
                "metadata",
                {}
            ).get(
                "event_id"
            )



            if eid not in unique:


                unique[eid]=e



        return list(
            unique.values()
        )









    # =================================================
    # ASK
    # =================================================


    def ask(
        self,
        question
    ):



        print(
            "\n[QUERY]",
            question
        )



        q=question.lower()





        # =====================================
        # RETRIEVE EVENTS
        # =====================================


        retrieved=self.retriever.retrieve(

            question,

            k=20

        )



        if not retrieved:


            return {

                "answer":
                "No relevant events found."

            }




        retrieved=self.remove_duplicates(
            retrieved
        )







        # =====================================
        # FIRST EVENT
        # =====================================


        if (
            "first" in q
            or
            "entered" in q
            or
            "appeared first" in q
        ):


            first=min(

                retrieved,

                key=lambda x:
                x["metadata"].get(
                    "timestamp",
                    99999
                )

            )


            return {


                "answer":
                first["content"],


                "event_id":
                first["metadata"].get(
                    "event_id"
                ),


                "timestamp":
                first["metadata"].get(
                    "timestamp"
                ),


                "evidence":
                first

            }









        # =====================================
        # COUNT PERSONS
        # =====================================


        if (
            "how many" in q
            and
            "person" in q
        ):


            persons=set()



            for m in self.memories:


                obj=m.get(
                    "class_name"
                )


                if obj=="person":


                    pid=(

                        m.get("track_id")
                        or
                        m.get("object_id")
                        or
                        m.get("id")

                    )


                    if pid:

                        persons.add(pid)



            return {


                "answer":

                f"{len(persons)} persons appeared in the video.",


                "persons":

                list(persons)

            }









        # =====================================
        # WHEN APPEARED
        # =====================================


        if (
            "when" in q
            and
            "appear" in q
        ):



            event=min(

                retrieved,

                key=lambda x:
                x["metadata"].get(
                    "timestamp",
                    99999
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









        # =====================================
        # DESCRIBE VIDEO
        # =====================================


        if "describe" in q:



            events=[]



            for e in retrieved:


                events.append({

                    "event":
                    e["content"],


                    "timestamp":
                    e["metadata"].get(
                        "timestamp"
                    )

                })




            return {


                "events":
                events,


                "total":
                len(events)

            }









        # =====================================
        # TIMELINE
        # =====================================


        if "timeline" in q:



            timeline=[]



            ordered=sorted(

                retrieved,

                key=lambda x:
                x["metadata"].get(
                    "timestamp",
                    99999
                )

            )



            for e in ordered:


                timeline.append({

                    "event_id":
                    e["metadata"].get(
                        "event_id"
                    ),


                    "event":
                    e["content"],


                    "time":
                    e["metadata"].get(
                        "timestamp"
                    )

                })



            return {


                "timeline":
                timeline

            }








        # =====================================
        # DEFAULT RAG ANSWER
        # =====================================


        return {


            "answer":

            [
                r["content"]
                for r in retrieved
            ],


            "evidence":

            retrieved

        }