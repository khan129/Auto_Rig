import maya.cmds as cmds


def create_jntchains(jointls, types):
    '''
    Creates joint lists and parents accordingly.

    Args: type (ik or fk)
    Return: ik joints (list)
            fk joints (list)
    '''
    jj=[]
    for jnt in jointls:
       cmds.select( d=True )
       jointLoc = cmds.xform(jnt, q=1, ws=1, t=1) 
       scaleLoc = cmds.xform(jnt, q=1, ws=1, s=1)
       print jnt
       cmds.joint(n=jnt+'_'+types,p=(jointLoc))
       jj.append(jnt+'_'+types)


    #Parents joint to previous using Index 
    #& retrieve value for first and last jt. 
    for everyobj in jj:
        if  jj.index(everyobj) != 0:
            indexNum = jj.index(everyobj)
            lowerNum = indexNum - 1
            cmds.parent( jj[indexNum], jj[lowerNum] )
    return jj

def create_LimbRig(name, ik, fk):
    '''
    creates full limb rig, ready to be attached to full body rig 
    Args: UserIn (str) text from ui


    '''
    jointls = cmds.ls(orderedSelection = True)        

    ik_jj = create_jntchains(jointls,'ik')
    fk_jj = create_jntchains(jointls,'fk')
    result_jj = create_jntchains(jointls,'Result')

    createIK(name, joints=ik_jj, controls=None)
    createFK(name, joints=fk_jj, controls=None)
    create_switch(name='dragon', control=None, ik_jj=ik_jj, fk_jj=fk_jj, result_jj=result_jj)
    #create_footroll()
def create_switch(name, control, ik_jj, fk_jj, result_jj):
    if control == None:
        ctrl_name=name + 'IKFK_switch_cc'
        cmds.circle(nr=(0,1,0), c=(0, 0, 0), r=1, n= ctrl_name) 
        cmds.pointConstraint(fk_jj[2], ctrl_name, mo = False)
        cmds.pointConstraint(fk_jj[2], ctrl_name, rm = True)
    ikfk_attr = cmds.addAttr(ctrl_name, longName='IKFK', attributeType='float', defaultValue = 1, k=True )

    # IK / FK Switch: FK connections with driven keys 
    index = len(fk_jj)       
    while index > -1:
        index=index-1              
        cmds.parentConstraint(ik_jj[index],fk_jj[index], result_jj[index], mo=False)

        cmds.setAttr(name +'IKFK_switch_cc.IKFK', 0)
        cmds.setAttr(result_jj[index]+'_parentConstraint1.'+fk_jj[index]+ 'W1', 1)
        cmds.setDrivenKeyframe( result_jj[index] + '_parentConstraint1.' +fk_jj[index]+ 'W1', cd = name +'IKFK_switch_cc.IKFK')
        cmds.setAttr(name +'IKFK_switch_cc.IKFK', 1)
        cmds.setAttr(result_jj[index]+'_parentConstraint1.'+fk_jj[index]+ 'W1', 0)
        cmds.setDrivenKeyframe( result_jj[index] + '_parentConstraint1.' +fk_jj[index]+ 'W1', cd = name +'IKFK_switch_cc.IKFK')
        
        cmds.setAttr(name +'IKFK_switch_cc.IKFK', 1)
        cmds.setAttr(result_jj[index]+'_parentConstraint1.'+ik_jj[index]+ 'W0', 1)
        cmds.setDrivenKeyframe( result_jj[index] + '_parentConstraint1.' +ik_jj[index]+ 'W0', cd = name + 'IKFK_switch_cc.IKFK')
        cmds.setAttr(result_jj[index]+'_parentConstraint1.'+ik_jj[index]+ 'W0', 0)
        cmds.setAttr(name +'IKFK_switch_cc.IKFK', 0)
        cmds.setDrivenKeyframe( result_jj[index] + '_parentConstraint1.' +ik_jj[index]+ 'W0', cd = name + 'IKFK_switch_cc.IKFK')

    # Control visibility 
    for fk in fk_jj:

        control = fk + '_fk_cc'
        condNode = cmds.shadingNode('condition', asUtility=True)
        cmds.setAttr(condNode + ".firstTerm", 0) 
        cmds.setAttr(condNode + ".secondTerm", 1) 
        cmds.connectAttr(name + 'IKFK_switch_cc.IKFK', condNode + '.firstTerm')
        cmds.connectAttr(condNode + '.outColorR', control  +  '.visibility')
    cmds.connectAttr(ctrl_name + '.IKFK', name + '_ik_cc.visibility')
    cmds.connectAttr(ctrl_name + '.IKFK', name + '_cc_loc.visibility')

def follow(follow1, follow2, control):
    pass

def create_Spine(name, ik, fk, controls, stretchy, twist):
    pass

def createIK(name, joints, controls):
    firstJoint = joints[0]
    lastJoint = joints[-1]
    cmds.ikHandle( sj=firstJoint, ee=lastJoint, sol= 'ikRPsolver', n = name + '_ik' )
    poleAxis = 'X'
    
    #create pole control
    cmds.spaceLocator(n = name + '_cc_loc')
    cmds.pointConstraint(joints[1], name + '_cc_loc')
    cmds.pointConstraint(joints[1], name + '_cc_loc', rm = True)
    if poleAxis == 'X':
        cmds.move( 10, 0, 0, name + '_cc_loc', r=True )
    if poleAxis == 'Y':
        cmds.move( 0, 10, 0, name + '_cc_loc', r=True )
    if poleAxis == 'Z':
        cmds.move( 0, 0, 10, name + '_cc_loc', r=True )
        print 'pole is in Z'
    if poleAxis == 'Y':
        #set preferred angle
        cmds.rotate( '90deg', 0, 0, joints[1] )
        cmds.joint(joints[1], e=True, spa=True) 
        cmds.rotate( 0, 0, 0, joints[1] )
    if poleAxis == 'Z':
        #set preferred angle
        cmds.rotate( 90, 0, 0, joints[1] )
        cmds.joint(joints[1], e=True, spa=True) 
        cmds.rotate( 0, 0, 0, joints[1] )
    if poleAxis == 'X':
        #set preferred angle
        cmds.rotate(0, 0,  '90deg', joints[1] )
        cmds.joint(joints[1], e=True, spa=True) 
        cmds.rotate( 0, 0, 0, joints[1] )
    if controls == None:
        ctrl_name=name + '_ik_cc'
        cmds.circle(nr=(0,1,0), c=(0, 0, 0), r=(4)*2, n= ctrl_name) 
        cmds.parentConstraint(lastJoint, ctrl_name)
        cmds.parentConstraint(lastJoint, ctrl_name, rm = True)
        cmds.parentConstraint(ctrl_name, name + '_ik')

    else:
        cmds.parentConstraint(controls, name + '_ik', w=1, mo = True)

    
    cmds.makeIdentity(name + '_cc_loc', apply=True, translate=True, rotate=True, scale=True )
    cmds.poleVectorConstraint( name + '_cc_loc', name + '_ik', w=1 )

def getPole(polejoint):

    poleValue = []
    poleAxis = ''
    newAxis = 0

    polePos = cmds.xform('poleJoint', q=1, ws=1, t=1)
    positivePol = []
    
    for axis in polePos:
       if axis <= 0:
           newaxis = axis * -1
           positivePol.append(newaxis)

       else:
           positivePol.append(axis)
           
    Posx = positivePol[0] 
    Posy = positivePol[1]
    Posz = positivePol[2]
    
    ####if joints point in y then poleAxis cant be Y
    
    if Posx > Posy and Posx > Posz:

       poleValue = polePos[0]
       poleAxis = 'X'
    
    if Posy > Posx and Posy > Posz:

       poleValue = polePos[1]
       poleAxis = 'Y'
                 
    if Posz > Posx and Posz > Posy:
         
       poleValue = polePos[2]
       poleAxis = 'Z'
    return poleAxis

def createFK(name, joints, controls):
    '''
    Args:
    joints (list)
    controls (list), if not provided will generate nurb circles 
    '''
    if controls == None:
        controls = []

    #create controls for joints    
    for joint in joints: 
        ctrl_name = joint + '_fk_cc'
        controls.append(ctrl_name)
        print joint
        cmds.circle(nr=(0,1,0), c=(0, 0, 0), r=(4)*2, n= ctrl_name) 
        cmds.parentConstraint(joint, ctrl_name)
        cmds.parentConstraint(joint, ctrl_name, rm = True)
        cmds.orientConstraint(ctrl_name, joint, w=1, mo = True) 

    #parent controls
    for ctrl in controls:           
        if controls.index(ctrl) != 0:
            indexNum2 = controls.index(ctrl) 
            lowerNum2 = indexNum2 - 1               
            cmds.parent( controls[indexNum2], controls[lowerNum2] )                                                 


