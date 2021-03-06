'''
Created on Feb 1, 2015

@author: ryan
'''
import numpy as np

import abc

from python.ee.rf.network.elements.SElement import SElement 
   
class S2Port(SElement):
    """
    This class denotes an s-parameters element. It must have GetA(), GetB(),
    GetC() and GetD() implemented or an exception will be raised. ABCD 
    corresponds to the ABCD matrix of a given two port element.
    """ 
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, node1, node2, s11=None, s12=None, s21=None, s22=None, 
                 z0 = 50.0, zs = 50.0, zl = 50.0):
        
        super(S2Port, self).__init__(node1,node2,z0)
        
        self.SetS11(s11)
        self.SetS12(s12)
        self.SetS21(s21)
        self.SetS22(s22)
        
        self.SetZs(zs)
        self.SetZl(zl)

    def SetZs(self, zs):
        self.zs = zs
        self.SetGammaS(SElement.CalcGamma(zs, self.z0))
    
    def SetZl(self, zl):
        self.zl = zl
        self.SetGammaL(SElement.CalcGamma(zl, self.z0))
    
    def GetInputVSWR(self):
        return (1.0+np.abs(self.GetS11Prime()))/(1.0 - np.abs(self.GetS11Prime()))
    
    def GetOutputVSWR(self):
        return (1.0+np.abs(self.GetS22Prime()))/(1.0 - np.abs(self.GetS22Prime()))
    
    def SetGammaS(self, gammaS):
        self.gammaS = gammaS
    
    def SetGammaL(self, gammaL):
        self.gammaL = gammaL
        
    
    def GetS11Prime(self):
        s11, s12, s21, s22 = self.GetSTuple()
        rl = self.gammaL
        return s11 + s12*s21*rl / (1.0-rl*s22)
    
    def GetS22Prime(self):
        s11, s12, s21, s22 = self.GetSTuple()
        rs = self.gammaS
        return s22 + s12*s21*rs/(1.0-rs*s11)
    
    def GetS21Prime(self):
        s11, s12, s21, s22 = self.GetSTuple()
        rl = self.gammaL
        rs = self.gammaS
        numerator = s21*np.sqrt(1.0-np.abs(rs)**2) * np.sqrt(1.0-np.abs(rl)**2)
        denominator = (1.0-s11*rs)*(1.0-s22*rl)-s21*s12*rl*rs
        return numerator/denominator
    
    def GetS12Prime(self):
        s11, s12, s21, s22 = self.GetSTuple()
        rl = self.gammaL
        rs = self.gammaS
        numerator = s12*np.sqrt(1.0-np.abs(rs)**2) * np.sqrt(1.0-np.abs(rl)**2)
        denominator = (1.0-s11*rs)*(1.0-s22*rl)-s21*s12*rl*rs
        return numerator/denominator
    
    def GetInsertionLossPrime(self):
        return 20 * np.log10(np.abs(self.GetS21Prime()))
    
    def GetReturnLossPrime(self):
        return 20 * np.log10(np.abs(self.GetS11Prime()))
    
    def SetS11(self, s11):
        self.s11 = s11
    
    def SetS22(self, s22):
        self.s22 = s22
    
    def SetS12(self, s12):
        self.s12 = s12
    
    def SetS21(self, s21):
        self.s21 = s21
    
    @staticmethod
    def __CalcS11__(z0, A,B,C,D):
        numerator = A + B/z0 - C*z0 - D
        denominator = A + B/z0 + C*z0 + D
        return numerator/denominator
    
    @staticmethod
    def __CalcS21__(z0, A,B,C,D):
        numerator = 2.0
        denominator = A + B/z0 + C * z0 + D
        return numerator/denominator
    @staticmethod
    def __CalcS12__(z0, A,B,C,D):
        numerator = 2.0* (A *D - B*C)
        denominator = A + B/z0 + C*z0 + D
        return numerator / denominator
    
    @staticmethod
    def __CalcS22__(z0, A,B,C,D):
        numerator = -A + B/z0 - C*z0 + D
        denominator = A + B/z0 + C * z0 + D
        return numerator/denominator
    
    ############################################################################
    
    def CalcDelta(self):
        s11 = self.GetS11Prime()
        s12 = self.GetS12Prime()
        s21 = self.GetS21Prime()
        s22 = self.GetS22Prime()
        return s11*s22 - s12 * s21

        
    def CalcK(self):
        s11 = self.GetS11Prime()
        s12 = self.GetS12Prime()
        s21 = self.GetS21Prime()
        s22 = self.GetS22Prime()
        delta = self.CalcDelta()
        numerator = 1.0-np.abs(s11)**2-np.abs(s22)**2+np.abs(delta)**2
        denominator = 2.0 * np.abs(s12*s21)
        return numerator/denominator
    
    def CalcMu(self):
        s11 = self.GetS11Prime()
        s12 = self.GetS12Prime()
        s21 = self.GetS21Prime()
        s22 = self.GetS22Prime()
        delta = self.CalcDelta()
        numerator = 1.0 - np.abs(s11)**2
        denominator = np.abs(s22-delta*np.conj(s11)) + np.abs(s12*s21)
        return numerator / denominator
        
    
    def IsStable(self):
        return np.abs(self.GetS11Prime()) < 1 \
                and np.abs(self.GetS22Prime()) < 1 \
                and self.CalcK() > 1
    
    def IsStableMu(self):
        return self.CalcMu() > 1.0
    
    def CalcCl(self):
        s11 = self.GetS11Prime()
        s12 = self.GetS12Prime()
        s21 = self.GetS21Prime()
        s22 = self.GetS22Prime()
        delta = self.CalcDelta()
        numerator = np.conj(s22-delta*np.conj(s11))
        denominator = np.abs(s22)**2 - np.abs(delta)**2
        return numerator/denominator
    
    def CalcRl(self):
        s11 = self.GetS11Prime()
        s12 = self.GetS12Prime()
        s21 = self.GetS21Prime()
        s22 = self.GetS22Prime()
        delta = self.CalcDelta()
        numerator = s12*s21
        denominator = np.abs(s22)**2 - np.abs(delta)**2
        return np.abs(numerator/denominator)
    
    def CalcCs(self):
        s11 = self.GetS11Prime()
        s12 = self.GetS12Prime()
        s21 = self.GetS21Prime()
        s22 = self.GetS22Prime()
        delta = self.CalcDelta()
        numerator = np.conj(s11-delta*np.conj(s22))
        denominator = np.abs(s11)**2 - np.abs(delta)**2
        return numerator/denominator
    
    def CalcRs(self):
        s11 = self.GetS11Prime()
        s12 = self.GetS12Prime()
        s21 = self.GetS21Prime()
        s22 = self.GetS22Prime()
        delta = self.CalcDelta()
        numerator = s12*s21
        denominator = np.abs(s11)**2 - np.abs(delta)**2
        return np.abs(numerator/denominator)
    ############################################################################
    def GetS11(self):
        if self.s11 is None:
            self.s11 = self.__CalcS11__(self.z0, self.GetA(), self.GetB(), self.GetC(), self.GetD())
        return self.s11
    
    def GetS12(self): 
        if self.s12 is None:
            self.s12 = self.__CalcS12__(self.z0, self.GetA(), self.GetB(), self.GetC(), self.GetD())
        return self.s12
    
    def GetS21(self):
        if self.s21 is None:
            self.s21 = self.__CalcS21__(self.z0, self.GetA(), self.GetB(), self.GetC(), self.GetD())
        return self.s21
    
    def GetS22(self):
        if self.s22 is None:
            self.s22 = self.__CalcS22__(self.z0, self.GetA(), self.GetB(), self.GetC(), self.GetD())
        return self.s22
    
    def GetSTuple(self):
        return self.GetS11(), self.GetS12(), self.GetS21(), self.GetS22()
    
    def GetSMatrix(self):
        s11 = self.GetS11()
        s12 = self.GetS12()
        s21 = self.GetS21()
        s22 = self.GetS22()
        row1 = [s11, s12]
        row2 = [s21, s22]
        matrix = [row1,row2]
        return np.matrix(matrix)
    
    def GetSPrimeMatrix(self):
        s11 = self.GetS11Prime()
        s12 = self.GetS12Prime()
        s21 = self.GetS21Prime()
        s22 = self.GetS22Prime()
        row1 = [s11, s12]
        row2 = [s21, s22]
        matrix = [row1,row2]
        return np.matrix(matrix)
    
    def GetReturnLoss(self):
        return 20 * np.log10(np.abs(self.GetS11()))
    
    def GetInsertionLoss(self):
        return 20 * np.log10(np.abs(self.GetS21()))

    def GetABCDTuple(self):
        return self.GetA(), self.GetB(), self.GetC(), self.GetD()
    
    def GetABCDMatrix(self):
        """
        Returns its associated ABCD matrix.
        
        Parameters:
        -----------
        None
        
        Returns:
        --------
        ABCD : 4x4 numpy matrix
            The associated ABCD matrix.
        """
        a = self.GetA()
        b = self.GetB()
        c = self.GetC()
        d = self.GetD()
        row1 = [a,b]
        row2 = [c,d]
        matrix = [row1,row2]
        return np.matrix(matrix)
    
    
    def __mul__(self, other):
        newABCD = self.GetABCDMatrix() * other.GetABCDMatrix()
        A = newABCD.item((0,0))
        B = newABCD.item((0,1))
        C = newABCD.item((1,0))
        D = newABCD.item((1,1))
        s11 = self.__CalcS11__(self.z0, A, B, C, D)
        s12 = self.__CalcS12__(self.z0, A, B, C, D)
        s21 = self.__CalcS21__(self.z0, A, B, C, D)
        s22 = self.__CalcS22__(self.z0, A, B, C, D)
        return S2Port(node1=self.node1, node2=other.node2, z0=self.z0,zl=other.zl,zs=self.zs,s11=s11,s12=s12,s21=s21,
                      s22=s22)