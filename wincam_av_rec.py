import os
import time
import json
import shutil
import datetime
import subprocess
import pywinauto

from ntp import RequestTimefromNtp

def win_record(seconds,
               repeat,
               dst,
               sys_dir
               ):
    """
    seconds: the expected recording length in seconds.
    repeat: the number of videos expected to record in one run.
    dst: the directory of dataset.
    sys_dir: the Windows Camera APP default save directory, normally in C dirve, like C:/Users/tangc/Pictures/Camera Roll
    """

    if not os.path.exists(dst):
        os.makedirs(dst)

    subprocess.run('start microsoft.windows.camera:', shell=True)  # open camera app
    time.sleep(2)  # have to sleep

    # take control of camera window to take video
    desktop = pywinauto.Desktop(backend="uia")
    cam = desktop['相机'] # change the number of camera app according to your system, english version should be "Camera"
    # make sure in video mode
    if cam.child_window(title="切换到 视频 模式", control_type="Button").exists(): # change the name according to your app: switch to video mode
        cam.child_window(title="切换到 视频 模式", control_type="Button").click_input() # change the name according to your app: switch to video mode
    time.sleep(1)

    for r in range(0, repeat):
        # # start then stop video
        str_dtime, strt = RequestTimefromNtp()
        cam.child_window(title="录制视频", control_type="Button").click_input() # change the name according to your app: start record
        time.sleep(seconds)
        cam.child_window(title="停止拍摄视频", control_type="Button").click_input() # change the name according to your app: stop record
        end_dtime, endt = RequestTimefromNtp()
        time.sleep(3)

        # retrieve vids from camera roll and sort
        all_contents = list(os.listdir(sys_dir))
        vids = [f for f in all_contents if "_Pro.mp4" in f]
        vids.sort()
        vid = vids[-1]  # get last vid

        # compute time difference
        vid_time = vid.replace('WIN_', '').replace('_Pro.mp4', '')
        vid_time = datetime.datetime.strptime(vid_time, '%Y%m%d_%H_%M_%S')
        now = datetime.datetime.now()
        diff = now - vid_time
        # time different greater than duration plus 1 minute, assume something wrong & quit
        if diff.seconds > (seconds + 60):
            break
        
        # copy video from system loc to dataset loc.
        shutil.copy2(sys_dir+'/'+vid, dst)

        # write timestamp to json
        temp_dict = {
            "start_dtime": str_dtime,
            "start_time": strt,
            "end_dtime": end_dtime,
            "end_time": endt 
        }

        with open(dst+"/"+vid.replace(".mp4", '.json'), "w") as outfile:
            json.dump(temp_dict, outfile)

    subprocess.run('Taskkill /IM WindowsCamera.exe /F', shell=True)  # close camera app
    print('Recorded successfully!')

if __name__ == "__main__":
  win_record(seconds=5, 
             repeat=3,
             dst='D:/Glasgow/lip_detection/video_audio_rec/test',
             sys_dir = 'C:/Users/tangc/Pictures/Camera Roll'
           )