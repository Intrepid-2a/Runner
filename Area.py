"""
Motion curvature estimation across blind spot
TWCF IIT vs PP experiment 2a piloting
Authors: Belén María Montabes de la Cruz, Clement Abbatecola, in collaboration with Marius t'Hart
    Code Version:
        2.0 # 2024/04/09    Final common version before eye tracking
        3.0 # 2024/03/07    Common version with Eye tracking version
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


######
#### Initialize experiment
######

def doAreaTask(ID=None, hemifield=None, location=None):

    ## parameters... these are staircase parameters, but this task does not do any staircases?
    
    nRevs   = 10   
    nTrials = 30  # at least 10 reversals and 30 trials for each staircase (30*8 staircases = 240 trials minimum)
    letter_height = 1

    # way simpler site specific handling
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

    # not site specific should be:
    # filenames, blind spot markers, colors, fusion stimuli etc etc
    # and these are already handled in localizeSetup
    # so removing a lot of redundant code here, and possibilities for making confusing new errors
    # by not updating one, while updating the other implementation of the exact same things

    # keeping what needs to be done for this task only:

    random.seed(ID+'area'+hemifield) # as close to guaranteed unique trial order as we can

    trackEyes = [True, True]

    main_path = '../data/area/'
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


    # setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename+str(x), task='area', ID=ID) # data path is for the mapping data, not the eye-tracker data!
    setup = localizeSetup(location=location, trackEyes=[False, False], filefolder=None, filename=None, task='area', ID=ID, noEyeTracker=True) 


    win = setup['win']

    hiFusion = setup['fusion']['hi']
    loFusion = setup['fusion']['lo']

    blindspot = setup['blindspotmarkers'][hemifield]
    
    fixation = setup['fixation']
    xfix     = setup['fixation_x']


    # colors
    colors   = setup['colors']
    col_both = colors['both']
    if hemifield == 'left':
        col_ipsi, col_contra = colors['left'], colors['right']
    if hemifield == 'right':
        col_contra, col_ipsi = colors['left'], colors['right']

    blindspot = setup['blindspotmarkers'][hemifield]
    bs_prop = setup['blindspotmarkers'][hemifield+'_prop']

    rad = max(bs_prop['size']) + 3 # 1.5 dva padding? (effectively 0.5... could be OK)



    ## Creating distributions for the experiment
    # Range of possible start sizes
    step = rad/10 # rad (height or width +3)/10
    adaptorig = [rad-step*5, rad-step*4, rad-step*3, rad-step*2, rad-step, rad+step, rad+step*2, rad+step*3, rad+step*4, rad+step*5]
    # NOTE : there is no 'no difference' e.g. rad-step, rad, rad+step, can add if preferred

    # Repeating so there's 50 trials per eye and location (5 repeats of an original size for all)
    # random.seed(1)
    # random.shuffle(adaptorig) #shuffeling with seed
    adapt = []
    i = 1
    while i < 6: #5 repetitions  
        # random.seed (i)
        random.shuffle(adaptorig)
        adapt += adaptorig
        i += 1

    # print(adapt)



    # # jitter added to the field to reduce local cues
    # marius: this is jitter added to the "field" property in the fusion stimuli... which... doesn't exist?
    # not sure why it's not just added to the pos property of the fusion stimuli objects? or needed
    jitter = (0.005, 0.01, 0.015, 0.02,0.025, 0, -0.005, -0.01, -0.015, -0.02,-0.025)



    ## BS stimuli
    # blindspot = visual.Circle(win, radius = .5, pos = [7,0], units = 'deg', fillColor=col_ipsi, lineColor = None)
    # blindspot.pos = spot_cart
    # blindspot.size = spot_size

    ## eyetracking   
    # colors = {'both'   : col_both, 
    #           'back'   : col_back} 
    # tracker = EyeTracker(tracker           = 'eyelink',
    #                      trackEyes         = [True, True],
    #                      fixationWindow    = 2.0,
    #                      minFixDur         = 0.2,
    #                      fixTimeout        = 3.0,
    #                      psychopyWindow    = win,
    #                      filefolder        = eyetracking_path,
    #                      filename          = et_filename+str(y),
    #                      samplemode        = 'average',
    #                      calibrationpoints = 5,
    #                      colors            = colors)

    # elif location == 'toronto':
    
    #     # not sure what you want to do here, maybe check if parameters are defined, otherwise throw an error? Or keep the gui in that case?
        
        
    #     expInfo = {}
    #     askQuestions = False
    #     if ID == None:
    #         expInfo['ID'] = ''
    #         askQuestions = True
    #     if hem == None:
    #         expInfo['hemifield'] = ['left','right']
    #         askQuestions = True
    #     if askQuestions:
    #         dlg = gui.DlgFromDict(expInfo, title='Infos', screen=0)

    #     if ID == None:
    #         ID = expInfo['ID'].lower()
    #     if hem == None:
    #         hem = expInfo['hemifield']
        
    #     ## paths
    #     main_path = '../data/area/'
    #     data_path = main_path
    #     eyetracking_path = main_path + 'eyetracking/' + ID + '/'
    #     x = 1
    #     filename = ID + '_dist_' + ('LH' if hem == 'left' else 'RH') + '_'
    #     while (filename + str(x) + '.txt') in os.listdir(data_path):
    #         x += 1
    #     y = 1
    #     et_filename = ID + '_dist_' + ('LH' if hem == 'left' else 'RH') + '_'
    #     while len(glob(eyetracking_path + et_filename + str(y) + '.*')):
    #         y += 1
        
    #     # this _should_ already be handled by the Runner utility: setupDataFolders()
    #     os.makedirs(data_path, exist_ok=True)
    #     os.makedirs(eyetracking_path, exist_ok=True)
        

        
    #     trackEyes = [True, True]
        
    #     # get everything shared from central:
    #     setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename+str(y), task='distance', ID=ID) # data path is for the mapping data, not the eye-tracker data!
    
    #     # unpack all this
    #     win = setup['win']
    
    #     colors = setup['colors']
    #     col_both = colors['both']
    #     if hem == 'left':
    #         col_ipsi, col_contra = colors['left'], colors['right']
    #     if hem == 'right':
    #         col_contra, col_ipsi = colors['left'], colors['right']

    #     hiFusion = setup['fusion']['hi'] #might need to change it due to size
    #     loFusion = setup['fusion']['lo']
    
    #     blindspot = setup['blindspotmarkers'][hem]
        
    #     fixation = setup['fixation']
    
    #     tracker = setup['tracker']
 
    # else:
    #     raise ValueError("Location should be 'glasgow' or 'toronto', was {}".format(location))


    x = 1
    filename = ID + '_area_' + ('LH' if hemifield == 'left' else 'RH') + '_'
    while (filename + str(x) + '.txt') in os.listdir(data_path):
        x += 1

    # create output files:
    respFile = open(data_path + filename + str(x) + '.txt','w')
    respFile.write('\t'.join(map(str, ['Trial',
                                    'StimulusPosition',
                                    'EyeStim',
                                    'FixOrigSize',
                                    'PeriOrigSize',
                                    'OriginalDiff',
                                    'FinalDiff', 
                                    'GazeOut'])) + '\n')
    respFile.write(''.join(map(str, ['Start: \t' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '\n'])))
    
    respFile.close()

    # gazeFile = open(eyetracking_path + filename + str(x) + '_gaze.txt','w')
    # gazeFile.write("Trial\tPosition\tEye\tTime\tGaze\n")
    # gazeFile.close()

    ## instructions
    instructions = visual.TextStim(win, text="Throughout the experiment you will fixate at a a cross located at the centre of the screen. It is important that you maintain fixation on this cross at all times.\n\n In every trial you will be presented with two circles, one surrounding the fixation cross and another in the periphery.The circles will always be slightly different in size. Your task is to make the size of the fixation circle match the one in the periphery by moving your mouse up or down.\n \n Move up = increase size of fixation circle.\n \n Move down = decrease size of fixation circle.\n\n Mouse click = accept final size and continue to next trial \n\n\n Press the space bar when you're ready to start the experiment.", color = col_both)
    instructions.wrapWidth = 40
    instructions.draw()
    win.flip()
    k = ['wait']
    while k[0] not in ['q','space']:
        k = event.waitKeys()
    if k[0] in ['q']:
        win.close()
        core.quit()
    
    ######
    ## Prepare stimulation
    ######

    ## stimuli
    # point1 = visual.Circle(win, pos = pol2cart(00, 3), edges = 200,  lineWidth = 20,fillColor = None, units = 'deg') # fixation  > changes
    # point2 = visual.Circle(win, pos = pol2cart(00, 6), edges = 200, lineColor = col_both, lineWidth = 15, fillColor = None, units = 'deg') # BS vs outside BS > fixed
    
    point1 = dashedCircle(win=win, size=10, ndashes=12, lineWidth=10, lineColor=col_both)
    point2 = dashedCircle(win=win, size=10, ndashes=12, lineWidth=10, lineColor=col_both)

    # blindspot.autoDraw = True 
    
    # # Rotating target stimuli
    # def Check1(Pos, color):
    #     for p in range(0,360,30)  :
    #         piece1=visual.Pie(win, size=(rad+0.6, rad+.6), start=p, end=p+15, edges=100,pos=Pos, lineWidth=0, lineColor=False,
    #             fillColor=color, interpolate=False, colorSpace='rgb', units='deg')
    #         inner_stim = visual.Circle(win, size=(rad, rad),  pos=Pos, units='deg',colorSpace='rgb', fillColor=col_back)
    #         piece1.draw() 
    #         inner_stim.draw()
        
    # def Check2(Pos, color):
    #     for p in range(0,360,30)  :
    #         piece2=visual.Pie(win, size=(rad+0.6, rad+0.6), start=p+15, end=p+30, edges=100,pos=Pos, lineWidth=0, lineColor=False,
    #             fillColor=color, interpolate=False, colorSpace='rgb', units='deg')
    #         inner_stim = visual.Circle(win, size=(rad, rad),  pos=Pos, units='deg',colorSpace='rgb', fillColor=col_back)
    #         piece2.draw()
    #         inner_stim.draw()  


    # blindspot.autoDraw = True

    ## Positions, colors and instructions by hemifield
    
    spot_cart = bs_prop['cart']
    spot_size = bs_prop['size']
    spot      = bs_prop['spot']

    if hemifield == 'right':
        #angle division between BS and outside locations = polar angle of the BS x and (y + BS size), - angle of the BS location (dev from 0) + 4 (padding) + radious
        angup = (cart2pol(spot_cart[0], spot_cart[1] + spot_size[1])[0] - spot[0]) + 2 + 2 + rad
        positions = {
            "righ-top": [(spot[0] + angup, spot[1])], # BS location + angup, same radians 
            "righ-mid": [(spot[0],  spot[1])], 
        }
    else:
        #angle division between BS and outside locations = polar angle of the BS x and (y + BS size), + angle of the BS location (dev from 0) + 4 (padding) +radious
        angup = (cart2pol(spot_cart[0], spot_cart[1] - spot_size[1])[0] - spot[0]) + 2 + 2 + rad
        positions = {
            "left-top": [(spot[0] - angup, spot[1])], # BS location + angup, same radians 
            "left-mid": [(spot[0],  spot[1])],
        }
    # positions
    poss = list(positions.items())
  
    
    ## Break
    breakk = visual.TextStim(win, text="You are now midway through the experiment.\n You can take a little break. Press space bar when you're ready to continue.", pos = [0, 5], color = col_both)
    breakk.wrapWidth = 40
    ntrial = 0 # trial counter to be used for the break
    brk = len(adapt)*2


    ######
    #### Prepare eye tracking
    ######

    ## setup and initialize eye-tracker
    tracker.initialize(calibrationScale=(0.35, 0.35))
    tracker.calibrate()
    win.flip()
    fixation.draw()
    win.flip()

    k = event.waitKeys()
    if k[0] in ['q']:
        win.close()
        core.quit()

    tracker.startcollecting()


    ######
    #### Staircase
    ######
    
    ## Experiment parameters -  4 staircases, 2xabove (RG), 2x below(RG)
    trial=[[0, 0], [0, 0]] # [above[R,G], BS[R,G]]
    fixsize = 0
    perisize = 0
    finaldiff = []
    ongoing = [[True, True], [True, True]]
    not_ongoing = [[False, False], [False, False]]
    turn=1
    eye = ['left', 'right']



    abort = False
    recalibrate = False

    #mouse element
    mouse = event.Mouse(visible=False) #invisible

    #trials for each position
    adapt1 = adapt.copy()
    adapt2 = adapt.copy()
    adapt3 = adapt.copy()

    random.shuffle(adapt1)
    random.shuffle(adapt2)
    random.shuffle(adapt3)

    adaptposs = [[adapt, adapt1], [adapt2, adapt3]] # print(adaptposs[0][0],adaptposs[0][1], adaptposs[1][0], adaptposs[1][1]) add 1more [0] to index
    #Circle stimuli position jitter
    posjit = [0 , 0.05, 0.1, 0.15, 0.25, 0.5, -0.05, -0.1, -0.15, -0.25, -0.5]

    #keeping track of time 
    trial_clock = core.Clock()
    
    #k = ['wait']
    #while k[0] not in ['q','space']:
    #    k = event.waitKeys()
    #if k[0] in ['q']:
    #    win.close()
    #    core.quit()

    while not ongoing == not_ongoing:
    
        # Point 1 locations and colors
        if ongoing[0][0] == False and ongoing [0][1] == False :  #any 
            position = 1 #BS location, defined below
            col = np.random.choice(list(compress([0, 1], ongoing[position])))
        elif ongoing[1][0] == False and ongoing [1][1] == False:
            position = 0 #Outside BS location, defined below
            col = np.random.choice(list(compress([0, 1], ongoing[position])))
        else:
            position = np.random.choice([0, 1]) 
            col = np.random.choice(list(compress([0, 1], ongoing[position])))
            # print(list(compress([0, 1], ongoing[position])))

        if position == 0:
            point1.setPos( pos = pol2cart(poss[0][1][0][0], poss[0][1][0][1]) ) # Outside BS location
        else:
            point1.setPos( pos = pol2cart(poss[1][1][0][0], poss[1][1][0][1]) ) # BS location

        point1.setSize( size = rad )
        
        # print('hello 5')
        
        # Point 2 radius 
        currtrial = trial[position][col]# current trial
        curradapt = adaptposs[position][col] # current staircase (i.e. adapt, adapt1, adapt2, adapt3)
        point2.size = [curradapt[currtrial], curradapt[currtrial]] 
        point2.pos = [0, 0]  #pol2cart(poss[0][1][0][0], -poss[0][1][0][1]) #[0, 0]
        point2.pos += [random.choice(posjit), random.choice(posjit)]
        # print('hello 6')

        #color of dots - which eye to stimulate
        # marius: the color mapping decided on each trial?
        if eye[col] == hemifield: #add col
            # point1.lineColor = col_ipsi
            # point2.lineColor = col_ipsi
            point1.setLineColor(col_ipsi)
            point2.setLineColor(col_ipsi)

        else:
            # point1.lineColor = col_cont
            # point2.lineColor = col_cont
            point1.setLineColor(col_cont)
            point2.setLineColor(col_cont)

        #adapting fixation size to eliminate local cues during size estimation
        f = random.sample(ndarray.tolist(np.arange(0.5, 2.25, 0.25)), 1)
        fixation.vertices = ((0, -f[0]), (0, f[0]), (0,0), (-f[0], 0), (f[0], 0))

        # print('hello 7')

        #adding fusion stimuli
        hiFusion.resetProperties()
        loFusion.resetProperties()
        # the fieldPos property does not exist...
        # hiFusion.fieldPos = (random.sample(jitter, 2))
        # loFusion.fieldPos = (random.sample(jitter, 2))
        # repeat_draw()

        # fixation.draw()
        # hiFusion.draw()
        # loFusion.draw()
        # # blindspot.draw()

        # win.flip()
        tracker.waitForFixation()
        gaze_out = False

        ## pre trial fixation 
        # tracker.comment('pre-fixation')
        # if not tracker.waitForFixation(fixationStimuli = [fixation, hiFusion, loFusion]):
        #     recalibrate = True
        #     gaze_out = True
        
        # print('pre fixation ok \n')

        

        ## commencing trial 

        # from now on, we could draw things and flip the window... before doesn't do anything...

        # why is there a gazefile? this is handled by the eye-tracker...

        # gazeFile = open(eyetracking_path + filename + str(x) + '_gaze.txt','a')
        if not gaze_out:
            
            stim_comments = ['og difference', 'final difference'] #BM what's this?
            #tracker.comment('start trial %d'%(trial))
            trial_clock.reset()

            # setting adaptive method
            jit1 = random.choice(posjit)
            jit2 = random.choice(posjit)
            mouse.clickReset()
            
            #og parameters... OG parameters are the original parameters?
            ogdiff = point1.size[0] - point2.size[0]
            ogp2 = point2.size[0]
            cycle = 0
            # if len(stim_comments) == 2:
            #     tracker.comment(stim_comments.pop()) 

            while 1 and not abort:
                t = trial_clock.getTime()

                trial[position][col]

                if not tracker.gazeInFixationWindow():
                    gaze_out = True
                    finaldiff = 'Trial aborted'
                    break

                #drawing the stimuli

                k = event.getKeys(['space', 'q'])
                if k:
                    if 'q' in k:
                        abort = True # abort task
                        break
                    elif 'space' in k:
                         finaldiff = 'Trial aborted' # abort trial
                         break
                
                
                
                # taking participant input:
                # wheel_dX, wheel_dY = mouse.getWheelRel() #gets x/ylocation of mouse

                mousepos = mouse.getPos()
                point2.size = abs(mousepos[0]) / 3
                
                # if turn == 1: # so only ~7 times per second? (even fewer in glasgow)
                #     Check1([point1.pos[0] + jit1, point1.pos[1] + jit2], point1.lineColor)
                # else:
                #     Check2([point1.pos[0] + jit1, point1.pos[1] + jit2], point1.lineColor)
                # point2.size +=  [wheel_dY*(step/2), wheel_dY*(step/2)] # uses y mouse location to adjust
                
                # point1.draw()
                # point2.draw()

                # repeat_draw()

                fixation.draw()
                hiFusion.draw()
                loFusion.draw()
                blindspot.draw()

                point1.draw()
                point2.draw()


                win.flip()

                
                m = mouse.getPressed()
                if m[0] == True:
                    print(m)
                    finaldiff = point1.size[0] - point2.size[0]
                    mouse.clickReset()
                    break

            if len(stim_comments) == 1:
                tracker.comment(stim_comments.pop()) # pair 2 off
            gazeFile.close()

        if abort: # trial intentionally aborted? or task/experiment aborted?
            break
        
        if not gaze_out: # trial aborted because of other reasons? ... why the blink parameter?
            blink = 1
            if not finaldiff == 'Trial aborted':
                trial[position][col] += 1
                print('this trial is ', trial[position][col])
            else:
                print('this trial was aborted')
                pass
        else:
            blink = 0
            # auto recalibrate if no initial fixation
            # why is this not handled before the trial, so we can still do it?
            if recalibrate:
                recalibrate = False
                tracker.calibrate()
                win.flip()
                fixation.draw()
                win.flip()
                k = event.waitKeys()
                if k[0] in ['q']:
                    abort = True
                    break
            else:
                hiFusion.draw()
                loFusion.draw()
                visual.TextStim(win, '#', height = letter_height, color = col_both).draw()
                win.flip()
                k = ['wait']
                while k[0] not in ['q', 'up', 'r']:
                    k = event.waitKeys()
                if k[0] in ['q']:
                    abort = True
                    break
        
                # manual recalibrate
                if k[0] in ['r']:
                    tracker.calibrate()
                    win.flip()
                    fixation.draw()
                    win.flip()
                    k = event.waitKeys()
                    if k[0] in ['q']:
                        abort = True
                        break

        while blink==1: # what is "blink"? what does that mean? do we have accurate blink detection now?

            hiFusion.draw()
            loFusion.draw()
            xfix.draw()

            win.flip()

            m = mouse.getPressed() # what is the right click for? clickReset and break trial loop? why break trial loop?
            if m[2] == True:
                print(m)
                mouse.clickReset()
                break
                
        #writing reponse file 
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write('\t'.join(map(str, [trial[position][col],                # which eye was used?
                                        position,# Stimulus location
                                        col,
                                        round(ogp2, 2), #change
                                        round(point1.size[0], 2),
                                        round(ogdiff,2),
                                        finaldiff, 
                                        gaze_out])) + "\n") #block
        respFile.close()
        #final updates
        #if not finaldiff == 'Trial aborted':
        #    trial[position][col]  = trial[position][col]  +1
        #else:
        #    pass
        # Break midway through
        ntrial +=1
        if ntrial == brk:
            fixation.draw()
            breakk.draw()
            win.flip()
            event.waitKeys(keyList = ['space'])
        ##Check if experiment can continue  
        print('running trial N=',  trial[position][col], 'of', len(adaptposs[position][col])-1, 'in position =', position, 'and color =', col)
        ongoing[position][col] =  trial[position][col] <= len(adaptposs[position][col]) -1
        
    ## Closing prints
    if abort:
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write("Run manually ended at " + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + "!")
        respFile.close()
        bye = visual.TextStim(win, text="Run manually ended \n Press space bar to exit")
    elif ongoing == not_ongoing:
        print('run ended properly!')
        bye = visual.TextStim(win, text="You have now completed the experimental run. Thank you for your participation!! \n Press space bar to exit") # it will exit after 4 seconds?
    else:
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write("something weird happened")
        respFile.close()
        print('something weird happened')

    print(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
    # blindspot.autoDraw = False

    ## Farewells
    bye.draw()
    win.flip()
    core.wait(4)
    
    tracker.shutdown()
    win.close()
    core.quit()




from time import time
class dashedCircle():

    def __init__(   self,
                    win,
                    pos       = [0,0],
                    size      = 1,         # only circles for now, no ellipses 
                    ndashes   = 12,
                    dashprop  = 0.5,
                    Hz        = 0.1,       # rotations/second (0 = no rotation, sign = direction)
                    lineWidth = 1,
                    lineColor = [-1,-1,-1],
                    ori       = 0):

        self.win       = win
        self.pos       = pos
        self.size      = size
        self.ndashes   = int(ndashes)
        self.dashprop  = dashprop
        self.Hz        = Hz
        self.lineWidth = lineWidth
        self.lineColor = lineColor
        self.ori       = ori

        self.starttime = time()
        self.createDashes()
        
    def createDashes(self):
        self.dashes = []
        dashlength = (((360 / self.ndashes) * self.dashprop) / 180) * np.pi
        dashedges = int( max(2, np.round(720 / self.ndashes)) )
        for dash in range(self.ndashes):
            SA = (((360 / self.ndashes) * dash) / 180) * np.pi  # start angle in radians
            EA = SA + dashlength
            edge_angles = np.linspace(SA,EA,num=dashedges)
            vertices = []
            for v in range(dashedges):
                vertices.append([np.cos(edge_angles[v])*self.size, np.sin(edge_angles[v])*self.size])
            vertices = np.array(vertices)
            self.dashes.append(visual.ShapeStim( win=self.win, 
                                                 lineWidth=self.lineWidth,
                                                 lineColor=self.lineColor,
                                                 vertices=vertices,
                                                 closeShape=False,
                                                 ori=self.ori,
                                                 pos=self.pos))
            
    def setPos(self, pos):
        self.pos = pos
        for dash_no in range(len(self.dashes)):
            self.dashes[dash_no].pos = pos

    def setSize(self, size):
        self.size = size
        self.createDashes()

    def setLineColor(self, lineColor):
        self.lineColor = lineColor
        for dash_no in range(len(self.dashes)):
            self.dashes[dash_no].lineColor = lineColor

    def draw(self):
        elapsed = time() - self.starttime
        add_revolutions = (elapsed * self.Hz) % 1
        dash_ori = self.ori + (add_revolutions * 360)
        for dash_no in range(len(self.dashes)):
            self.dashes[dash_no].ori = dash_ori
            self.dashes[dash_no].draw()




if __name__ == "__main__": #BM what's this?
    doAreaTask()           # if you run the file as a script, the function gets defined
                           # but doesn't run
                           # however, if this is the __main__ script, this if will run the task (in Glasgow)
                           # if it is not the __main__ script the task can be imported (in Toronto)