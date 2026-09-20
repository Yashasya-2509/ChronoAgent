from pathlib import Path

from app.query.query_engine import QueryEngine



MEMORY_FOLDER = Path(
    "data/memory"
)



def get_latest_video_id():

    files = list(
        MEMORY_FOLDER.glob(
            "*_event_memory.json"
        )
    )


    if not files:
        raise Exception(
            "No processed videos found"
        )


    latest = max(
        files,
        key=lambda x:x.stat().st_mtime
    )


    return latest.stem.replace(
        "_event_memory",
        ""
    )



def main():

    print("="*60)
    print(
        " CHRONOAGENT QUERY SYSTEM "
    )
    print("="*60)



    video_id = get_latest_video_id()


    print(
        "\nUsing Video:",
        video_id
    )


    engine = QueryEngine(
        video_id
    )


    while True:


        query=input(
            "\nAsk CCTV Question: "
        )


        if query=="exit":
            break



        result = engine.answer(
            query
        )


        print("\nANSWER")
        print("-"*40)


        print(
            result
        )



if __name__=="__main__":
    main()