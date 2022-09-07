import sys

class MinHeap:

    def __init__(self):
        self.maxsize = 1000000
        self.size = 0
        self.Heap = ["0", 0, ""]*(self.maxsize + 1)
        self.FRONT = 1

    def parent(self, pos):
        return pos//2


    def leftChild(self, pos):
        return 2 * pos


    def rightChild(self, pos):
        return (2 * pos) + 1


    def isLeaf(self, pos):
        return pos*2 > self.size

    def swap(self, fpos, spos):
        self.Heap[fpos], self.Heap[spos] = self.Heap[spos], self.Heap[fpos]

    def minHeapify(self, pos):
        try:
            if not self.isLeaf(pos):
                if (self.Heap[pos][0] > self.Heap[self.leftChild(pos)][0] or
                self.Heap[pos][0] > self.Heap[self.rightChild(pos)][0]):

                    
                    if self.Heap[self.leftChild(pos)][0] < self.Heap[self.rightChild(pos)][0]:
                        self.swap(pos, self.leftChild(pos))
                        self.minHeapify(self.leftChild(pos))

                    else:
                        self.swap(pos, self.rightChild(pos))
                        self.minHeapify(self.rightChild(pos))
        except TypeError:
            pass

    def insert(self, l):
        element = l[0]
        fp = l[1]
        value = l[2]

        self.size+= 1
        self.Heap[self.size] = l

        current = self.size
        parent_index = self.parent(current)
        
        try:
            while self.Heap[current][0] < self.Heap[self.parent(current)][0]:
                self.swap(current, self.parent(current))
                current = self.parent(current)
        except IndexError:
            print("Index error")

    def minheap(self):

        for pos in range(self.size//2, 0, -1):
            self.minHeapify(pos)

    def remove(self):

        popped = self.Heap[self.FRONT]
        self.Heap[self.FRONT] = self.Heap[self.size]
        self.size-= 1
        self.minHeapify(self.FRONT)
        return popped

