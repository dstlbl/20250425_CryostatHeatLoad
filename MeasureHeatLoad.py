#!/bin/env python3
#coding=ASCII

import numpy as np
import time

import venus_data_utils.venusplc as venusplc

venus = venusplc.VENUSController(read_only=False)

################  fast set coils
def change_superconductors(Igoal):
        time_start_change = time.time()
        usefastdiff = 0.1  # only use the fast search if the difference between current and goal is > this amount
        Inow=np.array([venus.read(['inj_i']),venus.read(['ext_i']),
                    venus.read(['mid_i']),venus.read(['sext_i'])])   # current currents

        done = np.zeros(4)+1                    # int array to check if search is done
        direction = np.sign(Igoal-Inow)         # di
        Idiff = np.abs(Igoal-Inow)
        done[np.where(Idiff>usefastdiff)]=0

        Iaim = np.zeros(4)
        Iaim[np.where(direction>0)]=Igoal[np.where(direction>0)]+5
        Iaim[np.where(direction<0)]=Igoal[np.where(direction<0)]-5
        Iaim[np.where(done==1)]=Igoal[np.where(done==1)]

        diffup = np.array([.03,.04,.08,.04])
        diffdown = np.array([.06,.10,.25,.10])
        Ioff = Igoal*1.0
        for i in range(len(Ioff)):
            if direction[i]>0: Ioff[i]=Ioff[i]-direction[i]*diffup[i]
            if direction[i]<0: Ioff[i]=Ioff[i]-direction[i]*diffdown[i]

        checkdone = np.zeros((4,40))+5.0

        start_time = time.time()
        venus.write({'inj_i':Iaim[0], 'ext_i':Iaim[1],
                        'mid_i':Iaim[2], 'sext_i':Iaim[3]})

        def check_done(done,Inow,Igoal,Ioff):
            if done[0]==0 and direction[0]*(Inow[0]-Ioff[0])>0:
                venus.write({'inj_i':Igoal[0]}); done[0]=1
            if done[1]==0 and direction[1]*(Inow[1]-Ioff[1])>0:
                venus.write({'ext_i':Igoal[1]}); done[1]=1
            if done[2]==0 and direction[2]*(Inow[2]-Ioff[2])>0:
                venus.write({'mid_i':Igoal[2]}); done[2]=1
            if done[3]==0 and direction[3]*(Inow[3]-Ioff[3])>0:
                venus.write({'sext_i':Igoal[3]}); done[3]=1
            return(done)

        names=['inj_i','ext_i','mid_i','sext_i']

        diffall = len(checkdone[0,:])*.04
        diffall_sext = len(checkdone[3,:])*.06
        while (np.sum(checkdone[0,:])>diffall or np.sum(checkdone[1,:])>diffall or 
                 np.sum(checkdone[2,:])>diffall or np.sum(checkdone[3,:])>diffall_sext):
            for i in range(5):
                time.sleep(0.1)
                Inow=np.array([venus.read(['inj_i']),venus.read(['ext_i']),
                    venus.read(['mid_i']),venus.read(['sext_i'])])   # current currents
                done = check_done(done,Inow,Igoal,Ioff)
                time.sleep(.27)

            if time.time()-time_start_change >300.0:
                Inow=np.array([venus.read(['inj_i']),venus.read(['ext_i']),
                    venus.read(['mid_i']),venus.read(['sext_i'])])   # current currents
                for i in range(4):
                    if np.abs(Inow[i]-Igoal[i])<0.08 and done[i]==0:   # for small change problem
                        Igoal[i]=Igoal[i]-.01*np.sign(Inow[i]-Igoal[i])
                        venus.write({names[i]:Igoal[i]})
                        time_start_change=time.time()
                    if np.abs(Inow[i]-Igoal[i])>=0.08:   # for some reason done going to 1 but not changing I goal
                        done[i]=0
                        venus.write({names[i]:Igoal[i]})
                        time_start_change=time.time()
            checkdone[:,:-1] = checkdone[:,1:]; checkdone[:,-1]=np.abs(Inow-Igoal)
##############  end fast coil set


### Power settings
with open('setnum','r') as f:
    setnum = int(f.readline())

if setnum == 0: filename = 'settings28and18.txt'
if setnum == 1: filename = 'settings28only.txt'
if setnum == 2: filename = 'settings18at28.txt'
if setnum == 3: filename = 'settings18only.txt'

with open(filename,'r') as f:
    settings = f.readlines()

with ('results','a') as output:
    for setting in settings():
        setting = setting.split()
        Iinj = float(settting[0])
        Iext = float(settting[1])
        Imid = float(settting[2])
        Isxt = float(settting[3])
        P28min = int(setting[4])
        P28max = int(setting[5])
        P28stp = int(setting[6])
        P18min = int(setting(7))
        P18max = int(setting(8))
        P18stp = int(setting(9))

        #### Set magnet
        change_superconductors(np.array([Iinj,Iext,Imid,Isxt])
    
        #### Set power
        P28vals = np.linspace(P28min,P28max,int((P28max-P28min)/(P28stp*1.))+1)
        P18vals = np.linspace(P18min,P18max,int((P18max-P18min)/(P18stp*1.))+1)
    
        for P28 in P28vals:
            for P18 in P18vals:
                toomuch = 0
                venus.write({'g28_req':P28})   # DST check if writing when off matters
                venus.write({'k18_fw':P18})   # DST check if writing when off matters

                #### DST add line to watch for settling or trouble
                read heater power
                    while not settled:
                            measure
                            if power<.1:
                               change power to low
                               toomuch = 1
                               if P18 isn't last one or P28 isn't last one:
                                   skip to next in list


                # wait for a while and watch for trouble
                # when settled:
                val18 = P18
                val28 = P28
                if len(P18vals)==1: val18 = 0
                if len(P28vals)==1: val28 = 0
                if not toomuch:
                    output.write("%.1f %5.1f %5.1f %5.1f %5.1f %6.1f %6.1f %5.3f\n"
                            %(time.time(),Iinj,Iext,Imid,Isxt,val28,val18,venus.read('four_k_heater_power'))

with open('setnum','w') as f:
    f.write(str(setnum+1))
