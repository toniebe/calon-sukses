# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 21:04:56 2017

@author: mizannn
"""

class TourManager:
   destinationNodes = []
   
   def addNode(self, node):
      self.destinationNodes.append(node)
   
   def getNode(self, index):
      return self.destinationNodes[index]
   
   def numberOfNodes(self):
      return len(self.destinationNodes)