#!/usr/bin/env python3
import rospy
import numpy as np
from geometry_msgs.msg import Vector3

class Example(object):
    def __init__(self):
        self._areas = np.array([], np.int32)
        
        self._ranges = np.array((360), np.int32) # искомый массив дальностей (далее умножается на 1000)
        self._zeros = np.array([], np.int32) # массив содержит точки со всеми нулями (слепая зона + единичные помехи)
        self._blindZone = np.array([], np.int32) # массив содержит точки, которые оказались максимально близко к лидару (предположительно)
        self._NM_Max= np.array([], np.int32) # noize map показывает точку с максимальной дальнойтью в диапазоне +-5 от точки
        self._NM_Max_Sort= np.array([], np.int32) # noize map max sort содержит сортированный массив NP_Max по убыванию дальности
        self._NM_Max_Mid= np.array([], np.int32) # noize map max mid содержит элементы NP_Max, в котором незначитальные точки отфильтрованны
        self._oldMinMax = np.empty((0, 4), np.int32)
        self._speedMap = np.array([], np.int32) #speedMap хранит изменение скорости графика с шагом в один градус

        self._NM_Min= np.array([], np.int32) # noize map будет показывать точки с минимальной дальнойтью в диапазоне +-5 от точки


    def clear(self):
        self._areas = np.array([], np.int32)
        
        self._zeros = np.array([], np.int32)
        self._NM_Max= np.array([], np.int32)
        self._NM_Max_Sort= np.array([], np.int32)
        self._NM_Max_Mid= np.array([], np.int32)
        self._blindZone = np.array([], np.int32)
        self._oldMinMax = np.empty((0, 4), np.int32)

        self._NM_Min= np.array([], np.int32)

        self._speedMap = np.array([], np.int32)

    
    def filter(self): # применим к _ranges (нужно провести реальные тесты в лабиринте) 
            self._max = False
            for i in range(-2,self._ranges.size-1):
                if self._ranges[i] == 0 and (self._ranges[i-1] > 250 or self._ranges[i-1] == 0) and self._ranges[i+1] >= 0: # поиск зоны нулей (далёкий проезд или обрыв) скорее всего туда ехать можно
                    self._zeros = np.append(self._zeros, i) 
                elif self._ranges[i] == 0 and (0 < self._ranges[i-1] <= 250 or self._ranges[i-1] == -1): # поиск слепой зоны (именно диапазон, ндиничные помехи не учитываем)
                    self._ranges[i] = -1
                    self._blindZone = np.append(self._blindZone, i)
                
                #далее не else, а сортировка массивов _zeros и _blindZone
            """for i in range(0, self._zeros.size):
                if self._zeros[i] - self._zeros[i-1] <= 2 or abs(self._zeros[i-1] - self._zeros[i]) >= 358:
                    self._ranges[self._zeros[i]] = round((self._ranges[i-1] + self._ranges[i+1])/2)
                    self._zeros[i-1]    
                if self._ranges[i-1] < self._ranges[i] or self._max:
                    self._max = True
                    if self._ranges[i-1] > self._ranges[i]:   
                            self._areas = np.append(self._areas, i-1)
                            self._max = False """
    
    
    def findNoizeMax(self):
        noize = 0
        noizeMem = -1
        flag = False
        for i in range(0,360):
            #noize = np.sum(self._ranges[i-11:i]) 
            noize = self._ranges[i]+self._ranges[i-1]+self._ranges[i-2]+self._ranges[i-3]+self._ranges[i-4]+self._ranges[i-5]+self._ranges[i-6]+self._ranges[i-7]+self._ranges[i-8]+self._ranges[i-9]+self._ranges[i-10]
            if noize >= noizeMem or flag:
                flag = True
                if noize < noizeMem:   
                    self._NM_Max= np.append(self._NM_Max, i-6)
                    flag = False
            noizeMem = noize
        self._NM_Max= np.delete(self._NM_Max, 0)
        #print(self._NM_Max)

    def findNoizeMin(self):
        noize = 0
        noizeMem = 500000
        flag = False
        for i in range(0,360):
            noize = self._ranges[i]+self._ranges[i-1]+self._ranges[i-2]+self._ranges[i-3]+self._ranges[i-4]+self._ranges[i-5]+self._ranges[i-6]+self._ranges[i-7]+self._ranges[i-8]+self._ranges[i-9]+self._ranges[i-10]
            if noize <= noizeMem or flag:
                flag = True
                if noize > noizeMem: 
                    self._NM_Min= np.append(self._NM_Min, i-6)
                    flag = False
            noizeMem = noize
        self._NM_Min= np.delete(self._NM_Min, 0)
    
    def sortToMin(self, mass):
        self._NM_Max_Sort= np.array(mass)
        for i in range(0, mass.size):
            buf = i
            for j in range(i, mass.size):
                if self._ranges[self._NM_Max_Sort[buf]] < self._ranges[self._NM_Max_Sort[j]]:
                    buf = j
            tmp = self._NM_Max_Sort[i]
            self._NM_Max_Sort[i] = self._NM_Max_Sort[buf]
            self._NM_Max_Sort[buf] = tmp
    
    def sortToMid(self, mass):
        for i in range(0, mass.size):
            if self._ranges[mass[i]] >= np.mean(self._ranges) + (np.mean(self._ranges) * 0.5):
                self._NM_Max_Mid= np.append(self._NM_Max_Mid, mass[i])
        if self._NM_Max_Mid.size <= 4:
            self._NM_Max_Mid= np.array([], np.int32)
            for i in range(0, mass.size):
                if self._ranges[mass[i]] >= np.mean(self._ranges) + (np.mean(self._ranges) * 0.3):
                    self._NM_Max_Mid = np.append(self._NM_Max_Mid, mass[i])
        if self._NM_Max_Mid.size <= 4:
            self._NM_Max_Mid= np.array([], np.int32)
            for i in range(0, mass.size):
                if self._ranges[mass[i]] >= np.mean(self._ranges):
                    self._NM_Max_Mid= np.append(self._NM_Max_Mid, mass[i])
        if self._NM_Max_Mid.size <= 4:
            self._NM_Max_Mid= np.array([], np.int32)
            for i in range(0, mass.size):
                if self._ranges[mass[i]] >= np.mean(self._ranges) - (np.mean(self._ranges) * 0.3):
                    self._NM_Max_Mid= np.append(self._NM_Max_Mid, mass[i])            
        if self._NM_Max_Mid.size <= 4:
            self._NM_Max_Mid= np.array(mass)

    def findMinMax(self, array):
        fMin = False
        fMax = False
        tmp = 0
        for i in range (-1,array.size):
            tmp += 1 
            if (array[i-1] < array[i]) or fMax:
                fMax = True
                if array[i-1] > array[i]:
                    self._oldMinMax =  np.append(self._oldMinMax, np.array([[1, i if i >= 0 else 359+i, array[i-1], tmp]],  np.int32), axis = 0)
                    tmp = 0
                    fMax = False
                    fMin = True
                    continue
            if (array[i-1] > array[i]) or fMin:
                fMin = True
                if array[i-1] < array[i]:
                    self._oldMinMax = np.append(self._oldMinMax, np.array([[0, i if i >= 0 else 359+i, array[i-1], tmp]],  np.int32), axis = 0)
                    tmp = 0
                    fMin = False
                    fMax = True

    def speed(self): #производная изменения расстояния с делелием в 1 градус
        for i in range(0, 360):
            self._speedMap = np.append(self._speedMap, self._ranges[i]-self._ranges[i-1])


    


    
    def mainNM(self, msg):
        self.clear()
        self._ranges = np.array(msg.ranges) * 1000
        self._ranges = np.array(self._ranges, np.int32)
        self.filter() # применяется к _ranges
        self.findNoizeMax() #noizeMap
        self.findNoizeMin()
        #self.sortToMin(self._NM_Max) #сортировка по убыванию шума, итог в _NM_Max_Sort
        
        
        #self.findMinMax(self._ranges)
        #self._NM_Max= -np.sort(-self._ranges[self._NM_Max])
        
        
        
        
        #print("Ranges")
        #print(self._ranges)
        #self.filter() # применяется к _ranges
        
        #print(self._ranges)
        #print(self._zeros)
        #print(self._blindZone)
        #print(self._NM_Max)
        #print(self._ranges[self._NM_Max])
        """print("Max")
        print(self._NM_Max)
        print(self._ranges[self._NM_Max])
        print("Min")
        print(self._NM_Min)
        print(self._ranges[self._NM_Min])"""
        self.speed()
        print(self._ranges)
        print(self._speedMap)
        
        #print(self._NM_MaxSort)
        #print(self._ranges[self._NM_MaxSort])
        #print(self._ranges[self._NM_MaxSort])
        
        #print(self._oldMinMax)
        #print(self._NM_Max_Mid)
        #print(self._ranges[self._NM_Max_Mid])
        #print(self._zeros, self._blindZone)


        


    



      #if self._areas.shape[0] >= 2:
            #for i in range(0,self._areas.shape[0]-1):
                #if (self._areas[i+1][0] - self._areas[i][0]) > 5:
                    #self._areas[i][0] = (self._areas[i][0] + self._areas[i+1][0])/2
                    #self._areas[i][1] = (self._areas[i][1] + self._areas[i+1][1])/2
                    #self._areas = np.delete(self._areas, i+1, axis = 0)"""
        
        #вот тут мы продолжим
        
        
        
        #print(self._ranges)
        #print(self._areas)
        #print(self._zeros)
        #print(self._ranges[self._areas])

    '''def sizing(self, msg):
        self._ranges = np.array(msg.ranges) * 1000
        self.clear()
        self.filter()
        for i in range(0,self._half.size):
            self._half[i] = (self._ranges[i*2] + self._ranges[2*i + 1]) / 2
        
        for i in range(-3,self._half.size):
            if self._half[i-1] > self._half[i] or self._max:
                self._max = True
                if self._half[i-1] < self._half[i]:   
                        if abs(self._half[i - 1] - self._half[i - 5] * 0.98) <= 6:
                            self._areas = np.append(self._areas, (i-1)*2 if i >0 else 360-(i-1)*2)
                            self._max = False
        print(self._half)
        print(self._areas)

    def findTarget(self, msg, minR, maxR):
        self._ranges = np.array(msg.ranges) * 1000
        self.clear()
        if minR > maxR:
            minR = minR -360
        for i in range(minR,maxR):
            if self._ranges[i-1] > self._ranges[i] or self._max:
                self._max = True
                if self._ranges[i-1] < self._ranges[i]:   
                        #if abs(self._ranges[i - 1] - self._ranges[i - 11] * 0.98) <= 5:
                            self._areas = np.append(self._areas, i-1 if i > 0 else 359 - abs(i))
                            self._max = False
        print(self._areas)'''

    #def standarting(self):
        #if self._areas.size < 4:
            


    def setRanges(self, msg):
        self._ranges = np.array(msg.ranges) * 1000

    def getSpeed(self):
        return int(self._spdL), int(self._spdR)            