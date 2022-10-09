import random
import numpy as np
import sys
import fbleau as fb
import warnings
warnings.simplefilter("ignore")         #For the DeprecationWarning thrown by numpy
# ---------------------------------------------
# -----------------  Helpers  -----------------
# ---------------------------------------------

#Getlines: Reads the # of lines in the file
#AnalyzeGraph: Reads the file containing the graph and deciphers it, converting it to a list
#GetUsers: Reads the users file 
#Forward: Forwards the message to a random neighbour of the given node, including itself.

def GetLines(filepath):
    f = open(filepath, "r")
    m = len(f.readlines())
    f.close()
    return m

def AnalyzeGraph(filepath):
    f = open(filepath, "r")
    graph = []
    for line in f.readlines():
        subgraph = []
        for index, i in enumerate(line):
            if i == "1":
                subgraph.append(int(index/2))
        graph.append(subgraph)
    f.close()
    return graph

def GetUsers(filepath):
    f = open(filepath, "r")
    users = []
    for line in f.readlines():
        users.append(line.rstrip())
    f.close()
    return users

def Forward(cur, userList):
    tempList = list(userList[cur])
    tempList.append(cur)
    cur = random.choice(tempList)
    return cur

# ---------------------------------------------
# ---------------- Simulation -----------------
# ---------------------------------------------


#Lines 55 - 82
#Basic validation of the arguments, check if phi can be converted to float and open the files via the helper functions
#In case of broken paths != 0, validate the fixing strategy
if __name__ == "__main__":
    assert len(sys.argv) >= 6, "Wrong number of arguments. Please run as following: simulate <phi> <graph-file> <corrupted-file> <users-file> <broken-paths> <fix-strategy>"
    try:
        phi = float(sys.argv[1])
        if (phi >= 1 or phi <= 0):
            print("Please input a valid phi, in between (0,1)")
            sys.exit()
    except ValueError:
        print("Cannot cast " + sys.argv[1] +
              " to float. Please enter a valid argument.")
        sys.exit()
    m = GetLines(sys.argv[2])
    userList = AnalyzeGraph(sys.argv[2])
    corruptedUsers = GetUsers(sys.argv[3])
    initUsers = GetUsers(sys.argv[4])
    brokenPaths = int(sys.argv[5])
    if brokenPaths != 0:
        try:
            if (sys.argv[6] == "last-honest"):
                strategy = 1
            elif (sys.argv[6] == "initiator"):
                strategy = 2
            else:
                print("Wrong strategy. Please select 'last-honest' or 'initiator'.")
                sys.exit()
        except IndexError:
            print("For a non-zero Broken Paths value, please insert a fix strategy: initiator or last-honest.")
            sys.exit()
            
    detectedNodesTotal = []                 #Gets updated to hold all of the detected nodes, for all senders
    detectedNodes = []                      #Stores the detected nodes of the current sender
    for i in initUsers:                     #loops all the senders
        brokenPathsCount = 1                #Makes sure that in case of broken paths = 0 we do not stop the protocol
        detectedNodes.clear()       
        delivered = False                   #Init false, set true if message delivered to break the while loop
        currentUser = i
        #print("Initial user: ", i)
        firstTransmition = True             #Makes sure that we Forward the message
        while (not delivered):              #While the message is not delivered
            if firstTransmition:
                firstTransmition = False    
                prevUser = currentUser
                currentUser = Forward(int(currentUser), userList)   #Forward the message using the sender and the graph
                if str(currentUser) in corruptedUsers and str(prevUser) not in corruptedUsers:  #If the receiver is corrupted and the sender is NOT corrupted
                    detectedNodes.append(int(prevUser))         #Append to the list of detected users
                    if brokenPathsCount==brokenPaths:           #In case of brokenpaths > 0, if we detect #brokenpaths users, we move to the next sender
                        detectedNodesTotal.append(detectedNodes[:])
                        break
                    brokenPathsCount += 1
                    firstTransmition=True               #in case of detection, we always forward the message
                    if brokenPaths != 0:                
                        if strategy==1:                 #we select the strategy
                            currentUser = prevUser      #last-honest
                        else:
                            currentUser = i             #initiator
            else:
                if random.random() < phi:               #probability of forwarding
                    prevUser = currentUser
                    currentUser = Forward(int(currentUser), userList)
                    if str(currentUser) in corruptedUsers and str(prevUser) not in corruptedUsers:
                        #print(prevUser, "detected by corrupted user", currentUser)
                        detectedNodes.append(int(prevUser))
                        if brokenPathsCount==brokenPaths:
                            detectedNodesTotal.append(detectedNodes[:])
                            break
                        brokenPathsCount += 1
                        firstTransmition=True
                        if brokenPaths != 0:
                            if strategy==1:
                                currentUser = prevUser
                            else:
                                currentUser = i
                else:                                   #deliver case
                    delivered = True
                    #print(currentUser, "detected by the Web Server")
                    detectedNodes.append(int(currentUser))
                    print("Initial Sender:", i, "-- Nodes detected:", detectedNodes)
                    detectedNodesTotal.append(detectedNodes[:])     #Store the detected nodes

# ---------------------------------------------
# ----------------- F-Bleau -------------------
# ---------------------------------------------

#In order to make a train and test set, it has to be made sure that the 
#Input arrays are of the same dimensions. Find the size of biggest 
#sub-list and make all of the other lists the same size  
#filling the new cells with the '-1' value, as discussed on piazza.

    maxInternalList = (len(max(detectedNodesTotal, key=len)))

    for detected in detectedNodesTotal:
        if(len(detected) < maxInternalList):
            for x in range(maxInternalList-len(detected)):
                detected.extend([-1])

    #Convert list of lists into Numpy array
    npyDetected = np.array(detectedNodesTotal, dtype='Float64')
    npySenders = np.array(initUsers, dtype='Uint64')
    #Split the datasets into portions 75-25 train-test
    splValue = int(75*len(initUsers) / 100)

    trainSetDetections, testSetDetections  = np.array_split(npyDetected, [splValue])[0], np.array_split(npyDetected, [splValue])[1]
    trainSetSenders, testSetSenders = np.array_split(npySenders, [splValue])[0], np.array_split(npySenders, [splValue])[1]

#Fbleau run with NN Bound
    nnBound = fb.run_fbleau(
            train_x=trainSetDetections, train_y=trainSetSenders,
            test_x=testSetDetections, test_y=testSetSenders,
            estimate="nn-bound", log_errors=False, log_individual_errors=False,
            absolute=False, scale=False)

    print("NN-Bound")
    print(nnBound)