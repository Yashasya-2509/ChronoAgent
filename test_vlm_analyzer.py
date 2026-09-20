from app.vision_language.vlm_analyzer import VLMAnalyzer



def main():


    print("\n")
    print("="*60)
    print(" CHRONOAGENT - VLM ANALYSIS TEST ")
    print("="*60)



    analyzer = VLMAnalyzer()



    results = analyzer.analyze_keyframes(

        "data/manifests/VID_91bbf259_keyframes.json",

        "data/detections/VID_91bbf259_detections.json"

    )



    print(
        f"\nFrames analyzed: {len(results)}"
    )



    for r in results:


        print("\n----------------")


        print(
            "Frame:",
            r["frame_id"]
        )


        print(
            "Time:",
            r["timestamp"]
        )


        print(
            "Description:",
            r["description"]
        )


        print(
            "Objects detected:",
            len(r["objects"])
        )




if __name__=="__main__":

    main()