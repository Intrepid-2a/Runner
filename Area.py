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
from math import sin, cos, radians, pi 
from glob import glob
from itertools import compress

from psychopy.hardware import keyboard
from pyglet.window import key


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
    # setup = localizeSetup(location=location, trackEyes=[False, False], filefolder=None, filename=None, task='area', ID=ID, noEyeTracker=True) 
    setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename + str(x), task='area', ID=ID) 

    tracker = setup['tracker']

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

    # called rad... but it's diameter, not radius
    rad = max(bs_prop['size']) + 3 # 1.5 dva padding? (effectively 0.5... could be OK)
    
    # print('RAD = %0.4f'%(rad))


    ## Creating distributions for the experiment
    # Range of possible start sizes
    step = rad/10 # rad (height or width +3)/10
    adaptorig = [rad-step*5, rad-step*4, rad-step*3, rad-step*2, rad-step, rad+step, rad+step*2, rad+step*3, rad+step*4, rad+step*5]
    # NOTE : there is no 'no difference' e.g. rad-step, rad, rad+step, can add if preferred

    # Repeating so there's 50 trials per eye and location (5 repeats of an original size for all)
    adapt = []
    i = 1
    while i < 6: #5 repetitions  
        random.shuffle(adaptorig)
        adapt += adaptorig
        i += 1

    # # jitter added to the field to reduce local cues
    jitter = (0.005, 0.01, 0.015, 0.02,0.025, 0, -0.005, -0.01, -0.015, -0.02,-0.025)


    x = 1
    filename = ID + '_area_' + ('LH' if hemifield == 'left' else 'RH') + '_'
    while (filename + str(x) + '.txt') in os.listdir(data_path):
        x += 1

    # create output files:
    respFile = open(data_path + filename + str(x) + '.txt','w')
    respFile.write(''.join(map(str, [ 'Start: \t' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '\n'])))
    respFile.write('\t'.join(map(str, [ 'TotalTrial',
                                        'Trial',
                                        'StimulusPosition',
                                        'EyeStim',
                                        'FixationSize',
                                        'FixCirclePos',
                                        'PerCirclePos',
                                        'hiFusionPos',
                                        'loFusionPos',
                                        'FixOrigSize',
                                        'PeriOrigSize',
                                        'OriginalDiff',
                                        'FixFinalSize',
                                        'FinalDiff', 
                                        'GazeOut'])) + '\n')
    
    respFile.close()


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
    
    # foveal reference circle:
    fov_point = visual.Circle( win = win, pos = [0,0], radius=0.5, edges = 360,                lineColor = col_both, lineWidth = 15, fillColor = None, interpolate = True)
    # peripheral dashed circle:
    per_point = dashedCircle(  win = win, pos = [0,0], size=1,     ndashes = 12, dashprop=0.5, lineColor = col_both, lineWidth = 15, Hz=0, interpolate = True)


    ## Positions, colors and instructions by hemifield
    
    spot_cart = bs_prop['cart']
    spot_size = bs_prop['size']
    spot      = bs_prop['spot']

    one_dva_angle = cart2pol(abs(spot_cart[0]), 5)[0] / 5

    if hemifield == 'right':
        #angle division between BS and outside locations = polar angle of the BS x and (y + BS size), - angle of the BS location (dev from 0) + 4 (padding) + radious
        angup = one_dva_angle * ( (spot_size[1]/2) + (rad/2) + 2)
        positions = {
            "righ-top": [(spot[0] + angup, spot[1])], # BS location + angup, same radians 
            "righ-mid": [(spot[0],  spot[1])], 
        }
        hifusX = -15
    else:
        #angle division between BS and outside locations = polar angle of the BS x and (y + BS size), + angle of the BS location (dev from 0) + 4 (padding) +radious
        angup = one_dva_angle * ( (spot_size[1]/2) + (rad/2) + 2)
        positions = {
            "left-top": [(spot[0] - angup, spot[1])], # BS location + angup, same radians 
            "left-mid": [(spot[0],  spot[1])],
        }
        hifusX =  15
    
    # positions
    poss = list(positions.items())
    
    
    ## Break
    ntrial = 1
    break_trial = 1

    ######
    #### Prepare eye tracking
    ######

    ## setup and initialize eye-tracker

    tracker.openfile()
    tracker.startcollecting()
    tracker.calibrate()


    win.flip()
    fixation.draw()
    win.flip()

    k = event.waitKeys()
    if k[0] in ['q']:
        win.close()
        core.quit()

    # tracker.startcollecting()


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
    mouse = event.Mouse(visible=False, win=win) #invisible

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

    # how finegrained / sensitive is the mouse position?
    # you need to move the mouse by X dva to get a 1 dva size change in the foveal circle
    mouse_scale = 3
    
    #k = ['wait']
    #while k[0] not in ['q','space']:
    #    k = event.waitKeys()
    #if k[0] in ['q']:
    #    win.close()
    #    core.quit()

    tracker.comment('%s hemifield'%(hemifield))

    while not ongoing == not_ongoing:
        
        # position: at blind spot / away from blind spot
        #  - 0:
        #  - 1:
        # col: which eye are the stimulus presented to? (in which color are they displayed)
        #  - 0:
        #  - 1:
        
        # Point 1 locations and colors
        if ongoing[0][0] == False and ongoing [0][1] == False :  #any 
            position = 1 #BS location, defined below
            col = np.random.choice(list(compress([0, 1], ongoing[position]))) # col is 'color' in R... what does it mean here? condition?
        elif ongoing[1][0] == False and ongoing [1][1] == False:
            position = 0 #Outside BS location, defined below
            col = np.random.choice(list(compress([0, 1], ongoing[position])))
        else:
            position = np.random.choice([0, 1]) 
            col = np.random.choice(list(compress([0, 1], ongoing[position])))


        per_pos = pol2cart(poss[position][1][0][0], poss[position][1][0][1])
        per_pos = [x + random.choice(posjit) for x in per_pos]
        per_point.pos = per_pos

        per_point.size = rad
        
        # Point 2 radius 
        # foveal point radius:
        currtrial = trial[position][col]# current trial
        curradapt = adaptposs[position][col] # current staircase (i.e. adapt, adapt1, adapt2, adapt3)

        fov_size = curradapt[currtrial]
        fov_point.size = curradapt[currtrial]
        fov_point.pos  = [random.choice(posjit), random.choice(posjit)]

        mouse_offset = fov_size * mouse_scale
        mouse.setPos([0,0])

        #color of dots - which eye to stimulate
        if eye[col] == hemifield: #add col
            per_point.lineColor = col_ipsi
            fov_point.lineColor = col_ipsi

        else:
            per_point.lineColor = col_contra
            fov_point.lineColor = col_contra

        # adapting fixation size to eliminate local cues during size estimation
        fixation.size = [random.choice(np.arange(0.5, 2.25, 0.25))] * 2


        #adding fusion stimuli
        hiFusion.pos = [hifusX + random.choice(posjit), random.choice(posjit)]
        loFusion.pos = [random.choice(posjit), random.choice(posjit) - 15]
        hiFusion.resetProperties()
        loFusion.resetProperties()


        tracker.waitForFixation()
        gaze_out = False


        tracker.comment('start trial %d'%(ntrial))

        ## commencing trial 

        if not gaze_out:
            
            trial_clock.reset()

            # setting adaptive method
            mouse.clickReset()
            
            tracker.comment('peripheral size %0.4f'%per_point.size)
            tracker.comment('location %d eye %d'%(position, col))
            tracker.comment('starting size %0.4f'%fov_point.size)

            ogdiff = fov_point.size - per_point.size
            ogp2 = fov_point.size

            while 1 and not abort:
                t = trial_clock.getTime()

                trial[position][col]

                if not tracker.gazeInFixationWindow():
                    gaze_out = True
                    finaldiff = 'Trial aborted'
                    tracker.comment('trial auto aborted')
                    break

                #drawing the stimuli

                k = event.getKeys(['space', 'q'])
                if k:
                    if 'q' in k:
                        abort = True # abort task
                        tracker.comment('task aborted')
                        break
                    elif 'space' in k:
                        finaldiff = 'Trial aborted' # abort trial
                        tracker.comment('trial aborted')
                        break
                
                
                # taking participant input:
                mousepos = mouse.getPos()
                fov_point.size = abs(mousepos[0] + mouse_offset) / mouse_scale
                
                per_point.ori = 15 * np.floor((t * (2/.366)) % 2)


                fixation.draw()
                hiFusion.draw()
                loFusion.draw()
                blindspot.draw()

                fov_point.draw()
                per_point.draw()

                win.flip()

                
                m = mouse.getPressed()
                if m[0] == True:
                    finaldiff = fov_point.size - per_point.size
                    tracker.comment('final size %0.4f'%fov_point.size)
                    mouse.clickReset()
                    break


        if abort: # M: trial intentionally aborted? or task/experiment aborted?
            # M: I think it's the task loop that gets interrupted here... but it's completely unclear what is going on
            break
        
        if not gaze_out: # trial aborted because of other reasons? ... why the blink parameter?
            blink = 1
            if not finaldiff == 'Trial aborted':
                trial[position][col] += 1
            else:
                pass
        else:
            blink = 0
            # auto recalibrate if no initial fixation
            # why is this not handled before the trial, so we can still do the trial?

            # this is never set to true?
            if recalibrate:
                pass
                # recalibrate = False
                # tracker.calibrate()

            else:
                hiFusion.draw()
                loFusion.draw()
                blindspot.draw() # for re-aligning the head?

                visual.TextStim(win, '#', height = letter_height, color = col_both).draw()
                print('# auto abort')
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


        #writing reponse file 
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write('\t'.join(map(str, [ntrial,                                 # total trials
                                           trial[position][col],                   # which eye was used? SHOULD be trial number?
                                                                                   # its the number of completed trials in this condition
                                           position,                               # Stimulus location [0|1]
                                           col,                                    # condition?
                                           '%0.2f'%(fixation.size[0]),                # size of fixation plus
                                           list(fov_point.pos),
                                           per_point.pos,
                                           hiFusion.pos,
                                           loFusion.pos,
                                           #round(ogp2, 3), #change
                                           '%0.4f'%(ogp2),                         # FixOrigSize (one of 10 values)
                                           # round(fov_point.size, 3),
                                           # '%0.3f'%(fov_point.size),             # PeriOrigSize (SHOULD be a constant)
                                           '%0.4f'%(rad),                          # PeriOrigSize (SHOULD be a constant)
                                           # round(ogdiff,3),
                                           '%0.4f'%(ogdiff),                       # original difference ?
                                           '%0.4f'%(fov_point.size),               # fix final size
                                           finaldiff if isinstance(finaldiff, str) else '%0.4f'%(finaldiff),                    # final difference? 
                                           gaze_out])) + "\n") #block              # gaze out?
        respFile.close()

        # check if we finished this condition:
        ongoing[position][col] =  trial[position][col] <= len(adaptposs[position][col]) -1

        print(' '.join(map(str, [          ntrial,                                 # total trials
                                           trial[position][col],                   # which eye was used? SHOULD be trial number?
                                                                                   # its the number of completed trials in this condition
                                           position,                               # Stimulus location [0|1]
                                           col,                                    # condition?
                                           #round(ogp2, 3), #change
                                           '%0.4f'%(ogp2),                         # FixOrigSize (one of 10 values)
                                           # round(fov_point.size, 3),
                                           # '%0.3f'%(fov_point.size),             # PeriOrigSize (SHOULD be a constant)
                                           '%0.4f'%(rad),                          # PeriOrigSize (SHOULD be a constant)
                                           # round(ogdiff,3),
                                           '%0.4f'%(ogdiff),                       # original difference ?
                                           '%0.4f'%(fov_point.size),               # fix final size
                                           finaldiff if isinstance(finaldiff, str) else '%0.4f'%(finaldiff),                    # final difference? 
                                           gaze_out])))


        # break every X trials (50?)
        ntrial += 1
        break_trial += 1

        if break_trial > 50:
            # do a break...

            win.flip()
            breaktext = visual.TextStim(win, 'take a break!', height = letter_height, color = col_both)
            print('- break...')
            breaktext.draw()
            win.flip()
            
            tracker.comment('break')

            on_break = True
            while on_break:
                keys = event.getKeys(keyList=['b']) # simpler solution: use a different key... like 'b'
                if 'b' in keys:
                    on_break = False
                breaktext.draw()
                win.flip()

            event.clearEvents(eventType='keyboard') # just to be sure?

            tracker.comment('continue')

            tracker.calibrate()
            break_trial = 1

        # wait until mouse button is no longer pressed:
        waiting_for_blink = True if blink else 0
        right_button_clicked = False

        while waiting_for_blink:

            m = mouse.getPressed()
            xfix.draw()
            blindspot.draw()
            win.flip()

            if m[2]:
                right_button_clicked = True

            if all([right_button_clicked, not m[2], not m[0]]):
                waiting_for_blink = False


        mouse.clickReset()
        event.clearEvents(eventType='mouse')            

        event.clearEvents(eventType='keyboard') # just to be more sure?

    ## Closing prints
    if abort:
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write("Run manually ended at " + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + "!")
        respFile.close()
        tracker.comment('run aborted')
        bye = visual.TextStim(win, text="Run manually ended \n Press space bar to exit")
    elif ongoing == not_ongoing:
        tracker.comment('run finished')
        print('run ended properly!')
        bye = visual.TextStim(win, text="You have now completed the experimental run. Thank you for your participation!! \n Press space bar to exit") # it will exit after 4 seconds?
    else:
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write("something weird happened")
        respFile.close()
        tracker.comments('unknown abort')
        print('something weird happened')

    print(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))

    ## Farewells
    bye.draw()
    win.flip()
    core.wait(4)
    
    tracker.shutdown()
    win.close()
    # core.quit()





# object that implements a rotating circle with dashed outline
# (limited ompatibility with psychopy visual stimulus objects)

# we need to keep time, in order to rotate the dashes:
from time import time

class dashedCircle():

    def __init__(   self,
                    win,
                    pos         = [0,0],
                    size        = 1,         # only circles for now, no ellipses 
                    ndashes     = 12,
                    dashprop    = 0.5,
                    Hz          = 0.1,       # rotations/second (0 = no rotation, sign = direction)
                    lineWidth   = 1,
                    lineColor   = [-1,-1,-1],
                    ori         = 0,
                    interpolate = True):

        self.win         = win
        self.pos         = pos
        self.size        = size
        self.ndashes     = int(ndashes)
        self.dashprop    = dashprop
        self.Hz          = Hz
        self.lineWidth   = lineWidth
        self.lineColor   = lineColor
        self.ori         = ori
        self.interpolate = interpolate

        self.starttime = time()
        self.createDashes()
        
    def createDashes(self):

        # to detect changes:
        self.currentProperties = {'ndashes'  : self.ndashes,
                                  'dashprop' : self.dashprop}

        self.dashes = []
        dashlength = (((360 / self.ndashes) * self.dashprop) / 180) * np.pi
        dashedges = int( max(2, np.round(720 / self.ndashes)) )
        for dash in range(self.ndashes):
            SA = (((360 / self.ndashes) * dash) / 180) * np.pi  # start angle in radians
            EA = SA + dashlength
            edge_angles = np.linspace(SA,EA,num=dashedges+1)
            vertices = []
            for v in range(dashedges+1):
                vertices.append([np.cos(edge_angles[v]), np.sin(edge_angles[v])])
            vertices = np.array(vertices)
            self.dashes.append(visual.ShapeStim( win         = self.win, 
                                                 size        = self.size/2,
                                                 lineWidth   = self.lineWidth,
                                                 lineColor   = self.lineColor,
                                                 vertices    = vertices,
                                                 closeShape  = False,
                                                 ori         = self.ori,
                                                 pos         = self.pos,
                                                 interpolate = self.interpolate))
    

    def draw(self):

        # if the ndashes or dashprop properties got changed, we need to recreate the shapestim objects:
        recreateDashes = False
        if self.ndashes  != self.currentProperties['ndashes']:  recreateDashes = True; self.currentProperties['ndashes']  = self.ndashes
        if self.dashprop != self.currentProperties['dashprop']: recreateDashes = True; self.currentProperties['dahsprop'] = self.dashprop
        if recreateDashes: self.createDashes()

        # make sure all other settings are properly used as well:
        for dash_no in range(len(self.dashes)):
            self.dashes[dash_no].ori         = self.ori
            self.dashes[dash_no].lineColor   = self.lineColor
            self.dashes[dash_no].lineWidth   = self.lineWidth
            self.dashes[dash_no].size        = self.size/2
            self.dashes[dash_no].pos         = self.pos
            self.dashes[dash_no].interpolate = self.interpolate

        # update orientation depending on elapsed time:
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