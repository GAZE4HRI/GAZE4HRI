using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

[System.Serializable]
public class FaceDir
{
    public float x;
    public float y;
}


    public class LookingAround : MonoBehaviour {

	// Use this for initialization
    public HeadLookController headLook;
    //private float offset = 1.5f;
    void Start()
    {
        headLook.target = new Vector3(0, 1.5f, 5);
    }

    public void LookStraightDown(String s)
    {
        headLook.target = new Vector3(0, 0, 5);
    }

    public void LookStraightUp(String s)
    {
        headLook.target = new Vector3(0, 3, 5);
    }

    public void LookStraight(String s)
    {
        headLook.target = new Vector3(0, 1.5f, 5);
    }

    public void LookLeftDown(String s)
    {
        headLook.target = new Vector3(1.5f, 0, 5);
    }

    public void LookLeftUp(String s)
    {
        headLook.target = new Vector3(1.5f, 3, 5);
    }

    public void LookLeft(String s)
    {
        headLook.target = new Vector3(1.5f, 1.5f, 5);
    }

    public void LookRightDown(String s)
    {
        headLook.target = new Vector3(-1.5f, 0, 5);
    }

    public void LookRightUp(String s)
    {
        headLook.target = new Vector3(-1.5f, 3, 5);
    }

    public void LookRight(String s)
    {
        headLook.target = new Vector3(-1.5f, 1.5f, 5);
    }

    public void LookFace(String jsonString)
    {
        FaceDir dir = JsonUtility.FromJson<FaceDir>(jsonString);
        headLook.target = new Vector3(dir.x, dir.y, 5);
    }


    // Update is called once per frame
    void Update () {
		
	}
}
