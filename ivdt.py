#-*- coding:utf-8 -*-

"""
    > I-VDT algorithm for eye movement events detection.
    > author: Mike Zheng
    > 08, May, 2021

    > Reference:
        Komogortsev, Oleg V. and Alex Karpov (2013). “Automated classification
        and scoring of smooth pursuit eye movements in the presence of fixations
        and saccades”. en. In: Behavior Research Methods 45.1, pp. 203–215. ISSN:
        1554-3528. DOI: 10.3758/s13428-012-0234-9.

    > Dataset: Lund2013
"""

#%% imports
import time
import numpy as np

#%% define object
class IVDT():

    def __init__(self, saccade_detection_threshold: float,
                 idt_dispersion_threshold: float,
                 idt_window_length:float,
                 minimal_saccade_amplitude: float,
                 minimal_saccade_length: float):
        """
        Set the parameters for fixation/saccade.sp detection.
        :param saccade_detection_threshold:
        :param idt_dispersion_threshold:
        :param idt_window_length:
        """
        super().__init__ ()
        # saccade detection threshold value, deg/sec (I-VT model description)
        self._saccade_detection_threshold = saccade_detection_threshold
        # Threshold value for maximal allowed dispersion of fixation, degrees
        self._idt_dispersion_threshold = idt_dispersion_threshold
        # Length of sample window for I-DT model
        self._idt_window_length = idt_window_length

        self._minimal_saccade_amplitude = minimal_saccade_amplitude

        self._minimal_saccade_length = minimal_saccade_length

    def get_idt_dispersion(self, etdata, onset_position,offset_position):
        """
         Calculate dispersion of window.
        :param onset_position:  start of window.
        :param offset_position:  end of window.
        :return:
        """
        self._etdata = etdata

        left_x = [ ]
        left_y = [ ]
        for i in range (onset_position, offset_position):
            left_x.append (float (self._etdata [ i ] [ 1 ]))
            left_y.append (float (self._etdata[ i ] [ 2 ]))

        if(len(left_x) == 0 or len(left_y) == 0):
            return 0

        max_x_l = max (left_x)
        max_y_l = max (left_y)
        min_x_l = min (left_x)
        min_y_l = min (left_y)
        dispersion = (max_x_l - min_x_l) + (max_y_l - min_y_l)

        return dispersion

    def cal_amp(self, etdata, onset_position, offset_position, idx):
        self._etdata = etdata
        tmp = []

        for i in range(onset_position, offset_position):
            tmp.append(self._etdata[i][idx])

        _max = max(tmp)
        _min = min(tmp)

        return _max - _min


    ## Classification functions
    def classify(self, data, delta_t_sec):
        """

        :return:
        """

        self._etdata = data
        self._delta_t_sec = delta_t_sec

        """
             STAGE 1 - Saccade/non saccade classification, I-VT algorithm.
        """
        #calculate_delta_t()
        x_velocity_degree = np.zeros(len(self._etdata), np.float)
        y_velocity_degree = np.zeros (len (self._etdata), np.float)

        # Calculate absolute degree velocity of our records

        for i in range(1, len(self._etdata)):
            x_velocity_degree[i] = (self._etdata[i][1] - self._etdata[i-1][1]) / self._delta_t_sec
            y_velocity_degree[i] = (self._etdata[i][2] - self._etdata[i-1][2]) / self._delta_t_sec

        # First point is a special case
        x_velocity_degree[0] = 0
        y_velocity_degree [ 0 ] = 0
        self._etdata[0][4] = 0 # mark first point as noise

        VELOCITY = []
        # Calculate VELOCITY of each point
        for i in range(0, len(self._etdata)):
            vel = np.sqrt(x_velocity_degree[i]**2 + y_velocity_degree[i]**2)
            VELOCITY.append(vel)

        # Perform a first stage classification - mark all saccade's samples
        for i in range(0, len(self._etdata)):
            if(abs(VELOCITY[i] >= self._saccade_detection_threshold) and self._etdata[i][3] != 'False'):
                self._etdata[i][4] = 2

        # And all other samples as fixations
        for i in range(0, len(self._etdata)):
            if(abs(VELOCITY[i] < self._saccade_detection_threshold) and self._etdata[i][3] != 'False'):
                self._etdata[i][4] = 1

        """
            STAGE 1 - Prelimenary filtration of saccades
        """
        # Perform a preliminary filtration - search all saccades, check their
        # amplitude and length and mark them back as nonclassified if failed.

        i = 1
        while(i < len(self._etdata)):
            # Get the first position of our classified eye movement.
            onset_position = i
            # Now we move towards the end of samples sequence until we meet sample
            # of different type or end of the samples.
            while(i < len(self._etdata) and (self._etdata[i][4] == self._etdata[onset_position][4]) ):
                i += 1
            # Now we found our offset position
            offset_position = i
            if(offset_position < len(self._etdata) and offset_position - onset_position < 2):
                offset_position += 1
            # Now we should exclude saccades with amplitudes less then 0.5 degree
            # And saccades that outside of allowed range, if necessary.
            if(self._etdata[onset_position][4] == 2):
                # print(self._etdata[onset_position][1])
                _x = self._etdata[558][2]
                _y = self._etdata[560][2]

                saccade_amplitude_x = self.cal_amp (self._etdata, onset_position, offset_position, 1)
                saccade_amplitude_y = self.cal_amp (self._etdata, onset_position, offset_position, 2)
                # saccade_amplitude_x = max (self._etdata [ onset_position :offset_position ] [ 1 ]) - \
                #                       min (self._etdata [ onset_position :offset_position ] [ 1 ])
                # saccade_amplitude_y = max (self._etdata [ onset_position :offset_position ] [ 2 ]) - \
                #                       min (self._etdata [ onset_position :offset_position ] [ 2 ])
                saccade_amplitude = np.sqrt(saccade_amplitude_x**2 + saccade_amplitude_y**2)
                saccade_length = offset_position - onset_position + 1

                if(saccade_amplitude < self._minimal_saccade_amplitude or
                        saccade_length < self._minimal_saccade_length):
                    for i in range(onset_position, offset_position):
                        self._etdata[i][4] = 1

        # Now we have to expand all non-filtered saccades to the one point from left


        """
            END OF STAGE 1
        """

        """
            STAGE 2 - Fixation/Pursuit separation
                        I-DT algorithm
        """
        # Now we ready to perform second stage classification.
        # All samples that were marked as fixation should be checked in order to determine
        # if this is really fixation or smooth pursuit. For this purpose we are using
        # I-DT classifier. It's an I-DT algorithm with one feature - we should left
        # intact samples that was classified before us.

        # Initialize I-DT window
        IDT_window_begin = 1
        IDT_window_end = int(min(IDT_window_begin + self._idt_window_length, len(self._etdata)))
        # print ("IDT_window_begin -  IDT_window_end = ", IDT_window_end - IDT_window_begin)
        # Until we reach the end of array
        while(IDT_window_begin < len(self._etdata)):
            # Calculate dispersion  for current window
            IDT_dispersion = self.get_idt_dispersion (self._etdata, IDT_window_begin, IDT_window_end)
            # Check if dispersion of current window is lesser than threshold value
            if(IDT_dispersion < self._idt_dispersion_threshold):
                # If true we begin increase the window by adding samples to it until it's
                # dispersion becames equal to threshold value.
                while((IDT_dispersion < self._idt_dispersion_threshold) and IDT_window_end < len(self._etdata)):
                    IDT_window_end = IDT_window_end + 1
                    IDT_dispersion = self.get_idt_dispersion (self._etdata, IDT_window_begin, IDT_window_end)
                # Now we successfully discover our fixation and should mark all samples as fixation.
                for i in range(IDT_window_begin, IDT_window_end):
                    if(self._etdata [ i ] [ 4 ] != 2):
                        self._etdata [ i ] [ 4 ] = 1
                # And clean the window
                IDT_window_begin = IDT_window_end + 1
                IDT_window_end = int(min(IDT_window_begin + self._idt_window_length, len(self._etdata)))
            else:
                # Otherwise (in case when dispersion of our window is larger than dispersion threshold value)
                if(self._etdata[IDT_window_begin] != 2):
                    self._etdata[IDT_window_begin] = 4  # PURSUIT_TYPE
                # Mark previous point as pursuit in case if it wasn't saccade
                if(IDT_window_begin > 1 and self._etdata[IDT_window_begin-1] != 2):
                    self._etdata [ IDT_window_begin - 1] = 4
                IDT_window_begin = IDT_window_begin + 1

        """
            END OF STAGE 2
        """

        """
            STAGE 3 - Merge of pursuit
        """
        current_position = 1
        while(current_position < len(self._etdata)):
            # Check if current sample is pursuit. If it really is pursuit we should
            # find its end and check if the next sample after end is fixation or saccade
            if(self._etdata[current_position] == 4):
                # First search for end of pursuit
                while(current_position < len(self._etdata) and self._etdata[current_position] == 4):
                    current_position = current_position + 1
                # Now we have to check what type is the next sample range
                begin_position = current_position
                while(current_position < len(self._etdata) and self._etdata[current_position] != 4 and self._etdata[current_position] != 2):
                    current_position = current_position + 1
                if(current_position < len(self._etdata) and self._etdata[current_position] == 4
                        and (current_position - begin_position) * delta_t_sec * 1000 < 100):
                    for i in range(begin_position, current_position):
                        self._etdata[i][4] = 4
            current_position += 1

        """
            END OF STAGE 3
        """

        return self._etdata

"""
    Usage on single file.
    > load dataset.
    > clare a ivdt obj and set the para.
    > get the res.
"""

"""
#%% load data.
datapath = "/Users/mike/PycharmProjects/thresholdBased/data/lund2013_npy_RA"
file = "%s/Lund2013_S1.npy" % datapath

etdata = np.load(file)
etdata = list(list(items) for items in list(etdata))

#% declare a ivdt object.
ivdt = IVDT(saccade_detection_threshold=7, # deg
            idt_dispersion_threshold=1.35,  # deg
            idt_window_length=0.1,          # 0.1s -> 100 ms
            minimal_saccade_amplitude=4,    # deg
            minimal_saccade_length=4)       # samples

SAMPLE_RATE = 500   # Sampling rate of data
delta_t_sec = 1 / SAMPLE_RATE
res_data = ivdt.classify(etdata, delta_t_sec)
"""