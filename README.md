# Runner

This repository has the goal to provide a GUI interface to all the experimental tasks used for the Intrepid 2a project. It has no role in data analysis. The code also organizes the folder structure and downloads git repos if they do not exist in the expected location.

# Folder structure

There should be one project folder (e.g. "Intrepid2a"). This folder will have 1 subfolder each for all the repositories (which are capitalized), as well as a folder with data, called `data`. Data is sorted by experiment (`distance`. `area` and `curvature`) and within each of these there exist further subfolders for: 1) color calibration files (`color`), 2) blind spot mapping files (`mapping`) and 3) eye-tracking data (`eyetracking`).

( Previously we agreed on then also having a folder for each participant with the task data in there, but it might be more convenient to store those up-front in the main data/task/ folder, as these are the more important files. Only the supplementary data is then stored in subfolders. )

