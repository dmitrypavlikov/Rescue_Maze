#!/usr/bin/env python3
import rospy

from geometry_msgs.msg import Vector3
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
from std_msgs.msg import Bool
from sensor_msgs.msg import LaserScan, Temperature, BatteryState

from Helpers.exampleD import Example
from Helpers.MotionAlgorithmD import Algorithm

algE = Example()
algD = Algorithm()
indicationArray = [-1]

def scan_callback(msg):
    #algE.setRanges(msg)
    indicationArray[0] = msg.ranges[0]
    algE.mainNM(msg)
    #algE.sizing(msg)

def left_temp_callback(msg):
    return

def right_temp_callback(msg):
    return

def battery_callback(msg):
    return

def gyro_callback(msg):
    return

def compas_callback(msg):
   return

def acc_callback(msg):
    return

def main():
    rospy.init_node("MotionNode")
    currentTime, lastTime = rospy.Time(), rospy.Time()

    #Publisher_XL430R = rospy.Publisher("/RightSpeedFromRasp", Twist, queue_size=10)
    #Publisher_XL430L = rospy.Publisher("/LeftSpeedFromRasp", Twist, queue_size=10)
    #Publisher_AID = rospy.Publisher("/FirstAidKit", Int32, queue_size=10)
    #Publisher_Gyro = rospy.Publisher("/ResetGyro", Int32, queue_size=10)

    #Subscriber_Temp = rospy.Subscriber("GyroscopeFromOpenCR", Vector3, callback=gyro_callback)
    #Subscriber_LeftTemp = rospy.Subscriber("LeftTemperatureFromOpenCR", Temperature, callback=left_temp_callback)
    #Subscriber_RightTemp = rospy.Subscriber("RightTemperatureFromOpenCR", Temperature, callback=right_temp_callback)
    Subscriber_Scan = rospy.Subscriber("/scan", LaserScan, callback=scan_callback)
    #Subscriber_voltage = rospy.Subscriber("VoltageFromOpenCR", Int32, callback=battery_callback)
    #Subscriber_Acc = rospy.Subscriber("AccFromOpenCR", Vector3, callback=acc_callback)
    #Subscriber_Compas = rospy.Subscriber("CompasFromOpenCR", Vector3, callback=compas_callback)
    #Subscriber_Gyro = rospy.Subscriber("GyroFromOpenCR", Vector3, callback=gyro_callback)

    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        """if indicationArray[0] == -1:
            rospy.loginfo("Lidar Error - /scan is empty")"""
        
        # msg_XL430L = Twist()
        # msg_XL430R = Twist()
        #msg_ResetGyro = Int32()
        #AID = Int32()
        #algE.findTarget()


        # rospy.loginfo(f"left  = {msg_XL430L.data}")
        # rospy.loginfo(f"right = {msg_XL430L.data}")
        # rospy.loginfo(f"Method info about speed: {chanksAlg.getSpeed()}")

        #Publisher_XL430L.publish(msg_XL430L)
        #Publisher_XL430R.publish(msg_XL430R)
        #Publisher_AID.publish(AID)
        #Publisher_Gyro.publish(msg_ResetGyro)

        rate.sleep()


if __name__ == '__main__':
    main()

