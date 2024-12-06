import os, subprocess, glob, copy, secrets

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

    original_WD = os.getcwd()

    os.chdir('..')
    project_dir = os.getcwd()

    for repo in repos:
        print('>> synching: %s'%(repo))
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

    if synchself:
        print('Not synching myself for now...')

    # get back to original working directory?
    os.chdir(original_WD)

def setupDataFolders(tasks='all'):

    if isinstance(tasks, str):
        if tasks == 'all':
            tasks = ['distance',
                     'area',
                     'curvature']

    if not(isinstance(tasks, list)):
        return

    original_WD = os.getcwd()

    os.chdir('..')
    project_dir = os.getcwd()

    for task in tasks:

        os.makedirs(os.path.join(project_dir, 'data', task, ''), exist_ok=True)

        for subdir in ['color', 'mapping', 'eyetracking']:
            os.makedirs(os.path.join(project_dir, 'data', task, subdir, ''), exist_ok=True)

    os.chdir(original_WD)


def findParticipantIDs(tasks='all', subtasks='all'):

    if isinstance(tasks, str):
        if tasks == 'all':
            tasks = ['distance',
                     'area',
                     'curvature']

    if isinstance(subtasks, str):
        if subtasks == 'all':
            subtasks = ['',
                        'color',
                        'mapping']

    participantIDs = []

    for task in tasks:
        for subtask in subtasks:
            fullpathnames = glob.glob(os.path.join('..', 'data', task, subtask, '*.txt'))
            filenames = [os.path.basename(x) for x in fullpathnames]
            taskIDs = [x.split('_')[0] for x in filenames]

            participantIDs = list(set(participantIDs + taskIDs))
            
    if '' in participantIDs:
        participantIDs.remove('')

    return(participantIDs)


def collectParticipantInfo():

    info = {}
    # how should this be structured?
    # like this?
    empty_participant = {
        'distance' :
            {
                'color'       : False,
                'mapping'     : False,
                'left'        : False,
                'right'       : False
            },
        'area' :
            {
                'color'       : False,
                'mapping'     : False,
                'left'        : False,
                'right'       : False
            },
        'curvature' :
            {
                'color'       : False,
                'mapping'     : False,
                'left'        : False,
                'right'       : False
            }
    }

    # if location == None:
    #     if os.sys.platform == 'linux':
    #         location = 'toronto'
    #     else:
    #         location = 'glasgow'

    # pre = {'toronto':'TOR', 'glasgow':'GLA'}[location]
    
    # then info could be populated with changed versions of the empty participant
    # keys can easily be extracted when generating new / unique participant IDs
    # or to show which tasks have already been completed by the participant
    # we can also write a function to count the number of data sets in each task
    # (having all 4 files... check the eye-tracking file as well?)

    # first we collect participant IDs from the color calibration folders:
    # that is the first task, so those are the only IDs that matter (right? right!?)

    participantIDs = findParticipantIDs()

    for ID in participantIDs:
        participantInfo = copy.deepcopy(empty_participant)

        for task in ['area', 'curvature', 'distance']:
            for subtask in ['color','mapping','left','right']:

                if subtask == 'color':
                    # write test to see if a single color calibration file exists
                    # participantInfo[task][subtask] == True
                    pass

                if subtask == 'mapping':
                    # check both left and right hemisphere blind spot marker info
                    # participantInfo[task][subtask] == True
                    pass

                if subtask == 'left':
                    pass

                if subtask == 'right':
                    pass


    
    return(participantIDs)

def getParticipantTaskInfo(ID):

    info = {}

    for task in ['area', 'curvature', 'distance', 'orientation']:
        info[task] = {}
        for subtask in ['color','mapping','RH','LH']:

            if subtask in ['color', 'mapping']:
                file_list = glob.glob(os.path.join('..', 'data', task, subtask, ID + '_*.txt' ) )

            if subtask in ['LH', 'RH']:
                file_list = glob.glob(os.path.join('..', 'data', task, ID + '*' + subtask + '*.txt' ) )
                # these should be checked for completeness !!!

            if len(file_list):
                info[task][subtask] = True
            else:
                info[task][subtask] = False

    return(info)              

def getGeneralDataInfo():
    
    tasks = ['distance',
             'area',
             'curvature']

    subtasks = ['',
                'color',
                'mapping']

    allParticipantIDs = []
    taskParticipants = {'distance':[],
                        'area':[],
                        'curvature':[]}


    for task in tasks:
        taskIDs = []
        for subtask in subtasks:
            fullpathnames = glob.glob(os.path.join('..', 'data', task, subtask, '*.txt'))
            filenames = [os.path.basename(x) for x in fullpathnames]
            taskIDs = taskIDs + [x.split('_')[0] for x in filenames]

            allParticipantIDs = list(set(allParticipantIDs + taskIDs))
            if '' in allParticipantIDs:
                allParticipantIDs.remove('')

        for ID in list(set(taskIDs)):
            # check if there exists a LH and RH file for each participant for this task
            if task == 'distance':
                basename = os.path.join('..', 'data', task, ID + '_dist')
            else:
                basename = os.path.join('..', 'data', task, ID + '_' + task)

            # are there any left hand files?
            left_done = False
            left  = glob.glob(basename + '_LH_*.txt')
            if len(left):
                left_done = True

            right_done = False
            right = glob.glob(basename + '_RH_*.txt')
            if len(right):
                right_done = True
            
            if all([right_done, left_done]):
                taskParticipants[task] += [ID]

    taskParticipants['all'] = list(set(taskParticipants['area']).intersection(set(taskParticipants['curvature'])).intersection(set(taskParticipants['distance'])))

    for key in taskParticipants.keys():
        taskParticipants[key] = len(taskParticipants[key])

    allParticipantIDs.sort()


    return({'IDs':allParticipantIDs,
            'counts':taskParticipants})


def generateRandomParticipantID(prepend='', nbytes=3):

    existingIDs = findParticipantIDs()

    newID = prepend + secrets.token_hex(nbytes)
    while newID in existingIDs:
        newID = prepend + secrets.token_hex(nbytes)

    return(newID)
