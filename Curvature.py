"""
Motion curvature estimation across blind spot
TWCF IIT vs PP experiment 2a piloting
Authors: Belén María Montabes de la Cruz, Clement Abbatecola
    Code Version:
        2.0 # 2024/04/09    Final common version before eye tracking

"""

from psychopy import core, visual, gui, data, event
from psychopy.tools.coordinatetools import pol2cart, cart2pol
from psychopy.tools.mathtools import distance
import numpy as np
import random, datetime, os
from glob import glob
from itertools import compress

from psychopy.hardware import keyboard
from pyglet.window import key

import sys, os
# sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import localizeSetup, EyeTracker

def placeCurvatureDots(B, C, curvature):

    # print([B, C, curvature])

    # B: coordinates of point B
    # C: coordinates of point C
    # curvature: the amount of curvature for the previous and next points

    # Assuming the time that passes between presentation of B and C
    # is equal to the time passing between A and B and between C and D
    # the location of A and D can be calculated, such that the 2 triplets 
    # of points have the specified curvature.

    # First, we need B to be lower on the screen than C:
    if B[1] > C[1]:
        B, C = C, B

    # Then, if the specified curvature is 0, this is a special case
    # for which the equation doesn't work...
    #
    # ... but the 4 points should lie on a straight line:

    if curvature == 0:
        A = [B[0] - (C[0]-B[0]), B[1] - (C[1]-B[1])]
        D = [C[0] + (C[0]-B[0]), C[1] + (C[1]-B[1])]
        # we return this result:
        # return([A, B, C, D]) # this returned a tuple, while for non-zero curvature, the function returns an array
        return(np.array([A,B,C,D]))

    # If the curvature is not 0, we need to do some more work.

    # distance between B and C:
    dist = ((B[0] - C[0])**2 + (B[1] - C[1])**2)**0.5
    
    # print(dist)

    # the radius of the circle describing the curvature:
    R = 1 / np.abs(curvature)

    # print(R)

    # The angle between two lines drawn through the origin
    # of the circle of curvature and the two points:
    ang_rad = 2 * ( (np.pi/2) - np.arccos( (dist/2) / R ) )

    # print(ang_rad)

    # Get the angle in radians for all 4 points,
    # with B and C in the middle:
    point_angles = [ang_rad * x for x in [-1.5,-.5,.5,1.5]]
    
    # print(point_angles)

    # Now get the coordinates of the 4 points:
    # point_coords = [[np.cos(xa)*R, np.sin(xa)*R] for xa in point_angles]
    # in an array:
    point_coords = np.array([np.cos(point_angles)*R, np.sin(point_angles)*R]).T

    # print(point_coords)
    
    # Right now, the curvature is always toward fixation
    # but the relative placement is correct,
    # we just need to move things around a bit.

    # First we correct for our positive and negative curvature.
    # This does not really exist, we just define negative curvature
    # to mean 'away from fixation'.
    point_coords = point_coords - [R,0]
    if curvature < 0:
        point_coords[:,0] *= -1
    
    # Now we flip the points if the original B and C are to the left:
    if np.mean([B[0], C[0]]) < 0:
        point_coords[:,0] *= -1
    
    # Then we reposition the points such that the current B (2nd) point
    # is at [0,0]:
    point_coords -= point_coords[1,:]

    # We get the original and current angle of a line through the 2nd
    # and 3rd point:
    orig_ang = np.arctan2(C[1]-B[1], C[0]-B[0])
    curr_ang = np.arctan2(point_coords[2,1], point_coords[2,0])

    # Rotate the current points by the difference to match the input orientation:
    th = orig_ang - curr_ang
    Rm = np.array([[np.cos(th), -1*np.sin(th)],[np.sin(th),np.cos(th)]])
    point_coords = Rm @ point_coords.T

    # print(point_coords)

    # Translate such that the second and third point match the input locations:
    point_coords = point_coords.T + B

    # That should be all, so we return all 4 coordinates:
    return(point_coords)



def doCurvatureTask(hemifield=None, ID=None, location=None):

    ## path
    # main_path = "."
    # data_path = main_path + "/data/"

    expInfo = {}
    askQuestions = False
    ## files
    if ID == None:
        expInfo['ID'] = ''
        askQuestions = True

    if hemifield == None:
        expFine['hemifield'] = ['left', 'right']
        askQuestions = True

    if askQuestions:
        dlg = gui.DlgFromDict(expInfo, title='Infos')
    

    if ID == None:
        ID = expInfo['ID']
    if hemifield == None:
        hemifield = expInfo['hemifield']

        # need to know which eye-tracker to use:
    if location == None:
        # hacky, but true for now:
        if os.sys.platform == 'linux':
            location = 'toronto'
        else:
            location = 'glasgow'



    random.seed(ID+'curvature'+hemifield)

    trackEyes = [True, True]

    # ## path
    # main_path = 'C:/Users/clementa/Nextcloud/project_blindspot/blindspot_eye_tracker/'
    # data_path = main_path + 'data/'
    main_path = '../data/curvature/'
    data_path = main_path
    eyetracking_path = main_path + 'eyetracking/' + ID + '/'
    
    # this _should_ already be handled by the Runner utility: setupDataFolders()
    os.makedirs(data_path, exist_ok=True)
    # but not this one:
    os.makedirs(eyetracking_path, exist_ok=True)

    # add functionality to name new eye-tracking file (make into generic function so it all works the same?):
    x = 1
    et_filename = 'dist' + ('LH' if hemifield == 'left' else 'RH')
    while len(glob(eyetracking_path + et_filename + str(x) + '.*')):
        x += 1


    setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename+str(x), task='curvature', ID=ID, noEyeTracker=True) # data path is for the mapping data, not the eye-tracker data!



    hiFusion = setup['fusion']['hi']
    loFusion = setup['fusion']['lo']

    blindspot = setup['blindspotmarkers'][hemifield]
    # print(blindspot.fillColor)
    
    fixation = setup['fixation']
    xfix     = setup['fixation_x']


    print(setup['paths']) # not using yet, just testing

    # unpack all this
    win = setup['win']

    colors = setup['colors']

    pyg_keyboard = key.KeyStateHandler()
    win.winHandle.push_handlers(pyg_keyboard)


    # colors = setup['colors']
    col_both = colors['both']
    if hemifield == 'left':
        col_ipsi, col_contra = colors['left'], colors['right']
    if hemifield == 'right':
        col_contra, col_ipsi = colors['left'], colors['right']

    
    x = 1
    filename = 'motion_' + {'left':'LH', 'right':'RH'}[hemifield] + ID.lower() + '_'
    while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
    respFile = open(data_path + filename + str(x) + '.txt','w')

    respFile.write(''.join(map(str, ['Start: \t' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '\n'])))
    respFile.write('\t'.join(map(str, ['TrialN',
                                        'Curvature',
                                        'Stimulus_position', 
                                        'GreenStim', 
                                        'Staircase', 
                                        'ResponseCode', 
                                        'Response', 
                                        'Reversal', 
                                        'AllTrials', 
                                        'StairsOngoing'])) + '\n')
    respFile.close()



    ######
    ## Prepare stimulation
    ######

    ## Parameters

    ## stimuli
    point1 = visual.Circle(win, radius = .7, pos = pol2cart(00, 6), fillColor = 'white', lineColor = None, units = 'deg')
    point2 = visual.Circle(win, radius = .7, pos = pol2cart(00, 6), fillColor = 'white', lineColor = None, units = 'deg')
    point3 = visual.Circle(win, radius = .7, pos = pol2cart(00, 6), fillColor = 'white', lineColor = None, units = 'deg')
    point4 = visual.Circle(win, radius = .7, pos = pol2cart(00, 6), fillColor = 'white', lineColor = None, units = 'deg')

    #########

    ## Circle positions and other hemifield dependencies

    # shouldn't this be different for left and right hemifield runs?

    bs_prop = setup['blindspotmarkers'][hemifield+'_prop']


    # Padding angles =  BSheight/3 + 2 (dotwidth) + 1(padding) --> value obtained from piloting
    # angpad = spot_righ_size[1]/3 + 2 + 1
    angpad = (bs_prop['size'][1]/3) + 2 + 1
    # Padding on circle side

    # this could be negative padding?
    # side = (spot_righ_size[1] - spot_righ_size[0])*0.15/0.5
    side = (bs_prop['size'][1] - bs_prop['size'][0]) * 0.15/0.5

    # ============================
    # MARIUS interpretation:

    # distance between dots in the trajectory should be related to the height of the blind spot:
    # dot_distance = bs_prop['size'][1] / 3
    # no, we'll keep a standard stimulus size for all participants:
    dot_distance = 2

    # stimulus width should be related to dot offset at maximum curvature:
    max_curvature_points = placeCurvatureDots(  B = [0,dot_distance/2],
                                                C = [0,-dot_distance/2],
                                                curvature = 0.4)

    stim_width = np.abs(max_curvature_points[0,0]) + 0.7
    # for me, this is 2.3145021189054944 dva... maybe we don't need to add the dot radius?

    # to get an angular offset, lets move things along a circle, by a distance equal to the minimum distance between stimuli:
    arc_length = (bs_prop['size'][1] * 1.0)  # maybe it should be higher ? no... less is fine, other wise we get close to the fusion stims

    # and with a radius that moves away from the blind spot center, toward fixation with enough padding (stim width and 2 dva extra)
    r = np.sqrt( (abs(bs_prop['cart'][0]) - (bs_prop['size'][0]/2) - 2 - stim_width)**2 + bs_prop['cart'][1]**2 )
    C = 2*np.pi*r                 # total circumference
    ang_up = (arc_length/C)*360   # is this correct? (propertion of total circumference * 360)

    # the direction by which the 'above' blind spot position is rotated, depends on hemifield:
    ang_mod = 1 if hemifield == 'right' else -1

    # at blind spot middle of trajectory:
    if hemifield == 'right':
        bsm_x = bs_prop['cart'][0] - (bs_prop['size'][0]/2) - 2 - stim_width
    else:
        bsm_x = bs_prop['cart'][0] + (bs_prop['size'][0]/2) + 2 + stim_width
    bsm = [bsm_x, bs_prop['cart'][1]]

    # positions in cartesian coordinates:
    positions = [ [ [sum(x) for x in zip(pol2cart(cart2pol(bsm[0], bsm[1])[0] + (ang_up*ang_mod), r), [0,dot_distance/2 ])],
                    [sum(x) for x in zip(pol2cart(cart2pol(bsm[0], bsm[1])[0] + (ang_up*ang_mod), r), [0,dot_distance/-2])] ],
                  [ [bsm[0], bsm[1]+(dot_distance/2)],
                    [bsm[0], bsm[1]-(dot_distance/2)] ] ]

    # print(positions)

    # end MARIUS interpretation

    # do we need different instructions? could be in terms of towards/away from fixation as it is now,
    # but it could also be: to the right / left, so it's independent of hemifield... (and maybe easier for participants as well?)

    if hemifield == 'right':
        instructions = visual.TextStim(win, text="Throughout the experiment you will fixate a cross located at the centre of the screen. It is important that you maintain fixation on this cross at all times.\n\n In every trial you will be presented with a dot which will move along a curve. You will have to indicate with a keypress if the dot's motion was curved towards fixation or away from fixation  \n \nLeft arrow = motion curved towards fixation.\n \n Right arrow = motion curved away from fixation.\n\n\n You will only be able to respond when the fixation cross rotates from a '+' to a 'x' \n\n\n Press the space bar when you're ready to start the experiment.", color=col_both)
    else:
        instructions = visual.TextStim(win, text="Throughout the experiment you will fixate at a a cross located at the centre of the screen. It is important that you maintain fixation on this cross at all times.\n\n In every trial you will be presented with a dot which will move along a curve. You will have to indicate with a keypress if the dot's motion was curved towards fixation or away from fixation  \n \nLeft arrow = motion curved away from fixation.\n \n Right arrow = motion curved towards fixation.\n\n\nYou will only be able to respond when the fixation cross rotates from a '+' to a 'x' \n\n\n Press the space bar when you're ready to start the experiment.")



    ## Experiment instructions
    instructions.wrapWidth = 30
    instructions.draw()
    win.flip()
    event.waitKeys(keyList='space')


    ## Experimental parameters

    ## Curvatures, note that 0.000001 instead of 0 to avoid crushing
    # this is 33 values, instead of the 15 we use in the distance task... this should affect the staircases: more trials and reversals needed?

    curvature = [round((x / 20)-0.4, ndigits=3) for x in list(range(0,17))]   # NEW 17 points only

    ## staircase
    # step has the current index into the list of curvatures for each staircase
    step = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]] #[['left', 'right'], ['left', 'right']]

    # direction flips the index into the curvature list, although we could have also just started at the max of step in half the staircases
    direction = [[[1, -1], [1, -1]], [[1, -1], [1, -1]]] # 2 directions per eye and position converging to straight
    # which eye sees the stimuli? (i.e. which color are the stimuli displayed in?)
    eye = [0, 1] #0 = col_left = red, 1 = col_righ = green

    eyecol = [col_ipsi, col_contra] # use contra and ipsi colors?

    revs = [[0, 0], [0, 0]], [[0, 0], [0, 0]] #counter for the number of reversals
    trial = [[0, 0], [0, 0]], [[0, 0], [0, 0]] #counter for the trail number
    Nrevs = 10 #following the dist task - 20/2 - 10
    Ntrials = 30 #following the dist task - 60/2 - 30
    resps = [[[[], []], [[], []]], [[[], []], [[], []]]] #keeps track of responses for the reversals
    stairs_ongoing = [[[True, True], [True, True]], [[True, True], [True, True]]] #to end experiment [left pos0, right pos0] [left pos1, right pos1] 
    not_ongoing = [[[False, False], [False, False]], [[False, False], [False, False]]] #to end experiment
    abort = False
    choice = []
    #keeping track of time
    trial_clock = core.Clock()


    while not stairs_ongoing == not_ongoing:


        #1. Select the position to draw on
        if  stairs_ongoing[0] == [[False, False], [False, False]]: # doing all(stairs_ongoing[1]) leads to error = 'list indices must be integers or slices, not list'
            position = 1
            #print('stair 0 = ', stairs_ongoing[0],'pos =', position)
        elif stairs_ongoing[1] == [[False, False], [False, False]]:#if position1=done   --- try any
            position = 0
            #print('stair 0 = ', stairs_ongoing[1],'pos =', position)
        elif any(stairs_ongoing[0]) == True and any(stairs_ongoing[1]) == True:
            position = np.random.choice([0, 1]) # 1 = above, 2 = BS
            #print('both stairs ongoing, pos = ', position) 
        #2. Select the eye to stimulate
        if stairs_ongoing[position][0] == [False, False]:
            eye = 1
        elif stairs_ongoing[position][1] == [False, False]:
            eye = 0
        elif any(stairs_ongoing[position][0]) == True and any(stairs_ongoing[position][1]) == True:
            eye = np.random.choice([0, 1])
        # 3. Select the staircase to draw (i.e. curvature towards or curvature away)
        staircase = np.random.choice(list(compress([0, 1], stairs_ongoing[position][eye])))
        fixation.color = col_both 

        point2.pos = positions[position][0]
        point3.pos = positions[position][1]
        
        ##position of first and fourth dots (mobile, either curved towards or curved away)
        tstep = step[position][eye][staircase] if step[position][eye][staircase] >0 else step[position][eye][staircase]*-1 #-1 to prevent it from being negative
        # why would it be negative?

        currentcurv = direction[position][eye][staircase] * curvature[tstep]
        print('currently we are at', currentcurv, 'current step =', tstep)
        coords = placeCurvatureDots(point2.pos, point3.pos, currentcurv)

        point1.pos = coords[3]
        point4.pos = coords[0]

        point1.fillColor =  eyecol[eye]
        point2.fillColor =  eyecol[eye]
        point3.fillColor =  eyecol[eye]
        point4.fillColor =  eyecol[eye]

        hiFusion.resetProperties()
        loFusion.resetProperties()
        
        trial_clock.reset()

        
        tp = trial_clock.getTime()
        while tp < 1.7:
            tp = trial_clock.getTime()
            blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
            
            if any([0.5 < tp < 0.6, 1.2 < tp < 1.4                ]):
                point1.draw()
            if any([0.6 < tp < 0.7, 1.1 < tp < 1.2, 1.4 < tp < 1.5]):
                point2.draw()
            if any([0.7 < tp < 0.8, 1.0 < tp < 1.1, 1.5 < tp < 1.6]):
                point3.draw()
            if any([0.8 < tp < 1.0,                 1.6 < tp < 1.7]):
                point4.draw()
            
            win.flip()


        hiFusion.draw()
        loFusion.draw()
        xfix.draw()
        win.flip()

        #Wait for responses
        k = ['wait']
        while k[0] not in ['q', 'space', 'left', 'right']:
            k = event.waitKeys()

        # deal with q/quit:
        if k[0] in ['q']:
            abort = True
            break
        # deal with space/abort
        if k[0] in ['space']:
            choice = 'Trial aborted'
            move = 0
            # trial_clock.reset()
        
        # get a move on the staircase:
        if k[0] in ['left', 'right']:
            # register button pressed:
            choice = k[0]
            # pick movement direction on staircase, depending on response: 
            move = {'right':-1, 'left':+1}[k[0]]
            # invert for inverted dircetions:
            move = move * direction[position][eye][staircase]
            # invert for left hemifield:
            move = move * {'right':1, 'left':-1}[hemifield]
            # make the move:
            step[position][eye][staircase] += move

        # now correct out of bounds moves:
        if step[position][eye][staircase] < 0:
            step[position][eye][staircase] == 0
            choice = 'NA'
        if step[position][eye][staircase] >= len(curvature):
            step[position][eye][staircase] = len(curvature) - 1
            choice = 'NA'

                
        ##Adapting the staircase
        resps[position][eye][staircase]  = resps[position][eye][staircase]  + [choice]
        #sets the bounds for the staircase
        ## Reversals
        if resps[position][eye][staircase][-2:] == ['left', 'right'] or resps[position][eye][staircase][-2:] == ['right', 'left']: 
            revs[position][eye][staircase]  = revs[position][eye][staircase]  + 1

        

        if abort:
                break # in this case: quit the task, not abort the trial
        #writing reponse file
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write('\t'.join(map(str, [trial[position][eye][staircase], 
                                        currentcurv,# Stimulus location
                                        position,
                                        eye, 
                                        staircase,
                                        [1 if k[0] == 'left' else 2][0],
                                        choice, 
                                        revs[position][eye][staircase],
                                        trial,
                                        stairs_ongoing])) + "\n") #block
        respFile.close()
        #final updates
        if not choice == 'Trial aborted':
            trial[position][eye][staircase]  = trial[position][eye][staircase]  +1
        else:
            pass
        ##Check if experiment can continue
        stairs_ongoing[position][eye][staircase]  = revs[position][eye][staircase]  <= Nrevs or trial[position][eye][staircase]  < Ntrials

    ## Closing prints
    bye = visual.TextStim(win, text="Run ended.\nPress space bar to exit")
    if abort:
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write("Run manually ended at " + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + "!")
        respFile.close()
        bye = visual.TextStim(win, text="Run manually ended \n Press space bar to exit")
    elif not any(stairs_ongoing):
        print('run ended properly!')
        bye = visual.TextStim(win, text="You have now completed the experimental run.\nThank you for your participation!!\n\nPress space bar to exit")

    blindspot.autoDraw = False
    ## Farewells
    bye.draw() # there was no bye stim defined on my runs... creating default stim above
    win.flip()
    event.waitKeys()

    win.close()

