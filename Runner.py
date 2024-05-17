#!/usr/bin/env python3

# GUI elements, and interaction with OS
import wx, wx.adv, os

# functions for Runner
from utilities import *

from calibration import *
from Distance import *


class MyFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.SetSize(600, 480) ## too big?

        ### --- MAKE GUI ELEMENTS --- ###
        self.existingParticipants = findParticipantIDs()


        if os.sys.platform == 'linux':
            temp_location = 'Toronto'
        else:
            temp_location = 'Glasgow'
		  
        self.location_radiobox = wx.RadioBox(self, label = 'location:', pos = (80,10), choices = ['Glasgow', 'Toronto'], majorDimension = 1, style = wx.RA_SPECIFY_ROWS) 
        self.location_radiobox.SetStringSelection(temp_location)

        # participant elements:
        self.text_participant = wx.StaticText(self, -1, "Participant ID:")
        self.refresh_icon = wx.Bitmap('rotate.png') 
        self.refresh_button = wx.Button(self, wx.ID_ANY, "refresh")
        self.refresh_button.SetBitmap(self.refresh_icon) 
        self.text_existing = wx.StaticText(self, -1, "Existing:")
        self.pick_existing = wx.ComboBox(self, id=wx.ID_ANY, choices=self.existingParticipants, style=wx.CB_READONLY)
        self.random_generate = wx.Button(self, wx.ID_ANY, "generate random")
        self.participantID = wx.TextCtrl(self, wx.ID_ANY, "")


        # task elements:
        self.area_count = wx.StaticText(self, -1, "#")
        self.area_text = wx.StaticText(self, -1, "AREA:")
        self.area_color = wx.Button(self, -1, "color")
        self.area_mapping = wx.Button(self, -1, "mapping")
        self.area_left = wx.Button(self, -1, "left")
        self.area_right = wx.Button(self, -1, "right")

        self.curve_count = wx.StaticText(self, -1, "#")
        self.curve_text = wx.StaticText(self, -1, "CURVATURE:")
        self.curve_color = wx.Button(self, -1, "color")
        self.curve_mapping = wx.Button(self, -1, "mapping")
        self.curve_left = wx.Button(self, -1, "left")
        self.curve_right = wx.Button(self, -1, "right")

        self.dist_count = wx.StaticText(self, -1, "#")
        self.dist_text = wx.StaticText(self, -1, "DISTANCE:")
        self.dist_color = wx.Button(self, -1, "color")
        self.dist_mapping = wx.Button(self, -1, "mapping")
        self.dist_left = wx.Button(self, -1, "left")
        self.dist_right = wx.Button(self, -1, "right")

        # synchronization elements:
        self.folder_check = wx.CheckBox(self, -1, "folders")
        self.folder_button = wx.Button(self, -1, "make")

        self.clone_check = wx.CheckBox(self, -1, "GitHub")
        self.clone_button = wx.Button(self, -1, "clone")

        self.pull_check = wx.CheckBox(self, -1, "GitHub")
        self.pull_button = wx.Button(self, -1, "pull")

        self.upload_check = wx.CheckBox(self, -1, "to OSF")
        self.upload_button = wx.Button(self, -1, "upload")

        self.__set_properties()
        self.__do_layout()

        ### --- BIND BUTTONS TO FUNCTIONS --- ###
        
        # location functionality:
        self.location_radiobox.Bind(wx.EVT_RADIOBOX,self.selectLocation)

        # participant ID functionality:
        self.Bind(wx.EVT_BUTTON, self.refresh, self.refresh_button)
        self.Bind(wx.EVT_COMBOBOX, self.pickExisting, self.pick_existing)
        self.Bind(wx.EVT_BUTTON, self.generateRandomID, self.random_generate)

        # task button functionality:
        self.Bind(wx.EVT_BUTTON, self.runTask, self.dist_color)
        self.Bind(wx.EVT_BUTTON, self.runTask, self.dist_mapping)
        self.Bind(wx.EVT_BUTTON, self.runTask, self.dist_left)
        self.Bind(wx.EVT_BUTTON, self.runTask, self.dist_right)
        
        # self.Bind(wx.EVT_BUTTON, self.runTask, task='area', subtask='color',   self.area_color)
        # self.Bind(wx.EVT_BUTTON, self.runTask, task='area', subtask='mapping', self.area_mapping)
        # self.Bind(wx.EVT_BUTTON, self.runTask, task='area', subtask='left',    self.area_left)
        # self.Bind(wx.EVT_BUTTON, self.runTask, task='area', subtask='right',   self.area_right)

        # self.Bind(wx.EVT_BUTTON, self.runTask, task='curve', subtask='color',    self.curve_color)
        # self.Bind(wx.EVT_BUTTON, self.runTask, task='curve', subtask='mapping',  self.curve_mapping)
        # self.Bind(wx.EVT_BUTTON, self.runTask, task='curve', subtask='left',     self.curve_left)
        # self.Bind(wx.EVT_BUTTON, self.runTask, task='curve', subtask='right',    self.curve_right)
        


        # more advanced stuff ?
        self.Bind(wx.EVT_BUTTON, self.makeDataFolders, self.folder_button)
        self.Bind(wx.EVT_BUTTON, self.cloneGitHub, self.clone_button)
        self.Bind(wx.EVT_BUTTON, self.pullGitHub, self.pull_button)

        # UPLOAD functionality needs to be figured out still...




    def __set_properties(self):
        self.SetTitle("Intrepid-2a Experiment Runner")
        self.disableChecks()
        self.selectLocation()
        # update list of choices for existing participants
        self.refresh()

        # count participants who already did the experiment?

    def __do_layout(self):

        # there will be 3 main sections, that each get a grid sizer:
        # - participant ID section
        # - task run setcion (with N counters)
        # - GitHub & OSF synchronization sections
        # these will be placed into the main grid afterwards

        main_grid        = wx.GridSizer(4, 1, 0, 0)
        # location thing is 1 item, no grid needed...
        participant_grid = wx.GridSizer(2, 3, 0, 0)
        taskrun_grid     = wx.GridSizer(3, 6, 0, 0)
        synch_grid       = wx.GridSizer(2, 4, 0, 0)  # too much?

        main_grid.Add(self.location_radiobox, 0, wx.ALIGN_LEFT, 0)

        # add elements to participant grid:
        participant_grid.Add(self.text_participant, 0, wx.ALIGN_LEFT, 0)
        participant_grid.Add(self.text_existing, 0, wx.ALIGN_LEFT, 0)
        participant_grid.Add(self.random_generate, 0, wx.ALIGN_LEFT, 0)
        participant_grid.Add(self.refresh_button, 0, wx.ALIGN_LEFT, 0)
        participant_grid.Add(self.pick_existing, 0, wx.ALIGN_LEFT, 0)
        participant_grid.Add(self.participantID, 0, wx.ALIGN_LEFT, 0)
        # add participant grid to main grid:
        main_grid.Add(participant_grid)

        # add elements to task-run grid:
        taskrun_grid.Add(self.area_count, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.area_text, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.area_color, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.area_mapping, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.area_left, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.area_right, -1, wx.ALIGN_LEFT, 0)

        taskrun_grid.Add(self.curve_count, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.curve_text, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.curve_color, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.curve_mapping, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.curve_left, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.curve_right, -1, wx.ALIGN_LEFT, 0)

        taskrun_grid.Add(self.dist_count, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.dist_text, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.dist_color, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.dist_mapping, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.dist_left, -1, wx.ALIGN_LEFT, 0)
        taskrun_grid.Add(self.dist_right, -1, wx.ALIGN_LEFT, 0)
        # add task-run grid to main grid:
        main_grid.Add(taskrun_grid)

        # add elements to synch grid:
        synch_grid.Add(self.folder_button, -1, wx.ALIGN_LEFT, 0)
        synch_grid.Add(self.folder_check, -1, wx.ALIGN_LEFT, 0)

        synch_grid.Add(self.clone_button, -1, wx.ALIGN_LEFT, 0)
        synch_grid.Add(self.clone_check, -1, wx.ALIGN_LEFT, 0)

        synch_grid.Add(self.pull_button, -1, wx.ALIGN_LEFT, 0)
        synch_grid.Add(self.pull_check, -1, wx.ALIGN_LEFT, 0)

        synch_grid.Add(self.upload_button, -1, wx.ALIGN_LEFT, 0)
        synch_grid.Add(self.upload_check, -1, wx.ALIGN_LEFT, 0)
        # add synch grid to main grid:
        main_grid.Add(synch_grid)



        self.SetSizer(main_grid)
        self.Layout() # frame method from wx


    def selectLocation(self, event=0):
        self.location = self.location_radiobox.GetStringSelection().lower()

    def refresh(self, event=0):
        self.existingParticipants = findParticipantIDs()
        
        self.pick_existing.Clear()
        self.pick_existing.AppendItems(self.existingParticipants)
        self.toggleParticipantTaskButtons(event)

    def pickExisting(self, event):
        self.participantID.SetValue(self.pick_existing.GetValue())
        self.toggleParticipantTaskButtons(event)


    def generateRandomID(self, event):
        newID = generateRandomParticipantID(prepend=self.location.lower()[:3]+'', nbytes=3)
        self.participantID.SetValue(newID)
        self.toggleParticipantTaskButtons(event)


    def toggleParticipantTaskButtons(self, event):

        info = getParticipantTaskInfo(self.participantID.GetValue())

        # new check 8 things, and toggle the 16 buttons:
        self.dist_color.Enable()
        self.dist_mapping.Disable()
        if info['distance']['color']:
            self.dist_mapping.Enable()
        self.dist_left.Disable()
        self.dist_right.Disable()
        if info['distance']['mapping']:
            self.dist_left.Enable()
            self.dist_right.Enable()

        self.area_color.Enable()
        self.area_mapping.Disable()
        if info['area']['color']:
            self.area_mapping.Enable()
        self.area_left.Disable()
        self.area_right.Disable()
        if info['area']['mapping']:
            self.area_left.Enable()
            self.area_right.Enable()
        
        self.curve_color.Enable()
        self.curve_mapping.Disable()
        if info['curvature']['color']:
            self.curve_mapping.Enable()
        self.curve_left.Disable()
        self.curve_right.Disable()
        if info['curvature']['mapping']:
            self.curve_left.Enable()
            self.curve_right.Enable()


    def runTask(self, event):

        if self.participantID.GetValue() == '':
            # no participant ID!
            return

        task = None
        subtask = None

        buttonId = event.Id
        if buttonId in [self.dist_color.Id, self.dist_mapping.Id, self.dist_left.Id, self.dist_right.Id]:
            task = 'distance'
        if buttonId in [self.area_color.Id, self.area_mapping.Id, self.area_left.Id, self.area_right.Id]:
            task = 'area'
        if buttonId in [self.curve_color.Id, self.curve_mapping.Id, self.curve_left.Id, self.curve_right.Id]:
            task = 'curvature'

        if buttonId in [self.dist_color.Id,   self.area_color.Id,   self.curve_color.Id]:
            subtask = 'color'
        if buttonId in [self.dist_mapping.Id, self.area_mapping.Id, self.curve_mapping.Id]:
            subtask = 'mapping'
        if buttonId in [self.dist_left.Id,    self.area_left.Id,    self.curve_left.Id]:
            subtask = 'left'
        if buttonId in [self.dist_right.Id,   self.area_right.Id,   self.curve_right.Id]:
            subtask = 'right'

        if subtask == None:
            print('no subtask')
            return
        if task == None:
            print('no task')
            return
        
        print([task, subtask])

        if subtask == 'color':
            # print('do color calibration')
            doColorCalibration(ID=self.participantID.GetValue(), task=task, location=self.location)
            return

        if subtask == 'mapping':
            # print('do blind spot mpapping')
            doBlindSpotMapping(ID=self.participantID.GetValue(), task=task, location=self.location)
            return

        if task == 'distance':
            print('do distance task')
            doDistanceTask(ID=self.participantID.GetValue(), hemifield=subtask, location=self.location)
            return


    def disableChecks(self):
        self.folder_check.SetValue(False)
        self.clone_check.SetValue(False)
        self.pull_check.SetValue(False)
        self.upload_check.SetValue(False)

    def makeDataFolders(self, event):

        if self.folder_check.GetValue():
            utilities.setupDataFolders()
        self.disableChecks()

    def cloneGitHub(self, event):

        if self.clone_check.GetValue():
            utilities.pullGitRepos(repos='all', main=True, clone=True)
        self.disableChecks()

    def pullGitHub(self, event):
        if self.pull_check.GetValue():
            utilities.pullGitRepos(repos='all', main=True, clone=False)
        self.disableChecks()






class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()

