from math import sqrt


class TrajectoryAnalyzer:


    def calculate_center(self, bbox):

        x_center = (
            bbox["x1"] +
            bbox["x2"]
        ) / 2

        y_center = (
            bbox["y1"] +
            bbox["y2"]
        ) / 2

        return (
            x_center,
            y_center
        )


    def calculate_distance(
        self,
        point1,
        point2
    ):

        return sqrt(
            (point1[0]-point2[0])**2 +
            (point1[1]-point2[1])**2
        )


    def analyze_track(
        self,
        observations
    ):

        trajectory = []

        total_distance = 0


        previous_point = None


        for obs in observations:

            center = self.calculate_center(
                obs["bbox"]
            )

            trajectory.append({

                "frame_id":
                    obs["frame_id"],

                "timestamp":
                    obs["timestamp"],

                "position":
                    center

            })


            if previous_point:

                distance = (
                    self.calculate_distance(
                        previous_point,
                        center
                    )
                )

                total_distance += distance


            previous_point = center


        return {

            "trajectory":
                trajectory,

            "total_distance":
                total_distance,

            "movement":
                (
                    "MOVING"
                    if total_distance > 50
                    else
                    "STATIONARY"
                )

        }