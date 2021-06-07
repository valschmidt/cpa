#!/usr/bin/env python
'''
Val Schmidt
Center for Coastal and Ocean Mapping 
University of New Hampshire
Copyright 2020,2021

License: BSD - Clause 2
'''

import numpy as np
import matplotlib.pyplot as plt

class vessel(object):
    def __init__(self,length,x,y,speed,heading):
        self.length = length
        self.pos = np.array([x,y])
        self.speed = speed
        self.heading = heading
        self.V = np.array([speed * np.sin(np.deg2rad(heading)),
                           speed*np.cos(np.deg2rad(heading))])
    
    def print(self):
        print("Vessel:")
        print("   pos:\t\t\t%0.3f,%0.3f" % (self.pos[0],self.pos[1]))
        print("   speed:\t\t\t%0.3f" % self.speed)
        print("   heading:\t\t\t%0.3f" % self.heading)
        print("   V:\t\t\t%0.3f,%0.3f" % (self.V[0],self.V[1]))
        print("")
              
    
    def cpa(self,vessel):
        '''
        Calculates the Closest Point of Approach (CPA) Between Two Vessels
        
        Parameters:
        ----------
        
        vessel: A vessel object of this type.
        
        Results:
        --------
        tcpa:    Time to CPA, negative indicates CPA has past.
        Vesselcpa: Coordinates of the other vessel at CPA
        Rcpa:    Range to the other vessel at CPA
        Bcpa:    Bearing to the other vessel at CPA
        
        Notes on the calculation:
        
        The progression of ownship and the vessel 
        are parameterized in time as follows:
        
        Xos(t) = Xo + Vx * t
        Yos(t) = Yo + Vy * t
        Xv(t) = Xvo + Vxt * t
        Yv(t) = Yvo + Vyt * t
        
        The the Range between the two vessels as a function
        of time is written as follows:
        
        R = sqrt( (Xv(t) - Xos(t))^2 + (Yv(t) - Yos(t))^2)
        
        The expressions above are substituted into R.
        
        R = sqrt( ((Xvo + Vxt * t) - (Xo + Vx * t))^2 +
                  ((Yvo + Vyt * t) - (Yo + Vy * t))^2)
                  
        Rearranging...
        
        R = sqrt( ((Xvo-Xo) + (Vxt-Vx)*t)^2 + 
                  ((Yvo-Yo) + (Vyt-Vy)*t)^2)
                  
        The CPA occurs when R is a minimum, so we take the
        first derivative wrt time, and set this to 0, and then solve
        for the time at which this occurs. 
        
        dR/dt = [2 * (Vxt-Vx) * ((Xvo-Xo) + (Vxt-Vx)*t) + 2 * (Vyt-Vy) * ((Yvo-Yo) + (Vyt-Vy)*t)] / R
        
        dR/dt equals 0 where numerator is 0, so we can drop R, and the 2 common to both terms. 
        Defining the vector, D, as the position of the vessel relative to ownship:
        D = (Xvo-Xo), (Vyt-Vy)
        and defining the vector, Vr, as the velocity of the vessel relative to ownship:
        Vr = (Vxt-Vx), (Vyt-Vy)
        then the time to cpa is given by:
        tcpa = -np.dot(Vr,D) / (Vr[0]**2 + Vr[1]**2)
        
        From this the position of the vessel and own ship can be calculated
        from the equations above, as well as the range and bearing 
        at which CPA will occur. 
        
        '''
        
        # Relative velocity vector:
        Vr = vessel.V - self.V
        # Relative position vector.
        D = vessel.pos - self.pos
        #print("Vr: %0.3f,%0.3f" % (Vr[0],Vr[1]))
        #print("R: %0.3f,%0.3f" % (R[0],R[1]))

        tcpa = -np.dot(Vr,D) / (Vr[0]**2 + Vr[1]**2)
        Vesselcpa = np.array([vessel.pos[0] + vessel.V[0] * tcpa,
                        vessel.pos[1] + vessel.V[1]*tcpa])
        OScpa = np.array([self.pos[0] + self.V[0] * tcpa,
                         self.pos[0] + self.V[1] * tcpa])
        CPA = Vesselcpa-OScpa
        Rcpa = np.linalg.norm(CPA)
        #Bcpa = np.arctan2(CPA[1],CPA[0]) * 180/np.pi - 90.
        Bcpa = self.bearingfromdxdy(CPA[0],CPA[1])


        return (tcpa,Vesselcpa,OScpa,Rcpa,Bcpa)
    
    def bearingfromdxdy(self,dx,dy):
        bearing = (np.arctan2( dx, dy) * 180/np.pi + 360) % 360
        return bearing
    
    def plotcpa(self,vessel,figure=None):
        
        (tcpa,Vesselcpa,OScpa,Rcpa,Bcpa) = self.cpa(vessel)
        
        if figure is None:
            F,(ax1,ax2) = plt.subplots(1,2)
        else:
            F, (ax1,ax2)  = plt.figure(figure.number)
       
        F.set_size_inches(12,6) 
        # Plot vessel 1 velocity vector.
        ax1.quiver(self.pos[0],self.pos[1],self.V[0],self.V[1],
                  angles='uv', scale_units='xy', scale=10,color = 'k')
        # Plot vessel 2 velocty vector.
        ax1.quiver(vessel.pos[0],vessel.pos[1],vessel.V[0],vessel.V[1],
                  angles='uv', scale_units='xy', scale=10,color = 'b')
        # Plot Location of vessel 2 at CPA
        ax2.quiver(Vesselcpa[0],Vesselcpa[1],vessel.V[0],vessel.V[1],
                          angles='uv', scale_units='xy', scale=10, color = 'm')
        # Plot location of own ship (vessel 1) at CPA
        ax2.quiver(OScpa[0],OScpa[1],self.V[0],self.V[1],
                          angles='uv', scale_units='xy', scale=10, color='r')
        # Plot vector from Own Ship (Vessel 1) to Vessel 2 at CPA
        ax2.quiver(OScpa[0],OScpa[1],Vesselcpa[0]-OScpa[0],Vesselcpa[1]-OScpa[1],
                  angles='uv',scale_units='xy', scale=1,color='k',alpha=.1)
        plt.text(Vesselcpa[0],Vesselcpa[1],'CPA: Range:%0.2f\n        Bearing:%0.2f' % (Rcpa,Bcpa))
        ax1.grid(True)
        ax2.grid(True)
        return F
            
    def riskofcollision(vessel):
        '''Calculate the Risk of Collision
        
        How might we do this? 
        We can calculate the CPA to the vessel.
        Then calculate the '''

    def courses_to_collide(self,vessel,N=10,minSpeed=2.,maxSpeed=25):
        '''Calculate N speeds and headings for vessel that will ensure a collision.
        
        Parameters:
        ----------
        vessel:  Vessel object for whom speeds and headings are calculated.
        N:   Number of solutions sought.
        minSpeed:   Minimum speed considered.
        maxSpeed:   Maximum speed consdiered.
        
        '''
        D = vessel.pos - self.pos

        # Confine a to values between 2 and 25 knots.
        Dnorm = np.linalg.norm(D)
        N = 10.
        max_a = maxSpeed/Dnorm
        min_a = minSpeed/Dnorm
        a = np.arange(min_a,max_a,(max_a-min_a)/N)


        Vt = [-D * x + v1.V for x in a]
        Speeds = np.array([np.linalg.norm(x) for x in Vt])
        Headings = np.array([v1.bearingfromdxdy(x[0],x[1]) for x in Vt])
        return (Speeds, Headings)
