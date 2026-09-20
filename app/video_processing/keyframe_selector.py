class KeyframeSelector:

    def __init__(self, max_keyframes_per_scene=3):
        self.max_keyframes_per_scene = max_keyframes_per_scene

    def select_keyframes(self, frames, scenes):

        selected = []

        for scene in scenes:

            # Get frames belonging to this scene
            scene_frames = [
                frame
                for frame in frames
                if (
                    scene["start_time"]
                    <= frame["timestamp"]
                    <= scene["end_time"]
                )
            ]

            if not scene_frames:
                continue

            count = min(
                self.max_keyframes_per_scene,
                len(scene_frames)
            )

            # If only one frame is available
            if count == 1:

                indices = [
                    len(scene_frames) // 2
                ]

            else:

                # Select evenly distributed frames
                step = (
                    len(scene_frames) - 1
                ) / (count - 1)

                indices = [
                    round(i * step)
                    for i in range(count)
                ]

            for index in indices:

                frame = scene_frames[index]

                frame["is_keyframe"] = True
                frame["scene_id"] = scene["scene_id"]

                selected.append(frame)

        return selected