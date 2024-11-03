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
from psychopy.tools import monitorunittools
import numpy as np
from numpy import ndarray
import random, datetime, os
import math, time
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

def doOrientationTask(ID=None, location=None, hemifield=None):

    letter_height = 1

    # way simpler site specific handling
    expInfo = {}
    askQuestions = False
    ## files
    if ID == None:
        expInfo['ID'] = ''
        askQuestions = True

    # if hemifield == None:
    #     expInfo['hemifield'] = ['left', 'right']
    #     askQuestions = True

    if askQuestions:
        dlg = gui.DlgFromDict(expInfo, title='Infos')
    

    if ID == None:
        ID = expInfo['ID']
    # if hemifield == None:
    #     hemifield = expInfo['hemifield']

    # need to know which eye-tracker to use:
    # (could also be asked in ExpInfo)
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

    random.seed(ID+'orientation') # as close to guaranteed unique trial order as we can

    trackEyes = [True, True]

    main_path = '../data/orientation/'
    data_path = main_path
    eyetracking_path = main_path + 'eyetracking/' + ID + '/'
    
    # this _should_ already be handled by the Runner utility: setupDataFolders()
    os.makedirs(data_path, exist_ok=True)

    # but not this one:
    os.makedirs(eyetracking_path, exist_ok=True)

    # add functionality to name new eye-tracking file (make into generic function so it all works the same?):
    x = 1
    et_filename = 'oriMA'
    while len(glob(eyetracking_path + et_filename + str(x) + '.*')):
        x += 1


    setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename + str(x), task='orientation', ID=ID) 
    # setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename + str(x), task='orientation', ID=ID, noEyeTracker=True) 

    tracker = setup['tracker']

    win = setup['win']

    hiFusion = setup['fusion']['hi']
    loFusion = setup['fusion']['lo']
    
    fixation = setup['fixation']
    xfix     = setup['fixation_x']


    # colors
    colors   = setup['colors']

    col_both = colors['both']
    
    blindspot_left  = setup['blindspotmarkers']['left']
    blindspot_right = setup['blindspotmarkers']['right']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # SET UP POSITIONS FOR STIMULI


    p2d = monitorunittools.pix2deg(1, win.monitor)
    winsize = win.monitor.getSizePix()
    vertical_range = winsize[1] * p2d


    # # # # # # # #  # # # # # # # # # # # # # # # # # # #  # # # # # # # # # # # # # # # # #
    # # # # # # # #  # # # # # # # # # # # # # # # # # # #  # # # # # # # # # # # # # # # # #
    #
    #      all conditions, as combinations of these parameters:
    #
    # # # # # # # #  # # # # # # # # # # # # # # # # # # #  # # # # # # # # # # # # # # # # #
    # # # # # # # #  # # # # # # # # # # # # # # # # # # #  # # # # # # # # # # # # # # # # #

    # # at blind spot, or away from blind spot:
    # stim_location = ['bs'] * 48 + ['out'] * 48

    # # left or right hemifield:
    # hemifield      = ['left'] * 24 + ['right'] * 24 + ['left'] * 24 + ['right'] * 24

    # # orientations:
    # # - reference orientation (horizontal; 0 or vertical; 90)
    # # - orientation offsets: 15 degrees for horizontal, 45 degrees for vertical pairs
    # # - applied either to the pairs spanning the blind spot, or the adjustable pair, not spanning the blind spot
    # ref_ori        = [0,  0,  0, 90, 90, 90] * 16
    # adj_ori_offset = [0, 15,  0,  0, 45,  0] * 16
    # ref_ori_offset = [0,  0, 15,  0,  0, 45] * 16

    # # the offsets can be in either direction (probably doesn't matter)
    # offset_dir     = [1] * 12 + [-1] * 12 + [1] * 12 + [-1] * 12 + [1] * 12 + [-1] * 12 + [1] * 12 + [-1] * 12

    # # starting difference is well outside the PSE shift for most people:
    # start_diff     = [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6




    # at blind spot, or away from blind spot:
    stim_location = ['bs'] * 48

    # left or right hemifield:
    hemifield      = ['left'] * 24 + ['right'] * 24

    # orientations:
    # - reference orientation (horizontal; 0 or vertical; 90)
    # - orientation offsets: 15 degrees for horizontal, 45 degrees for vertical pairs
    # - applied either to the pairs spanning the blind spot, or the adjustable pair, not spanning the blind spot
    ref_ori        = [0,  0,  0, 90, 90, 90] * 8
    adj_ori_offset = [0, 10,  0,  0, 40,  0] * 8
    ref_ori_offset = [0,  0, 10,  0,  0, 40] * 8

    # the offsets can be in either direction (probably doesn't matter)
    offset_dir     = [1] * 12 + [-1] * 12 + [1] * 12 + [-1] * 12

    # starting difference is well outside the PSE shift for most people:
    start_diff     = [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6 + [4] * 6 + [-4] * 6




    conditions = {
                  'stim_location'  : stim_location,
                  'hemifield'      : hemifield,
                  'ref_ori'        : ref_ori,
                  'adj_ori_offset' : adj_ori_offset,
                  'ref_ori_offset' : ref_ori_offset,
                  'offset_dir'     : offset_dir,
                  'start_diff'     : start_diff
                 }

    indices = list(range(len(stim_location)))
    condition_order = []
    for repeat in range(2):
        random.shuffle(indices)
        condition_order += indices

    # store responses, with the parameters describing the condition:
    x = 1
    filename = ID + '_orientation_MA_'
    while (filename + str(x) + '.txt') in os.listdir(data_path):
        x += 1

    # create output files:
    respFile = open(data_path + filename + str(x) + '.txt','w')
    respFile.write(''.join(map(str, [ 'Start: \t' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '\n'])))
    respFile.write('\t'.join(map(str, [ 

                                        'Trial',
                                        'Condition',
                                        'Location',
                                        'Hemifield',
                                        'ReferenceDistance',
                                        'ReferenceOrientation',
                                        'AdjustableOffset',
                                        'ReferenceOffset',
                                        'OffsetDirection',
                                        'StartingDifference',
                                        'AdjustableJitter',
                                        'AdjustedDistance',
                                        'Difference', 
                                        'GazeOut'
                                        
                                        ])) + '\n')
    
    respFile.close()


    ## instructions
    instructions = visual.TextStim(win, text="Throughout the experiment you will fixate at a a cross located at the centre of the screen. It is important that you maintain fixation on this cross at all times.\n\n In every trial you will be presented with two dot pairs. They will always span a different distance. Your task is to make the distances match each other by moving your mouse up or down.\n\nMove up = increase distance.\n\nMove down = decrease distance.\n\nLeft mouse click = accept final size and continue to next trial.\n\n\nPress the space bar when you're ready to start the experiment.", color = col_both)
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

    loFusion.pos = [0, -15]

    ## stimuli
    point1 = visual.Circle(win, radius = .5, pos = pol2cart(00, 3), units = 'deg', fillColor = col_both, lineColor = None)
    point2 = visual.Circle(win, radius = .5, pos = pol2cart(00, 6), units = 'deg', fillColor = col_both, lineColor = None)
    point3 = visual.Circle(win, radius = .5, pos = pol2cart(45, 3), units = 'deg', fillColor = col_both, lineColor = None)
    point4 = visual.Circle(win, radius = .5, pos = pol2cart(45, 6), units = 'deg', fillColor = col_both, lineColor = None)

    
    all_positions = {}

    for hemifield in ['left', 'right']:

        # get the properties of the blind spot in this hemifield:
        bs_prop = setup['blindspotmarkers'][hemifield+'_prop']

        diam = max(bs_prop['size']) + 2

        # at blind spot location:
        all_positions[hemifield+'bs'] = {'coords' : bs_prop['cart'],   'diam' : diam }

        # away from blind spot location:
        one_dva_angle = cart2pol(abs(bs_prop['cart'][0]), 1)[0]
        angup = one_dva_angle * ( (bs_prop['size'][1]/2) + (diam/2) + 2) * {'left' : -1, 'right': 1}[hemifield]
        out_pos = pol2cart(bs_prop['spot'][0] + angup, bs_prop['spot'][1])

        all_positions[hemifield+'out'] = {'coords' : out_pos,          'diam' : diam }


    
    
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


    abort = False
    recalibrate = False

    #mouse element
    mouse = event.Mouse(visible=False, win=win) #invisible

    #keeping track of time 
    trial_clock = core.Clock()

    # how finegrained / sensitive is the mouse position?
    # you need to move the mouse by X dva to get a 1 dva size change in the foveal circle
    mouse_scale = 3

    while len(condition_order):
        
        # get condition index:
        cidx = condition_order.pop(0) # pop from the start, append aborted trials at the end

        # retrieve condition parameters for the condition:
        location        = conditions['stim_location'][cidx]
        hemifield       = conditions['hemifield'][cidx]
        ref_ori         = conditions['ref_ori'][cidx]
        adj_ori_offset  = conditions['adj_ori_offset'][cidx]
        ref_ori_offset  = conditions['ref_ori_offset'][cidx]
        offset_dir      = conditions['offset_dir'][cidx]
        start_diff      = conditions['start_diff'][cidx]

        # apply condition parameters:
        pos_props   = all_positions[hemifield+location]
        ref_centre  = pos_props['coords']                  # blind spot middle or away position middle
        diam        = pos_props['diam']
        rad         = diam / 2

        # reference position (across blind spot pair)
        ref_rel_pos = pol2cart(ref_ori + (ref_ori_offset * offset_dir), rad + 1.5)
        point1.pos = [ref_centre[0]+ref_rel_pos[0], ref_centre[1]+ref_rel_pos[1]]
        point2.pos = [ref_centre[0]-ref_rel_pos[0], ref_centre[1]-ref_rel_pos[1]]

        # adjustable pair position... more complicated:
        # jitter added to the adjustable pair position, to reduce local cues:
        # hem_dir = {'left':1, 'right':-1}[hemifield]

        jitter = random.choice([ -2.0, -1.0, 1.0, 2.0 ])
        adj_jitter = pol2cart(ref_ori, jitter)

        # adj_offset = pol2cart(ref_ori + (90 * (hem_dir)), rad + (3 * (ref_ori/90)))
        if ref_ori == 0:
            adj_offset = [0, rad + 1]
        if ref_ori == 90:
            if hemifield == 'left':
                adj_offset = [ 2 + (1.414 * rad), 0]
            if hemifield == 'right':
                adj_offset = [-2 - (1.414 * rad), 0]


        adj_centre = [ ref_centre[0] + (adj_offset[0]) + adj_jitter[0], 
                       ref_centre[1] + (adj_offset[1]) + adj_jitter[1]    ]
        

        # hemifield dependent stuff for this trial:
        blindspot = setup['blindspotmarkers'][hemifield]

        point1.fillColor = colors[hemifield]
        point2.fillColor = colors[hemifield]
        point3.fillColor = colors[hemifield]
        point4.fillColor = colors[hemifield]

        starting_distance = max((diam + start_diff)/2, 0.75)

        print([diam, start_diff, starting_distance*2])

        mouse_offset = starting_distance * mouse_scale
        mouse.setPos([0,(-vertical_range/2)+mouse_offset])


        #adding fusion stimuli
        hiFusion.pos = [{'left':15, 'right':-15}[hemifield], 0]
        
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
            

            while 1 and not abort:
                t = trial_clock.getTime()

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


                adj_rad = abs((mousepos[1] + (vertical_range/2))) / mouse_scale

                # reference position (across blind spot pair)
                adj_rel_pos = pol2cart(ref_ori + (adj_ori_offset * offset_dir), adj_rad)

                point3.pos = [adj_centre[0]+adj_rel_pos[0], adj_centre[1]+adj_rel_pos[1]]
                point4.pos = [adj_centre[0]-adj_rel_pos[0], adj_centre[1]-adj_rel_pos[1]]


                fixation.draw()
                hiFusion.draw()
                loFusion.draw()
                blindspot.draw()

                if ((time.time() % 1) > 0.2): 
                # if ((time.time() % 0.5) > 0.1):   # faster?
                    point1.draw()
                    point2.draw()
                    point3.draw()
                    point4.draw()

                win.flip()

                
                m = mouse.getPressed()
                if m[0] == True:

                    adj_dist = adj_rad * 2
                    finaldiff = diam - adj_dist
                    tracker.comment('final distance %0.4f'%adj_dist)
                    mouse.clickReset()
                    break

        if finaldiff == 'Trial aborted':
            # aborted trials need to be redone:
            adj_dist = 'Trial aborted'
            condition_order.append(cidx)

        if abort: # M: trial intentionally aborted? or task/experiment aborted?
            # M: I think it's the task loop that gets interrupted here... but it's completely unclear what is going on
            break
        
        if not gaze_out:  #  trial aborted because of other reasons? 
            blink = 1     #  what does this do?
            
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

                # visual.TextStim(win, '#', height = letter_height, color = col_both).draw()
                visual.TextStim(win, '#', color = col_both).draw()
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
        respFile.write('\t'.join(map(str, [ ntrial,                                 # total trials
                                            cidx,
                                            location,                               # 'bs' or 'out'
                                            hemifield,                              # left or right
                                            diam,                                   # distance between reference dot pair
                                            ref_ori,
                                            adj_ori_offset,
                                            ref_ori_offset,
                                            offset_dir,
                                            start_diff,
                                            jitter,
                                            adj_dist,
                                            finaldiff if isinstance(finaldiff, str) else '%0.4f'%(finaldiff),                    # final difference? 
                                            gaze_out])) + "\n") #block              # gaze out?
        respFile.close()


        print(' '.join(map(str, [          ntrial,                                 # total trials
                                           cidx,
                                           location,                               # 'bs' or 'out'
                                           hemifield,                              # left or right
                                           diam,                                   # distance between reference dot pair
                                           ref_ori,
                                           max(adj_ori_offset, ref_ori_offset),
                                           finaldiff if isinstance(finaldiff, str) else '%0.4f'%(finaldiff),                    # final difference? 
                                           gaze_out] )))


        # break every X trials (50?)
        ntrial += 1
        break_trial += 1

        if break_trial > 40:
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
        bye = visual.TextStim(win, text="Run manually ended")
    # elif ongoing == not_ongoing:
    elif len(condition_order) == 0:
        tracker.comment('run finished')
        print('run ended properly!')
        bye = visual.TextStim(win, text="Run completed.\n\nThank you for your participation!!") # it will exit after 4 seconds?
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





if __name__ == "__main__": #BM what's this?
    doOrientationTask()    # if you run the file as a script, the function gets defined
                           # but doesn't run
                           # however, if this is the __main__ script, this will run the task (in Glasgow)
                           # if it is not the __main__ script the task can be imported (in Toronto)