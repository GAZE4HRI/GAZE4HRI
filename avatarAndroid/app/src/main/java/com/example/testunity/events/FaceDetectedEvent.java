package com.example.testunity.events;

import org.opencv.core.Point;

public class FaceDetectedEvent {
  public float x;
  public float y;

  public FaceDetectedEvent(float x, float y) {
    this.x = x;
    this.y = y;
  }
}
