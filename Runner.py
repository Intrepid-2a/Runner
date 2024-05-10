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

        self.SetSize(600, 400) ## too big?

        ### --- MAKE GUI ELEMENTS --- ###

        # participant elements:
        self.text_participant = wx.StaticText(self, -1, "Participant ID:")
        self.refresh_icon = wx.Bitmap('rotate.png') 
        self.refresh_button = wx.Button(self, wx.ID_ANY, "refresh")
        self.refresh_button.SetBitmap(self.refresh_icon) 
        self.text_existing = wx.StaticText(self, -1, "Existing:")
        self.pick_existing = wx.ComboBox(self, id=wx.ID_ANY, choices=[], style=wx.CB_READONLY)
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

        self.Bind(wx.EVT_BUTTON, self.makeDataFolders, self.folder_button)
        self.Bind(wx.EVT_BUTTON, self.cloneGitHub, self.clone_button)
        self.Bind(wx.EVT_BUTTON, self.pullGitHub, self.pull_button)

        self.Bind(wx.EVT_COMBOBOX, self.pickExisting, self.pick_existing)

        # UPLOAD functionality needs to be figured out still...




    def __set_properties(self):
        self.SetTitle("Intrepid-2a Experiment Runner")

        # update list of choices for existing participants
        self.refresh()

        # count participants who already did the experiment

    def __do_layout(self):

        # there will be 3 main sections, that each get a grid sizer:
        # - participant ID section
        # - task run setcion (with N counters)
        # - GitHub & OSF synchronization sections
        # these will be placed into the main grid afterwards

        main_grid        = wx.GridSizer(3, 1, 0, 0)
        participant_grid = wx.GridSizer(2, 3, 0, 0)
        taskrun_grid     = wx.GridSizer(3, 6, 0, 0)
        synch_grid       = wx.GridSizer(2, 4, 0, 0)  # too much?

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

    def refresh(self):
        # self.pick_existing.choices = findParticipantIDs()
        
        self.pick_existing.Clear()
        self.pick_existing.AppendItems(findParticipantIDs())

    def pickExisting(self, event):
        self.participantID.SetValue(self.pick_existing.GetValue())

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

