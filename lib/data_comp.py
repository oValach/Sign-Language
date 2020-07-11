import math
def comp_dist(trajectory,start,end):
    dists = []
    for i in range(len(trajectory[1])):
        sX = trajectory[start][i][0]
        sY = trajectory[start][i][1]
        sZ = trajectory[start][i][2]
        eX = trajectory[end][i][0]
        eY = trajectory[end][i][1]
        eZ = trajectory[end][i][2]
        dist = math.sqrt(((sX-eX)**2)+((sY-eY)**2)+((sZ-eZ)**2))
        dists.append(dist)
    
    return dists

def comp_speed(trajectory,dictionary,previousLine,traLine,nextLine):
    prevStart = previousLine['annotation_Filip_bvh_frame'][0] #začátek předchozího znaku
    prevEnd = previousLine['annotation_Filip_bvh_frame'][1] #konec -||-
    frameP = prevStart
    prevDist = [0]*61
    while frameP < prevEnd-1:
        oneFrameDist1 = comp_dist(trajectory,frameP,frameP+1)
        for jointIdx1 in range(len(oneFrameDist1)):
            prevDist[jointIdx1] = prevDist[jointIdx1] + oneFrameDist1[jointIdx1]
        frameP += 1
    prevFrames = prevEnd-prevStart
    prevTime = prevFrames/120
    prevSpeed = [dist / prevTime for dist in prevDist]


    traStart = traLine['annotation_Filip_bvh_frame'][0] #začátek transitiony
    traEnd = traLine['annotation_Filip_bvh_frame'][1] #konec -||-
    frameT = traStart
    traDist = [0]*61
    while frameT < traEnd-1:
        oneFrameDist2 = comp_dist(trajectory,frameT,frameT+1)
        for jointIdx2 in range(len(oneFrameDist2)):
            traDist[jointIdx2] = traDist[jointIdx2] + oneFrameDist2[jointIdx2]
        frameT += 1
    traFrames = traEnd-traStart
    traTime = traFrames/120
    traSpeed = [dist / traTime for dist in traDist]

    nextStart = nextLine['annotation_Filip_bvh_frame'][0] #začátek následujícího znaku
    nextEnd = nextLine['annotation_Filip_bvh_frame'][1] #konec -||-
    frameN = nextStart
    nextDist = [0]*61
    while frameN < nextEnd-1: #abs. vzd. po snímcích
        if nextEnd > trajectory.shape[0]:
            return [None,None,None,0]
        oneFrameDist3 = comp_dist(trajectory,frameN,frameN+1)
        for jointIdx3 in range(len(oneFrameDist3)):
            nextDist[jointIdx3] = nextDist[jointIdx3] + oneFrameDist3[jointIdx3]
        frameN += 1
    nextFrames = nextEnd-nextStart
    nextTime = nextFrames/120
    nextSpeed = [dist / nextTime for dist in nextDist]

    return [prevSpeed,traSpeed,nextSpeed,1]
