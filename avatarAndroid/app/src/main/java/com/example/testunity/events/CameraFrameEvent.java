package com.example.testunity.events;

import android.graphics.Bitmap;



public class CameraFrameEvent {
  public final Bitmap frame;

  public CameraFrameEvent(Bitmap frame) {
    this.frame = frame;

  }
}
