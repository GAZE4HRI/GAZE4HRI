package com.example.testunity.services;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.IBinder;
import android.os.PowerManager;
import android.util.Log;

import com.example.testunity.R;
import com.example.testunity.communication.CommunicationConfig;
import com.example.testunity.communication.UpdateSender;
import com.example.testunity.events.CameraFrameEvent;
import com.example.testunity.events.ConfigEvent;
import com.example.testunity.events.FaceDetectedEvent;
import com.google.android.gms.vision.face.FaceDetector;

import org.greenrobot.eventbus.EventBus;
import org.greenrobot.eventbus.Subscribe;
import org.json.JSONException;
import org.opencv.android.Utils;
import org.opencv.core.Mat;
import org.opencv.core.MatOfRect;
import org.opencv.core.Rect;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.opencv.objdetect.CascadeClassifier;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static com.example.testunity.communication.CommunicationConfig.INTENT_CONFIG;

public class CameraService extends Service {
    private PowerManager.WakeLock wakeLock;
    private ExecutorService executor;
    private ExecutorService VideoExecutor;
    private CascadeClassifier mJavaDetector;
    private FaceDetector faceDetector;
    private int mAbsoluteFaceSize = 0;
    private float mRelativeFaceSize = 0.15f;
    private  boolean detect = false;
    private int counter = 0;
    private Bitmap frame = null;
    private String TAG = "CameraService";
    private UpdateSender updateSender;
    public CameraService() {
//        EventBus.getDefault().register(this);
    }

    @Override
    public void onCreate() {
        super.onCreate();
        CameraService context = this;
        EventBus.getDefault().register(this);
        mJavaDetector = getCascade(context);
        executor = Executors.newFixedThreadPool(3);
        VideoExecutor = Executors.newFixedThreadPool(10);
        this.faceDetector = new
                FaceDetector.Builder(context).setTrackingEnabled(false)
                .build();

    }
    public CascadeClassifier getCascade(Context context){
        try {
            InputStream is = context.getResources().openRawResource(R.raw.lbpcascade_frontalface);
            File cascadeDir = context.getDir("cascade", Context.MODE_PRIVATE);
            File mCascadeFile = new File(cascadeDir, "lbpcascade_frontalface.xml");
            FileOutputStream os;
            os = new FileOutputStream(mCascadeFile);

            byte[] buffer = new byte[4096];
            int bytesRead;
            while ((bytesRead = is.read(buffer)) != -1) {
                os.write(buffer, 0, bytesRead);
            }
            is.close();
            os.close();
            mJavaDetector = new CascadeClassifier(mCascadeFile.getAbsolutePath());
            if (mJavaDetector.empty()) {
                mJavaDetector = null;
            }
            cascadeDir.delete();
        }catch (IOException e){
            Log.e("CameraE", "getCascade Error", e);
        }

        return mJavaDetector;
    }

    @Subscribe
    public void onCameraFrameEvent(CameraFrameEvent event) {
        Log.v(TAG, "onCameraFrame ok");
        frame = event.frame;

        Runnable Task = () -> {
            try {
                ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                frame.compress(Bitmap.CompressFormat.JPEG, 50, byteArrayOutputStream);
                byte[] arr = byteArrayOutputStream.toByteArray();
                Log.v(TAG, Thread.currentThread().getName());
                updateSender.sendUpdate(new Date(System.currentTimeMillis()), arr, "video", "video");
            } catch (NullPointerException e) {
                Log.e(TAG, "sender error", e);
            }
            Log.v(TAG, "send update");
        };
        if(updateSender!=null)
            VideoExecutor.execute(Task);

        if(detect && counter> 3){
            Runnable runnableTask = this::detect;
            executor.execute(runnableTask);

            counter = 0;
        }
        counter++;
    }
    public void detect(){
        long start = System.currentTimeMillis();
        Mat mat = new Mat();
        Mat mGray = new Mat();
        Utils.bitmapToMat(frame, mat);
        Imgproc.cvtColor(mat, mGray, Imgproc.COLOR_BGR2GRAY);
        int height = mGray.rows();
        int width = mGray.cols();
        if (mAbsoluteFaceSize == 0) {

            if (Math.round(height * mRelativeFaceSize) > 0) {
                mAbsoluteFaceSize = Math.round(height * mRelativeFaceSize);
            }
        }

        MatOfRect faces = new MatOfRect();
        if (mJavaDetector != null) {
            mJavaDetector.detectMultiScale(mGray, faces, 1.1, 2, 2,
                    new Size(mAbsoluteFaceSize, mAbsoluteFaceSize), new Size());
        } else {
            Log.e(TAG, "Detection method is not selected!");
        }
        Rect[] facesArray = faces.toArray();
        float xCenter = 0;
        float yCenter = 0;
        if(0 == facesArray.length){
            Log.e(TAG, "no faces detected");
        }

        for (int i = 0; i < facesArray.length; i++) {
            //Imgproc.rectangle(mRgba, facesArray[i].tl(), facesArray[i].br(),
            //    FACE_RECT_COLOR, 3);
            xCenter = (facesArray[i].x + facesArray[i].width + facesArray[i].x) / 2.0f;
            yCenter = (facesArray[i].y + facesArray[i].y + facesArray[i].height) / 2.0f;
            float halfx = (float) (width) / 2.0f;
            float x = ((halfx - xCenter)/halfx) * -1.5f;
            float halfy = (float) (height) / 2.0f;
            float y = ((halfy - yCenter)/halfy) * 1.5f + 1.5f;
            Log.v(TAG, "detect time " + (System.currentTimeMillis() - start));
            EventBus.getDefault().post(new FaceDetectedEvent(x,y));


        }
//        if (!faceDetector.isOperational()) {
//            Log.e("VideoEmotionRecognizer", "Could not set up the face detector!");
//            return;
//        }
//
//        Frame frame = new Frame.Builder().setBitmap(this.frame).build();
//        SparseArray<Face> faces = faceDetector.detect(frame);
//        if (faces.size() == 0) {
//            Log.e(TAG, "No face recogized");
//            return;
//        }
//        Face face = faces.valueAt(0);
//        float x1 = face.getPosition().x;
//        float y1 = face.getPosition().y;
//        float width = face.getWidth();
//        float height = face.getHeight();
//        float xCenter = (x1 + width + x1) / 2.0f;
//        float yCenter = (y1 + y1 + height) / 2.0f;
//        float halfx = (float) (width) / 2.0f;
//        float x = ((halfx - xCenter)/halfx) * -1.5f;
//        float halfy = (float) (height) / 2.0f;
//        float y = ((halfy - yCenter)/halfy) * 1.5f + 1.5f;
//        EventBus.getDefault().post(new FaceDetectedEvent(x,y));
    }

    @Subscribe
    public void onConfigEvent(ConfigEvent event) {
        Log.v(TAG,"onConfigEvent ok");
        if (event.config.containsKey("detect")){
            detect = event.config.get("detect");
        }

    }


    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
        wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,
                "MyApp::CameraLock");
        wakeLock.acquire(10*60*1000L /*10 minutes*/);
        CommunicationConfig communicationConfig = (CommunicationConfig) intent.getSerializableExtra(INTENT_CONFIG);
        if(communicationConfig==null) {
            try {
                communicationConfig = new CommunicationConfig(loadJSONFromAsset("communication.json"));
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        updateSender = new UpdateSender(getApplicationContext(), communicationConfig);

        return Service.START_STICKY;
    }

    private String loadJSONFromAsset(String fileName) {
        String json = null;
        try {
            InputStream is = getApplicationContext().getAssets().open(fileName);
            int size = is.available();
            byte[] buffer = new byte[size];
            is.read(buffer);
            is.close();
            json = new String(buffer, StandardCharsets.UTF_8);
        } catch (IOException ex) {
            ex.printStackTrace();
            return null;
        }
        return json;
    }
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }


    @Override
    public void onDestroy() {
        Log.d(TAG, "Service.onDestroy()...");

        wakeLock.release();
        super.onDestroy();

    }
}
