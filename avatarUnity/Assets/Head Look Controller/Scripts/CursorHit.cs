using UnityEngine;
using System.Collections;

public class CursorHit : MonoBehaviour {
	
	public HeadLookController headLook;
    public int direction;

    void LateUpdate ()
    {
        if(Input.GetKey(KeyCode.Alpha1))
            headLook.target = new Vector3(1.5f, 3, 5);
        if (Input.GetKey(KeyCode.Alpha2))
            headLook.target = new Vector3(0, 3, 5);
        if (Input.GetKey(KeyCode.Alpha3))
            headLook.target = new Vector3(-1.5f, 3, 5);
        if (Input.GetKey(KeyCode.Alpha4))
            headLook.target = new Vector3(1.5f, 1.5f, 5);
        if (Input.GetKey(KeyCode.Alpha5))
            headLook.target = new Vector3(0, 1.5f, 5);
        if (Input.GetKey(KeyCode.Alpha6))
            headLook.target = new Vector3(-1.5f, 1.5f, 5);
        if (Input.GetKey(KeyCode.Alpha7))
            headLook.target = new Vector3(1.5f, 0, 5);
        if (Input.GetKey(KeyCode.Alpha8))
            headLook.target = new Vector3(0, 0, 5);
        if (Input.GetKey(KeyCode.Alpha9))
            headLook.target = new Vector3(-1.5f, 0, 5);

        if (Input.GetKey(KeyCode.Alpha0))
            headLook.target = new Vector3(0, 1.5f, 5);
    }
}
