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
from numpy import ndarray
import random, datetime, os
import math
from math import sin, cos, radians, pi # why not use from numpy?
from glob import glob
from itertools import compress

from psychopy.hardware import keyboard
from pyglet.window import key

# from fusion_stim import fusionStim
# from curvature import placeCurvatureDots


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
        return(np.array([A,B,C,D])[0,:,:])

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

    ## colour (eye) parameters

    # col_file = open(glob(main_path + "/mapping_data/" + expInfo['ID'] + "_col_cal*.txt")[-1],'r')
    # col_param = col_file.read().replace('\t','\n').split('\n')
    # col_file.close()
    # col_left = eval(col_param[3]) # red 
    # col_righ = eval(col_param[5]) # green
    # col_both = [-0.7, -0.7, -0.7] # dark gray that is similar to the rg through glasses
    # col_back = [ 0.55, 0.45, -1.0] #changed by belen to rpevent red bleed


    ## Blind Spot Parameters
    # bs_file = open(glob(main_path + "/mapping_data/" + expInfo['ID'] + "_" + hem +  "_blindspot*.txt")[-1],'r')
    # bs_param = bs_file.read().replace('\t','\n').split('\n')
    # bs_file.close()
    # spot_righ_cart = eval(bs_param[1])
    # spot_righ = cart2pol(spot_righ_cart[0], spot_righ_cart[1])
    # spot_righ_size = eval(bs_param[3])
    # print("angles and radians", spot_righ)

    ## Window & elements
    # win = visual.Window([1720,1100],allowGUI=True, monitor='testMonitor', units='deg',  fullscr = False, color=col_back, screen=1)
    # win.mouseVisible = False
    # fixation = visual.ShapeStim(win, vertices = ((0, -2), (0, 2), (0,0), (-2, 0), (2, 0)), lineWidth = 4, units = 'pix', size = (10, 10), closeShape = False, lineColor = col_both)
    # xfix = visual.ShapeStim(win, vertices = ((-2, -2), (2, 2), (0,0), (-2, 2), (2, -2)), lineWidth = 4, units = 'pix', size = (10, 10), closeShape = False, lineColor = col_both)


    ######
    ## Prepare stimulation
    ######

    ## Parameters


    # In [16]: setup['blindspotmarkers']
    # Out[16]: 
    # {'left_prop': {'cart': [-15.84, -1.47],
    #   'spot': (-174.6979643253833, 15.908063992830806),
    #   'size': [5.21, 5.76],
    #   'tar': 9.21,
    #   'ang_up': 21.231788356874432},
    #  'left': <psychopy.visual.circle.Circle at 0x7fd3cd1f3100>,
    #  'right_prop': {'cart': [15.02, -2.37],
    #   'spot': (-8.966749923798016, 15.205831118357194),
    #   'size': [5.97, 5.59],
    #   'tar': 9.969999999999999,
    #   'ang_up': 23.066717128968264},
    #  'right': <psychopy.visual.circle.Circle at 0x7fd3d2a1faf0>}



    ## BS stimuli
    # blindspot = visual.Circle(win, radius = .5, pos = [7,0], lineColor = None)
    # blindspot.pos = spot_righ_cart
    # blindspot.size = spot_righ_size

    ## Fusion Stimuli  -copy distance

    # hiFusion = fusionStim(win=win, pos=[0, 0.8], colors = [col_back, col_both], columns=1, rows=5, square=0.07, units='norm', fieldShape = 'square')
    # loFusion = fusionStim(win=win, pos=[0,-0.8], colors = [col_back, col_both], columns=1, rows=5, square=0.07, units='norm', fieldShape = 'square')

    ## stimuli
    point1 = visual.Circle(win, radius = .7, pos = pol2cart(00, 6), fillColor = 'white', lineColor = None, units = 'deg')
    point2 = visual.Circle(win, radius = .7, pos = pol2cart(00, 6), fillColor = 'white', lineColor = None, units = 'deg')
    point3 = visual.Circle(win, radius = .7, pos = pol2cart(00, 6), fillColor = 'white', lineColor = None, units = 'deg')
    point4 = visual.Circle(win, radius = .7, pos = pol2cart(00, 6), fillColor = 'white', lineColor = None, units = 'deg')

    #########

    # print(setup['blindspotmarkers'])

    ## Circle positions and other hemifield dependencies

    # shouldn't this be different for left and right hemifield runs?

    bs_prop = setup['blindspotmarkers'][hemifield+'_prop']

            # blindspotmarkers[hemifield+'_prop'] = { 'cart'   : spot_cart,
            #                                     'spot'   : spot,
            #                                     'size'   : spot_size,
            #                                     'tar'    : tar,
            #                                     'ang_up' : ang_up       }

   

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
    dot_distance = bs_prop['size'][1] / 3

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






    # Protocol paper says:

    # - points are above/below this point:
    #     - point on line between fixation and centre of blind spot marker
    #     - distance to fixation is same distance to blind spot centre - (blind spot width/2) - 4 dva (padding)


    # - above/below blind spot locations the angle is increased/decreased by half the blind spot height (in angular difference relative to fixation)


    # cart2pol return: (theta, radius)  # i.e.: angle and distance, in that order

    # #Positions by hemifield
    # if hemifield == 'right':
    #     # angle division between BS and outside locations = polar angle of the BS x and y + BS size) - angle of the BS location (dev from 0) / 2 + 2(dot stimulus size) + 2 (padding)
    #     # angup = (cart2pol(spot_righ_cart[0], spot_righ_cart[1] + spot_righ_size[1])[0] - spot_righ[0])/2 + 2 + 2

    #     angup = (cart2pol(bs_prop['cart'][0], bs_prop['cart'][1] + bs_prop['size'][1])[0] - bs_prop['spot'][0])/2 + 4

    #     # spot_righ[0] is the angle (degrees) of the centre of the blind spot relative to fixation
    #     # the cart2pol(...)[0] part returns the angle of a point (relative to fixation) that is:
    #     # -  straight above the centre of the blind spot marker
    #     # -  but offset by the height of the blind spot marker
    #     # so the difference between those, divided by 2
    #     # gives something that is usually close to half the height of the blind spot marker in degrees angle, relative to fixation
    #     # adding 4 degrees angle (not dva!)

    #     #positions
    #     # positions = {
    #     # "righ-top": [pol2cart(spot_righ[0] + 3*angup, spot_righ[1] - spot_righ_size[0]-side)],
    #     # "righ-mid": [pol2cart(spot_righ[0] + angpad,  spot_righ[1] - spot_righ_size[0]-side), 
    #     #              pol2cart(spot_righ[0] -angpad, spot_righ[1]- spot_righ_size[0]-side)],
    #     # }


    #     # why are we pretending that the blind spot marker is a circle, when we calibrate it as an ellipse?
    #     # https://math.stackexchange.com/questions/22064/calculating-a-point-that-lies-on-an-ellipse-given-an-angle

    #     positions = {
    #     "righ-top": [pol2cart(bs_prop['spot'][0] + 3*angup, bs_prop['spot'][1] - bs_prop['size'][0]-side)],
    #     "righ-mid": [pol2cart(bs_prop['spot'][0] + angpad,  bs_prop['spot'][1] - bs_prop['size'][0]-side), 
    #                  pol2cart(bs_prop['spot'][0] - angpad,  bs_prop['spot'][1] - bs_prop['size'][0]-side)],
    #     }

    #     # angpad is not an angle, but a distance... should not be used here?


    #     poss = list(positions.items()) #list of positions used in experiment

    #     # these are the positions:
    #     print(poss)

    #     #to make top stimuli parallel to BS # why are there 4 levels? the input dictionary has 3...
    #     ydif = (poss[1][1][0][1]-poss[1][1][1][1])/2
    #     if poss[1][1][0][0] > poss[1][1][1][0]:
    #         xdif = (poss[1][1][0][0]-poss[1][1][1][0])/2
    #     else:
    #         xdif = (poss[1][1][1][0]-poss[1][1][0][0])/2

    #     print(xdif) # xdif should be 0? why does this have any value at all?

    #                 # ydif should be scaled with the height of the blind spot... it kind of is

    #     # #BS color
    #     # blindspot.fillColor = col_righ
    #     # Instructions
    #     instructions = visual.TextStim(win, text="Throughout the experiment you will fixate a cross located at the centre of the screen. It is important that you maintain fixation on this cross at all times.\n\n In every trial you will be presented with a dot which will move along a curve. You will have to indicate with a keypress if the dot's motion was curved towards fixation or away from fixation  \n \nLeft arrow = motion curved towards fixation.\n \n Right arrow = motion curved away from fixation.\n\n\n You will only be able to respond when the fixation cross rotates from a '+' to a 'x' \n\n\n Press the space bar when you're ready to start the experiment.", color=col_both)

    # else:


    #     # THIS USES THE RIGHT BLIND SPOT MARKER, NOT THE LEFT!

    #     # angle division between BS and outside locations = polar angle of the BS x and y - BS size) - angle of the BS location (dev from 0) / 2 + 2(dot stimulus size) + 2 (padding)
    #     angup = (cart2pol(spot_righ_cart[0], spot_righ_cart[1] - spot_righ_size[1])[0] + spot_righ[0])/2 + 2 + 2

    #     # positions
    #     positions = {
    #     "left-top": [pol2cart(spot_righ[0] + 3*angup, spot_righ[1] -  spot_righ_size[0]-side)], # this has 1 set of coordinates
    #     "left-mid": [pol2cart(spot_righ[0] -angpad,  spot_righ[1] - spot_righ_size[0]-side),    # this has 2 ? are those the above & below positions?
    #     pol2cart(spot_righ[0] -angpad, spot_righ[1]- spot_righ_size[0]-side)],
    #     }
    #     poss = list(positions.items()) #list of positions used in experiment

    #     # the block below is the same as for the right hemifield... 
    #     # move out of the if-else thing and only do once?

    #     # to make top stimuli parallel to BS
    #     ydif = (poss[1][1][0][1]-poss[1][1][1][1])/2
    #     if poss[1][1][0][0] < poss[1][1][1][0]:
    #         xdif = (poss[1][1][0][0]-poss[1][1][1][0])/2
    #     else:
    #         xdif = (poss[1][1][1][0]-poss[1][1][0][0])/2
    #     # #BS color
    #     # blindspot.fillColor = col_left

    #     # Instructions
    #     instructions = visual.TextStim(win, text="Throughout the experiment you will fixate at a a cross located at the centre of the screen. It is important that you maintain fixation on this cross at all times.\n\n In every trial you will be presented with a dot which will move along a curve. You will have to indicate with a keypress if the dot's motion was curved towards fixation or away from fixation  \n \nLeft arrow = motion curved away from fixation.\n \n Right arrow = motion curved towards fixation.\n\n\nYou will only be able to respond when the fixation cross rotates from a '+' to a 'x' \n\n\n Press the space bar when you're ready to start the experiment.")




    ## Experiment instructions
    instructions.wrapWidth = 30
    instructions.draw()
    win.flip()
    event.waitKeys(keyList='space')


    ## Experimental parameters

    ## Curvatures, note that 0.000001 instead of 0 to avoid crushing
    # curvature = [0.4, 0.375, 0.35, 0.325, 0.3, 0.275, 0.25,  0.225, 0.2, 0.175, 0.15, 0.125, 0.1, 0.075, 0.05, 0.025, -0.025, 0.000001,-0.000001, -0.05, -0.075, -0.1, -0.125, -0.15, -0.175, -0.2, -0.225, -0.25, -0.275, -0.3, -0.325, -0.35, -0.375, -0.4]
    # curvature = [0.4, 0.375, 0.35, 0.325, 0.3, 0.275, 0.25,  0.225, 0.2, 0.175, 0.15, 0.125, 0.1, 0.075, 0.05, 0.025, 0.000, -0.05, -0.075, -0.1, -0.125, -0.15, -0.175, -0.2, -0.225, -0.25, -0.275, -0.3, -0.325, -0.35, -0.375, -0.4]

    # this is 33 values, instead of the 15 we use in the distance task... this should affect the staircases: more trials and reversals needed?
    # curvature = [round((x / 40)-0.4, ndigits=3) for x in list(range(0,33))]

    curvature = [round((x / 20)-0.4, ndigits=3) for x in list(range(0,17))]   # NEW 17 points only

    ## staircase
    step = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]] #[['left', 'right'], ['left', 'right']]
    direction = [[[1, -1], [1, -1]], [[1, -1], [1, -1]]] # 2 directions per eye and position converging to straight
    eye = [0, 1] #0 = col_left = red, 1 = col_righ = green
    # eye: 0 = ipsi, 1 = contra
    # eyecol = [col_left, col_righ] # these colors are not defined
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

    # blindspot.autoDraw = True # hmmm... turn off when people can look away!
    # #repeated draws 
    # def repeat_draw():
    #     fixation.draw()
    #     hiFusion.draw()
    #     loFusion.draw()


    while not stairs_ongoing == not_ongoing:

        # these are not random?

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
        ##position of central dots (fixed, either above or around BS)
        # if position == 0: #above blind spot
        #     point2.pos = (poss[0][1][0][0]+xdif,poss[0][1][0][1]+ydif)
        #     point3.pos = (poss[0][1][0][0]-xdif,poss[0][1][0][1]-ydif)
        # elif position == 1: #blind spot
        #     point2.pos = poss[1][1][0]
        #     point3.pos = poss[1][1][1]
        point2.pos = positions[position][0]
        point3.pos = positions[position][1]
        
        ##position of first and fourth dots (mobile, either curved towards or curved away)
        tstep = step[position][eye][staircase] if step[position][eye][staircase] >0 else step[position][eye][staircase]*-1 #-1 to prevent it from being negative
        # why would it be negative?

        currentcurv = direction[position][eye][staircase] * curvature[tstep]
        print('currently we are at', currentcurv, 'current step =', tstep)
        coords = placeCurvatureDots(point2.pos, point3.pos, currentcurv)
        # print(coords)
        point1.pos = coords[3]
        point4.pos = coords[0]
        #color of dots - which eye to stimulate
        point1.fillColor =  eyecol[eye]
        point2.fillColor =  eyecol[eye]
        point3.fillColor =  eyecol[eye]
        point4.fillColor =  eyecol[eye]
        #resetting fusion stimuli
        hiFusion.resetProperties()
        loFusion.resetProperties()
        #drawing the stimuli
        trial_clock.reset()

        # print('resetted clock')

        # simplify this:
        # while trial_clock.getTime() < .5: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     win.flip()
        # while trial_clock.getTime() < .6: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point1.draw()
        #     win.flip()
        # while trial_clock.getTime() < .7: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point2.draw()
        #     win.flip()
        # while  trial_clock.getTime() < .8: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point3.draw()
        #     win.flip()
        # while trial_clock.getTime() < .9: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point4.draw()
        #     win.flip()
        # while trial_clock.getTime() < 1.0: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point4.draw()
        #     win.flip()
        # while trial_clock.getTime() < 1.1: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point3.draw()
        #     win.flip()
        # while trial_clock.getTime() < 1.2: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point2.draw()
        #     win.flip()
        # while trial_clock.getTime() < 1.3: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point1.draw()
        #     win.flip()
        # while trial_clock.getTime() < 1.4: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point1.draw()
        #     win.flip()
        # while trial_clock.getTime() < 1.5: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point2.draw()
        #     win.flip()
        # while  trial_clock.getTime() < 1.6: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point3.draw()
        #     win.flip()
        # while trial_clock.getTime() < 1.7: 
        #     blindspot.draw(); fixation.draw(); hiFusion.draw(); loFusion.draw()
        #     point4.draw()
        #     win.flip()
        
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

        # print('stimulus done')

        while trial_clock.getTime()  > 1.7: 
            hiFusion.draw()
            loFusion.draw()
            xfix.draw()
            win.flip()

        #Wait for responses
            k = ['wait']
            while k[0] not in ['q', 'space', 'left', 'right']:
                k = event.waitKeys()
            if hemifield == 'right':
                if k[0] in ['q']:
                    abort = True
                    break
                elif k[0] in ['left']:
                    if currentcurv == .4:
                        pass
                    else:
                        if step[position][eye][staircase] <= len(curvature)-2:
                            step[position][eye][staircase] += 1
                            # print(step[position][eye][staircase])
                            choice = 'left'
                        if step[position][eye][staircase] ==len(curvature)-1:
                            step[position][eye][staircase] -= 1
                            # print(step[position][eye][staircase])
                            choice= 'NA'
                    trial_clock.reset()
                elif k[0] in ['right']:
                    if currentcurv == -.4:
                        pass
                    else:
                        if step[position][eye][staircase] <= len(curvature)-2:
                            step[position][eye][staircase] -= 1
                            choice = 'right'
                            # print(step[position][eye][staircase])
                        if step[position][eye][staircase] ==len(curvature)-1:
                            step[position][eye][staircase] += 1
                            # print(step[position][eye][staircase])
                            choice= 'NA'
                    trial_clock.reset()
                elif k[0] in ['space']:
                    choice = 'Trial aborted'
                    trial_clock.reset()
            else: ## add -4 +4
                if k[0] in ['q']:
                    abort = True
                    break
                elif k[0] in ['right']:
                    if currentcurv == .4:
                        pass
                    else:
                        if step[position][eye][staircase] <= len(curvature)-2:
                            step[position][eye][staircase] += 1
                            choice = 'right'
                            # print(step[position][eye][staircase])
                        if step[position][eye][staircase] ==len(curvature)-1:
                            step[position][eye][staircase] -= 1
                            # print(step[position][eye][staircase])
                            choice= 'NA'
                    trial_clock.reset()
                elif k[0] in ['left']:
                    if currentcurv == -.4:
                        pass
                    else:
                        if step[position][eye][staircase] <= len(curvature)-2:
                            step[position][eye][staircase] -= 1
                            # print(step[position][eye][staircase])
                            choice = 'left'
                        if step[position][eye][staircase] ==len(curvature)-1:
                            step[position][eye][staircase] += 1
                            # print(step[position][eye][staircase])
                            choice= 'NA'
                    trial_clock.reset()
                elif k[0] in ['space']:
                    choice = 'Trial aborted'
            ##Adapting the staircase
            resps[position][eye][staircase]  = resps[position][eye][staircase]  + [choice]
        #sets the bounds for the staircase
        ## Reversals
            if resps[position][eye][staircase][-2:] == ['left', 'right'] or resps[position][eye][staircase][-2:] == ['right', 'left']: 
                revs[position][eye][staircase]  = revs[position][eye][staircase]  + 1
        if abort:
                break
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
    if abort:
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write("Run manually ended at " + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + "!")
        respFile.close()
        bye = visual.TextStim(win, text="Run manually ended \n Press space bar to exit")
    elif not any(stairs_ongoing):
        print('run ended properly!')
        bye = visual.TextStim(win, text="You have now completed the experimental run. Thank you for your participation!! \n Press space bar to exit")

    blindspot.autoDraw = False
    ## Farewells
    bye.draw()
    win.flip()
    event.waitKeys()

