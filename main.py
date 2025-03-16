import cv2 
import numpy as np
from utils.video_utils import read_video, save_video
from utils.data_export import save_tracks_to_csv 
from trackers import Tracker
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator





def main():
    # read video
    video_frames = read_video('input/08fd33_4.mp4')  

    #initialize Tracker
    tracker = Tracker('models/best.pt')

    tracks = tracker.get_object_tracks(video_frames,
                                       read_from_stub=[True],
                                       stub_path='stubs/track_stubs.pkl')
    

    # Get object positions 
    tracker.add_position_to_tracks(tracks)
    
    # camera movement estimator
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,
                                                                                read_from_stub=True,
                                                                                stub_path='stubs/camera_movement_stub.pkl')
    camera_movement_estimator.add_adjust_positions_to_tracks(tracks,camera_movement_per_frame)


    
    # View Trasnformer
    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)

    
    
    '''print("===== Debugging tracks['ball'] =====")
    for frame_num, ball_data in enumerate(tracks['ball']):
        print(f"Frame {frame_num}: {ball_data}")
    print("=====================================")'''



    # Assign Players Teams
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0],
                                    tracks['players'][0])
    
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num],
                                                 track['bbox'],
                                                 player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team] 
    
    
    
    
    # Assign Ball Aquisition
    
    player_assigner =PlayerBallAssigner()
    team_ball_control= []
    for frame_num, player_track in enumerate(tracks['players']):
        if 1 in tracks['ball'][frame_num]:
            ball_bbox = tracks['ball'][frame_num][1]['bbox']
            assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)
        else:
            continue


        if assigned_player != -1:
            tracks['players'][frame_num][assigned_player]['has_ball'] = True
            team_ball_control.append(tracks['players'][frame_num][assigned_player]['team'])
        else:
            team_ball_control.append(team_ball_control[-1])
    team_ball_control= np.array(team_ball_control)

    
    
    # Interpolate Ball Positions
    tracks["ball"] = tracker.interpolate_ball_positions(tracks['ball'])

    

    
    # Speed and distance estimator
    speed_and_distance_estimator = SpeedAndDistance_Estimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    
    
    
    
    #draw output
    ## draw object tracks
    output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control)

    
    # Draw Camera movement
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames,camera_movement_per_frame)

    ## Draw Speed and Distance
    speed_and_distance_estimator.draw_speed_and_distance(output_video_frames,tracks)


    # Save tracking data as CSV
    save_tracks_to_csv(tracks, "output_data/tracking_results.csv")

    # save video
    save_video(output_video_frames, 'output_videos/output_video_final.avi')

if __name__ == "__main__":
    main()    