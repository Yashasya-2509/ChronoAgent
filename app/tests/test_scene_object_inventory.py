from app.memory.scene_object_inventory import SceneObjectInventory


def main():

    print()
    print("=" * 70)
    print("CHRONOAGENT — SCENE OBJECT INVENTORY TEST")
    print("=" * 70)

    track_path = (
        "data/tracks/"
        "VID_0a2a093d_tracks.json"
    )

    output_path = (
        "data/memory/"
        "VID_0a2a093d_object_inventory.json"
    )

    inventory_builder = SceneObjectInventory()

    inventory = inventory_builder.build_from_file(
        track_path,
        output_path
    )

    inventory_builder.print_inventory(
        inventory
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    assert inventory["video_id"] == "VID_0a2a093d"

    assert (
        inventory["total_objects"] == 24
    )

    assert (
        len(inventory["objects"]) == 24
    )

    assert "PERSON" in inventory["by_class"]

    assert "CAR" in inventory["by_class"]

    assert "TRUCK" in inventory["by_class"]

    person_001 = next(
        obj
        for obj in inventory["objects"]
        if obj["object_id"] == "PERSON_001"
    )

    assert (
        person_001["first_seen"] == 0.6
    )

    assert (
        person_001["last_seen"] == 70.8
    )

    assert (
        person_001["duration"] == 70.2
    )

    print()
    print("PASS: Video ID preserved.")
    print("PASS: 24 unique objects loaded.")
    print("PASS: Objects grouped by class.")
    print("PASS: PERSON inventory validated.")
    print("PASS: Lifecycle timestamps preserved.")
    print()
    print("✅ SCENE OBJECT INVENTORY TEST PASSED")
    print()


if __name__ == "__main__":
    main()