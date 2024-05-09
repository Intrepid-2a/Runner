 #!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Distance comparison across blind spot
TWCF IIT vs PP experiment 2a piloting
Authors: Clement Abbatecola, Belén María Montabes de la Cruz
    Code version:
        2.2 # 2024/03/25    Various fixes (notably better file saving, eye-tracker handling and bug when first response was bad)
        2.1 # 2024/02/16    Common code for LH and RH
        2.0 # 2024/02/12    Final common version before eye tracking
"""


import psychopy
from psychopy import core, visual, gui, data, event
from psychopy.tools.coordinatetools import pol2cart, cart2pol
import numpy as np
import random, datetime, os
from glob import glob
from itertools import compress
# from fusion_stim import fusionStim

import sys, os
sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import localizeSetup, EyeTracker

######
#### Initialize experiment
######

def doDistanceTask(ID=None, hemifield=None, location=None):

    ## parameters
    nRevs   = 10   #
    nTrials = 30  # at least 10 reversals and 30 trials for each staircase (~ 30*8 staircases = 250 trials)
    # letter_height = 40 # 40 dva is pretty big?
    letter_height = 2

    ## files
    # expInfo = {'ID':'test', 'hemifield':['left','right']}
    # dlg = gui.DlgFromDict(expInfo, title='Infos', screen=0)
    # ID = expInfo['ID'].lower()
    # hemifield = expInfo['hemifield']
    expInfo = {}
    askQuestions = False
    if ID == None:
        expInfo['ID'] = ''
        askQuestions = True
    if hemifield == None:
        expInfo['hemifield'] = ['left','right']
        askQuestions = True
    # expInfo = {'ID':'test', 'hemifield':['left','right']}
    if askQuestions:
        dlg = gui.DlgFromDict(expInfo, title='Infos', screen=0)

    if ID == None:
        ID = expInfo['ID'].lower()
    if hemifield == None:
        hemifield = expInfo['hemifield']

    # need to know which eye-tracker to use:
    if location == None:
        # hacky, but true for now:
        if os.sys.platform == 'linux':
            location = 'toronto'
        else:
            location = 'glasgow'

    trackEyes = [True, True]

    # ## path
    # main_path = 'C:/Users/clementa/Nextcloud/project_blindspot/blindspot_eye_tracker/'
    # data_path = main_path + 'data/'
    main_path = '../data/distance/'
    data_path = main_path
    eyetracking_path = main_path + 'eyetracking/' + ID + '/'
    
    # this _should_ already be handled by the Runner utility: setupDataFolders()
    os.makedirs(data_path, exist_ok=True)
    # but not this one:
    os.makedirs(eyetracking_path, exist_ok=True)


    # create output file:
    x = 1
    # filename = '_dist_' + ('LH' if hemifield == 'left' else 'RH') + '_' + ID + '_'
    filename = ID + '_dist_' + ('LH' if hemifield == 'left' else 'RH') + '_'
    while (filename + str(x) + '.txt') in os.listdir(data_path):
        x += 1
    respFile = open(data_path + filename + str(x) + '.txt','w')

    respFile.write(''.join(map(str, ['Start: \t' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '\n'])))
    respFile.write('\t'.join(map(str, ['Resp',
                                    'Targ_loc',
                                    'Foil_loc',
                                    'Targ_len',
                                    'Difference',
                                    'Which_first',
                                    'Targ_chosen',
                                    'Reversal',
                                    'Foil_type',
                                    'Eye',
                                    'Gaze_out',
                                    'Stair',
                                    'Trial'])) + '\n')
    respFile.close()
    print(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
    print("Resp",
        "Targ_loc",
        "Foil_loc",
        "Targ_len",
        "Difference",
        "Which_first",
        "Targ_chosen",
        "Reversal",
        "Foil_type",
        "Eye",
        "Gaze_out",
        "Stair")


    x = 1
    et_filename = 'dist' + ('LH' if hemifield == 'left' else 'RH')
    while len(glob(eyetracking_path + et_filename + str(x) + '.*')):
        x += 1

    # get everything shared from central:
    setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename+str(x), task='distance', ID=ID) # data path is for the mapping data, not the eye-tracker data!

    print(setup['paths']) # not using yet, just testing

    # unpack all this
    win = setup['win']

    colors = setup['colors']
    col_both = colors['both']
    if hemifield == 'left':
        col_ipsi, col_contra = colors['left'], colors['right']
    if hemifield == 'right':
        col_contra, col_ipsi = colors['left'], colors['right']

    # if hemifield == 'left':
    #     col_ipsi, col_contra = colors['right'], colors['left']
    # if hemifield == 'right':
    #     col_contra, col_ipsi = colors['right'], colors['left']

    # print(colors)

    hiFusion = setup['fusion']['hi']
    loFusion = setup['fusion']['lo']

    blindspot = setup['blindspotmarkers'][hemifield]
    # print(blindspot.fillColor)
    
    fixation = setup['fixation']

    tracker = setup['tracker']
    



    ## instructions
    visual.TextStim(win,'Troughout the experiment you will fixate at a white cross that will be located at the center of the screen.   \
    It is important that you fixate on this cross at all times.\n\n You will be presented with pairs of dots. You will have to indicate which dots were closer together.\n\n Left arrow = first pair of dots were closer together.\
    \n\n Right arrow = second pair of dots were closer together.\n\n\n Press the space bar to start the experiment.', height = letter_height,wrapWidth=1200, color = 'black').draw()
    win.flip()
    k = ['wait']
    while k[0] not in ['q','space']:
        k = event.waitKeys()
    if k[0] in ['q']:
        win.close()
        core.quit()


    ######
    #### Prepare stimulation
    ######

    ## stimuli
    point_1 = visual.Circle(win, radius = .5, pos = pol2cart(00, 3), units = 'deg', fillColor = col_both, lineColor = None)
    point_2 = visual.Circle(win, radius = .5, pos = pol2cart(00, 6), units = 'deg', fillColor = col_both, lineColor = None)
    point_3 = visual.Circle(win, radius = .5, pos = pol2cart(45, 3), units = 'deg', fillColor = col_both, lineColor = None)
    point_4 = visual.Circle(win, radius = .5, pos = pol2cart(45, 6), units = 'deg', fillColor = col_both, lineColor = None)

    # blindspot = visual.Circle(win, radius = .5, pos = [7,0], units = 'deg', fillColor=col_ipsi, lineColor = None)
    # blindspot.pos = spot_cart
    # blindspot.size = spot_size
    # blindspot.autoDraw = True 

    left_prop  = setup['blindspotmarkers']['left_prop']
    right_prop = setup['blindspotmarkers']['right_prop']

    spot_left    = left_prop['spot']
    ang_up_left  = left_prop['ang_up']
    tar_left     = left_prop['tar']

    spot_right   = right_prop['spot']
    ang_up_right = right_prop['ang_up']
    tar_right    = right_prop['tar']

    ## prepare trials
    positions = {
        "left-top": [(spot_left[0]  - ang_up_left,  spot_left[1]  - tar_left/2),  (spot_left[0]  - ang_up_left,  spot_left[1]  + tar_left/2)],
        "left-mid": [(spot_left[0]  +          00,  spot_left[1]  - tar_left/2),  (spot_left[0]  +          00,  spot_left[1]  + tar_left/2)],
        "left-bot": [(spot_left[0]  + ang_up_left,  spot_left[1]  - tar_left/2),  (spot_left[0]  + ang_up_left,  spot_left[1]  + tar_left/2)],
        "righ-top": [(spot_right[0] + ang_up_right, spot_right[1] - tar_right/2), (spot_right[0] + ang_up_right, spot_right[1] + tar_right/2)],
        "righ-mid": [(spot_right[0] +           00, spot_right[1] - tar_right/2), (spot_right[0] +           00, spot_right[1] + tar_right/2)],
        "righ-bot": [(spot_right[0] - ang_up_right, spot_right[1] - tar_right/2), (spot_right[0] - ang_up_right, spot_right[1] + tar_right/2)],
    }

    if hemifield == 'left':
        # First column is target, second column is foil
        pos_array = [["left-mid", "left-top"],
                     ["left-mid", "left-bot"],
                     ["left-top", "left-bot"],
                     ["left-bot", "left-top"]]
        tar = tar_left
    else:
        pos_array = [["righ-mid", "righ-top"],
                     ["righ-mid", "righ-bot"],
                     ["righ-top", "righ-bot"],
                     ["righ-bot", "righ-top"]]
        tar = tar_right

    pos_array_bsa = pos_array[0:2]
    pos_array_out = pos_array[2:4]


    ######
    #### Prepare eye tracking
    ######

    ## setup and initialize eye-tracker + gaze ok region etc.
    #!!#

    # first calibration
    visual.TextStim(win,'Calibration...', color = col_both, units = 'deg', pos = (0,-2)).draw()
    fixation.draw()
    win.flip()
    k = event.waitKeys()
    if k[0] in ['q']:
        respFile.close()

        # send quit comment
        # stop tracking
        # close file
        # shutdown eye-tracker

        win.close()
        core.quit()
        
    #!!# calibrate
    #tracker.initialize() # this should be done in the central thing... dependent on location: in Toronto we need to override the calibrationTargets
    tracker.calibrate()
    tracker.startcollecting()
    tracker.openfile()

    fixation.draw()
    win.flip()

    k = event.waitKeys()
    if k[0] in ['q']:
        respFile.close()

        # send quit comment
        # stop tracking
        # close file
        # shutdown eye-tracker

        win.close()
        core.quit()

    #!!# start recording

    ######
    #### Staircase
    ######

    trial_clock = core.Clock()

    foil_type = [1, -1] * 4
    eye = ['left', 'left', 'right', 'right'] * 2
    pos_arrays = [pos_array_bsa[:]] * 4 + [pos_array_out[:]] * 4

    intervals = [3.5,3, 2.5, 2, 1.5, 1, .5, 0, -.5, -1, -1.5, -2, -2.5, -3, -3.5]
    position = [[]] * 8
    trial_stair = [0] * 8
    revs = [0] * 8
    direction = [1] * 8
    cur_int = [0] * 8
    reversal = False
    resps = [[True],[False]] * 4
    stairs_ongoing = [True] * 8

    trial = 1
    abort = False
    recalibrate = False

    while any(stairs_ongoing):

        increment = True

        ## choose staircase
        which_stair = random.choice(list(compress([x for x in range(len(stairs_ongoing))], stairs_ongoing)))

        ## set trial
        if position[which_stair] == []:
            random.shuffle(pos_arrays[which_stair])
            position[which_stair] = pos_arrays[which_stair][:]
        pos = position[which_stair].pop()

        shift = random.sample([-1, -.5, 0, .5, .1], 2)
        dif = intervals[cur_int[which_stair]] * foil_type[which_stair]
        which_first = random.choice(['Targ', 'Foil'])

        if which_first == 'Targ':
            point_1.pos = pol2cart(positions[pos[0]][0][0], positions[pos[0]][0][1]       + shift[0])
            point_2.pos = pol2cart(positions[pos[0]][1][0], positions[pos[0]][1][1]       + shift[0])
            point_3.pos = pol2cart(positions[pos[1]][0][0], positions[pos[1]][0][1]       + shift[1])
            point_4.pos = pol2cart(positions[pos[1]][1][0], positions[pos[1]][1][1] + dif + shift[1])
        else:
            point_3.pos = pol2cart(positions[pos[0]][0][0], positions[pos[0]][0][1]       + shift[0])
            point_4.pos = pol2cart(positions[pos[0]][1][0], positions[pos[0]][1][1]       + shift[0])
            point_1.pos = pol2cart(positions[pos[1]][0][0], positions[pos[1]][0][1]       + shift[1])
            point_2.pos = pol2cart(positions[pos[1]][1][0], positions[pos[1]][1][1] + dif + shift[1])

        if eye[which_stair] == hemifield:
            point_1.fillColor = col_ipsi
            point_2.fillColor = col_ipsi
            point_3.fillColor = col_ipsi
            point_4.fillColor = col_ipsi
        else:
            point_1.fillColor = col_contra
            point_2.fillColor = col_contra
            point_3.fillColor = col_contra
            point_4.fillColor = col_contra
        
        hiFusion.resetProperties()
        loFusion.resetProperties()

        ## pre trial fixation
        tracker.waitForFixation()
        gaze_out = False #? not sure what this variable is for but it needs to exist?

        # not sure, but the next while loop seems to be doing the same thing as "waitForFixation()"
        # 

        # trial_clock.reset()
        # gaze_out = False
        # while True and not abort:
        #     # Start detecting time
        #     t = trial_clock.getTime()
            
        #     #!!# get position at each t
        #     #!!# every 100 ms, check that positions were on average <2 dva from center
        #     #!!# after 5 consecutive intervals (500 ms) with correct fixation, break to start trial
        #     #!!# for now we break automatically:
        #     if t > .5:
        #         break
        #     #!!#

        #     hiFusion.draw()
        #     loFusion.draw()
        #     fixation.draw()
        #     win.flip()

        #     k = event.getKeys(['q'])
        #     if k:
        #         if 'q' in k:
        #             abort = True
        #             break
            
        #     # set up auto recalibrate after 5s
        #     if t > 5:
        #         recalibrate = True
        #         gaze_out = True
        #         break
        
        # should the trial start be here, or maybe when waiting for fixation?
        tracker.comment('start trial %d'%(trial))

        # in reverse order, so we can pop() them off:
        stim_comments = ['pair 2 off', 'pair 1 off', 'pair 2 on', 'pair 1 on']


        if not gaze_out:
            ## trial
            
            # blindspot.draw()
            # hiFusion.draw()
            # loFusion.draw()
            # fixation.draw()
            # win.flip()
            trial_clock.reset()
            gaze_in_region = True
        
            while trial_clock.getTime() < 1.3 and not abort:
                t = trial_clock.getTime()
                
                #!!# get position at each t
                #!!# if position is invalid or >2 dva, set gaze in region to False
                #!!# may also record gazes in file here and do stuff like showing gaze position if simulating with mouse
                
                if not tracker.gazeInFixationWindow():
                    gaze_out = True
                    break

                fixation.draw()
                blindspot.draw()
                hiFusion.draw()
                loFusion.draw()

                if .1 <= trial_clock.getTime() < .5:
                    if len(stim_comments) == 4:
                        tracker.comment(stim_comments.pop()) # pair 1 on
                    point_1.draw()
                    point_2.draw()
                elif .5 <= trial_clock.getTime() < 0.9:
                    if len(stim_comments) == 3:
                        tracker.comment(stim_comments.pop()) # pair 2 on
                    point_1.draw()
                    point_2.draw()
                    point_3.draw()
                    point_4.draw()
                elif 0.9 <= trial_clock.getTime() < 1.3:
                    if len(stim_comments) == 2:
                        tracker.comment(stim_comments.pop()) # pair 1 off
                    point_3.draw()
                    point_4.draw()
        
                blindspot.draw()
                win.flip()
                
                k = event.getKeys(['q'])
                if k and 'q' in k:
                    abort = True
                    break

            if len(stim_comments) == 1:
                tracker.comment(stim_comments.pop()) # pair 2 off

        if abort:
            break
        
        if not gaze_out: # what is this even testing? gaze_out is always False... skip!!!!
        
            ## response
            fixation.ori += 45
            fixation.color = 'black'
            hiFusion.draw()
            loFusion.draw()
            fixation.draw()
            win.flip()
            
            k = ['wait']
            while k[0] not in ['q', 'space', 'left', 'right']:
                k = event.waitKeys()
            if k[0] in ['q']:
                abort = True
                break
            elif k[0] in ['space']:
                position[which_stair] = position[which_stair] + [pos]
                increment = False
                resp = 'abort'
                targ_chosen = 'abort'
                reversal = 'abort'
            else:
                resp = 1 if k[0] == 'left' else 2
                
            fixation.ori -= 45
            
        else: # we should NEVER get here...
        
            ## dealing with auto-aborted trials
        
            # auto recalibrate if no initial fixation
            if recalibrate:
                recalibrate = False
                visual.TextStim(win,'Calibration...', color = col_both, units = 'deg', pos = (0,-2)).draw()
                fixation.draw()
                win.flip()
                k = event.waitKeys()
                if k[0] in ['q']:
                    abort = True
                    break
                    
                #!!# calibrate
                tracker.stopcollecting() # do we even have to stop/start collecting?
                tracker.calibrate()
                tracker.startcollecting()
                recalibrate = False

                
                fixation.draw()
                win.flip()
                k = event.waitKeys()
                if k[0] in ['q']:
                    abort = True
                    break
            
            # changing fixation to signify gaze out, restart with 'up' possibily of break and manual recalibration 'r' 
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
                    visual.TextStim(win,'Calibration...', color = col_both, units = 'deg', pos = (0,-2)).draw()
                    fixation.draw()
                    win.flip()
                    k = event.waitKeys()
                    if k[0] in ['q']:
                        abort = True
                        break

                    #!!# calibrate
                    tracker.stopcollecting() # do we even have to stop/start collecting?
                    tracker.calibrate()
                    tracker.startcollecting()

                    fixation.draw()
                    win.flip()
                    k = event.waitKeys()
                    if k[0] in ['q']:
                        abort = True
                        break
                
            position[which_stair] = position[which_stair] + [pos]
            increment = False
            resp = 'auto_abort'
            targ_chosen = 'auto_abort'
            reversal = 'auto_abort'
        
        if increment:
            '''
            which_first == 'Targ'          => was target first? (True/False)
            dif > 0                        => was target smaller? (True/False)
            k[0] == 'left'                 => was first chosen? (True/False)
            target first == target smaller => was first smaller? (True/False)
            first smaller == first chosen  => was smaller chosen? (True/False)
            
            (which_first == 'Targ') == (k[0] == 'left') => was target chosen?
            '''
            
            targ_chosen = (which_first == 'Targ') == (k[0] == 'left')

            ## update staircase (which direction, is there a reversal?)
            reversal = False
            resps[which_stair] = resps[which_stair] + [targ_chosen]
            if  resps[which_stair][-2] != resps[which_stair][-1]:
                reversal = True
                direction[which_stair] *= -1
                revs[which_stair] += len(resps[which_stair]) > 2
                
            ## increment/update
            cur_int[which_stair] = max(min(cur_int[which_stair] + direction[which_stair], len(intervals) - 1), 0)
            trial_stair[which_stair] = trial_stair[which_stair] + 1
            stairs_ongoing[which_stair] = revs[which_stair] <= nRevs or trial_stair[which_stair] < nTrials

        ## print trial
        print(resp,
            pos[0],
            pos[1],
            tar,
            dif,
            which_first,
            targ_chosen,
            reversal,
            foil_type[which_stair],
            eye[which_stair],
            gaze_out,
            which_stair)
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write('\t'.join(map(str, [resp,
                                        pos[0],
                                        pos[1],
                                        tar,
                                        dif,
                                        which_first,
                                        targ_chosen,
                                        reversal,
                                        foil_type[which_stair],
                                        eye[which_stair],
                                        gaze_out,
                                        which_stair,
                                        trial])) + "\n")
        respFile.close()
        trial += 1



    if abort:
        respFile = open(data_path + filename + str(x) + '.txt','a')
        respFile.write("Run manually ended at " + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + "!")
        respFile.close()
        tracker.comment('run aborted')
        # stop collecting?
        # close file?
        # shutdown eye-tracker?
    elif not any(stairs_ongoing):
        tracker.comment('run finished')
        print('run ended properly!')

    print(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
    blindspot.autoDraw = False

    #!!# stop recording

    # tracker.stopcollecting()
    # tracker.closefile()
    # tracker.shutdown()


    ## last screen
    visual.TextStim(win,'Run ended.', height = letter_height, color = 'black').draw()
    win.flip()
    k = event.waitKeys()

    #!!# close eye-tracker (eye-tracker object requires the window object - which should also be closed... but only after this last message)
    win.close()


if __name__ == "__main__":
    doDistanceTask()