import os, subprocess

def pullGitRepos(repos='all', main=True, clone=False):

    if isinstance(repos, str):
        if repos == 'all':
            repos = ['Calibration',
                     'EyeTracking',
                     'Distance',
                     'Area',
                     'Curvature',
                     'Analyses',
                     'Runner']
    
    if not(isinstance(repos, list)):
        return
    elif 'Runner' in repos:
        synchself=True # do this last: danger zone?
        repos.remove('Runner')

    os.chdir('..')
    project_dir = os.getcwd()

    for repo in repos:
        os.chdir(project_dir)
        # check if the directory exists:
        if os.path.isdir(repo):
            # go into the directory,
            os.chdir(repo)
            # switch to main?
            if main:
                subprocess.run(["git", "checkout", "main"])
            # and pull from remote
            subprocess.run(["git", "pull"])
        else:
            if clone:
                subprocess.run(["git", "clone", "https://github.com/Intrepid-2a/%s.git"%(repo)])

def collectParticipantInfo():

    info = {}
    # how should this be structured?
    # like this?
    empty_participant = {
        'location'    : ['nowhere'],
        'distance' :
            {
                'color'       : [False],
                'mapping'     : [False],
                'left'        : [False],
                'right'       : [False]
            },
        'area' :
            {
                'color'       : [False],
                'mapping'     : [False],
                'left'        : [False],
                'right'       : [False]
            },
        'curvature' :
            {
                'color'       : [False],
                'mapping'     : [False],
                'left'        : [False],
                'right'       : [False]
            }
    }
    # then info could be populated with changed versions of the empty participant
    # keys can easily be extracted when generating new / unique participant IDs
    # or to show which tasks have already been completed by the participant
    # we can also write a function to count the number of data sets in each task
    # (having all 4 files... check the eye-tracking file as well?)



