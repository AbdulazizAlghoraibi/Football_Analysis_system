import csv
import os

def save_tracks_to_csv(tracks, output_path="output_data/tracks_data.csv"):
    
    # Saves the tracking data (players, ball, referees) into a CSV file.
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Define CSV header
    headers = ["frame", "object_type", "id", "x1", "y1", "x2", "y2", "team", "has_ball"]
    
    with open(output_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)  

        # Iterate through frames
        for frame_num, (players, referees, ball) in enumerate(zip(tracks["players"], tracks["referees"], tracks["ball"])):
            
            # Save players data
            for player_id, player_info in players.items():
                writer.writerow([
                    frame_num, "player", player_id,
                    *player_info["bbox"],
                    player_info.get("team", "unknown"),
                    player_info.get("has_ball", False)
                ])

            # Save referees data
            for ref_id, ref_info in referees.items():
                writer.writerow([
                    frame_num, "referee", ref_id,
                    *ref_info["bbox"],
                    "N/A",  
                    False   
                ])

            # Save ball data
            for ball_id, ball_info in ball.items():
                writer.writerow([
                    frame_num, "ball", ball_id,
                    *ball_info["bbox"],
                    "N/A",  
                    False   
                ])

    print(f" Tracking data saved successfully to {output_path}")
