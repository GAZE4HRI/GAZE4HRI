using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class ButtonClickEvent : MonoBehaviour {

    public Button yourButton;
    public HeadLookController headLook;
    public int number;

    void Start()
    {
        Button btn = yourButton.GetComponent<Button>();
        btn.onClick.AddListener(TaskOnClick);
    }

 


    void TaskOnClick()
    {
        if (number == 1)
            headLook.target = new Vector3(1.5f, 3, 5);
        if (number == 2)
            headLook.target = new Vector3(0, 3, 5);
        if (number == 3)
            headLook.target = new Vector3(-1.5f, 3, 5);
        if (number == 4)
            headLook.target = new Vector3(1.5f, 1.5f, 5);
        if (number == 5)
            headLook.target = new Vector3(0, 1.5f, 5);
        if (number == 6)
            headLook.target = new Vector3(-1.5f, 1.5f, 5);
        if (number == 7)
            headLook.target = new Vector3(1.5f, 0, 5);
        if (number == 8)
            headLook.target = new Vector3(0, 0, 5);
        if (number == 9)
            headLook.target = new Vector3(-1.5f, 0, 5);
    }
}
