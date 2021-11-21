package com.example.testunity;

import android.Manifest;
import android.annotation.TargetApi;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Point;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.Image;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Process;
import android.provider.Settings;
import android.renderscript.Allocation;
import android.renderscript.Element;
import android.renderscript.RenderScript;
import android.renderscript.ScriptIntrinsicYuvToRGB;
import android.renderscript.Type;
import android.speech.tts.TextToSpeech;
import android.speech.tts.Voice;
import android.util.Log;
import android.view.Display;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.RelativeLayout;
import android.widget.Toast;

import com.example.testunity.communication.CommunicationConfig;
import com.example.testunity.communication.UpdateSender;
import com.example.testunity.events.ConfigEvent;
import com.example.testunity.communication.MqttHelper;
import com.example.testunity.services.CameraService;
import com.example.testunity.events.CameraFrameEvent;
import com.example.testunity.events.FaceDetectedEvent;
import com.google.gson.JsonObject;
import com.otaliastudios.cameraview.CameraListener;
import com.otaliastudios.cameraview.CameraView;
import com.otaliastudios.cameraview.VideoResult;
import com.otaliastudios.cameraview.controls.Audio;
import com.otaliastudios.cameraview.controls.Engine;
import com.otaliastudios.cameraview.controls.Facing;
import com.otaliastudios.cameraview.controls.Mode;
import com.otaliastudios.cameraview.frame.Frame;
import com.otaliastudios.cameraview.frame.FrameProcessor;
import com.otaliastudios.cameraview.size.Size;
import com.otaliastudios.cameraview.size.SizeSelector;
import com.otaliastudios.cameraview.size.SizeSelectors;
import com.unity3d.player.UnityPlayer;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.greenrobot.eventbus.EventBus;
import org.greenrobot.eventbus.Subscribe;
import org.json.JSONException;
import org.opencv.android.BaseLoaderCallback;
import org.opencv.android.LoaderCallbackInterface;
import org.opencv.android.OpenCVLoader;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

import androidx.annotation.NonNull;
import androidx.annotation.WorkerThread;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import static android.os.Environment.DIRECTORY_MOVIES;
import static com.example.testunity.communication.CommunicationConfig.INTENT_CONFIG;

//import com.mzielu.avatar.UnityPlayerActivity;
//import org.bytedeco.javacpp.Loader;
//import org.bytedeco.javacpp.opencv_core;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = MainActivity.class.getSimpleName(); // implements CameraBridgeViewBase.CvCameraViewListener2 {


    private RenderScript rs;
    private ScriptIntrinsicYuvToRGB yuvToRgbIntrinsic;
    private Type.Builder yuvType, rgbaType;
    private Allocation in, out;

    private UnityPlayer m_UnityPlayer;
    private MqttHelper mqttHelper;
    TextToSpeech ttobj;
    private boolean isVoiceSet;
    private boolean detect = false;
    private final int REQUEST_PERMISSION_STATE = 1;
    Context context;


    private BaseLoaderCallback mLoaderCallback = new BaseLoaderCallback(this) {
        @Override
        public void onManagerConnected(int status) {
            if (status == LoaderCallbackInterface.SUCCESS) {
            } else {
                super.onManagerConnected(status);
            }
        }
    };

    private float x = -1000;
    private float y = -1000;
    private boolean started = false;
    CommunicationConfig communicationConfig = null;
    private EditText editText;
    private CameraView camera;
    private int counter = 0;
    private long lastClicked;
    private int screenWidth;
    private int screenHeight;
    volatile boolean runAudioThread = false;
    private Thread audioThread;
    private UpdateSender updateSender;


//    private boolean isUnityLoaded;
private SizeSelector getSize() {
    SizeSelector width = SizeSelectors.minWidth(1280);
    SizeSelector sizeSelector = SizeSelectors.smallest();
    return SizeSelectors.and(width, sizeSelector);
}
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EventBus.getDefault().register(this);
        setContentView(R.layout.activity_main);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        lastClicked = System.currentTimeMillis();
        Display display = getWindowManager().getDefaultDisplay();
        Point size = new Point();
        display.getSize(size);
        screenWidth = size.x;
        screenHeight = size.y;
        rs = RenderScript.create(this);
        yuvToRgbIntrinsic = ScriptIntrinsicYuvToRGB.create(rs, Element.U8_4(rs));
        camera = findViewById(R.id.camera);
        camera.setLifecycleOwner(this);
        camera.setEngine(Engine.CAMERA2);
        camera.setExperimental(true);
        camera.setAudio(Audio.OFF);
        camera.setMode(Mode.VIDEO);

        camera.setFacing(Facing.FRONT);
//        camera.setAudioBitRate(96000);
//        camera.setVideoBitRate(100000);
        camera.addCameraListener(new CameraListener() {

            @Override
            public void onVideoTaken(VideoResult result) {
                // A Video was taken!
            }

            // And much more
        });
//        camera.setFrameProcessingMaxWidth(1300);
//        camera.setFrameProcessingMaxHeight(800);
        camera.setPreviewStreamSize(getSize());


        camera.setFrameProcessingExecutors(2);
        camera.setFrameProcessingPoolSize(2);
        camera.addFrameProcessor(new FrameProcessor() {
            @Override
            @WorkerThread
            public void process(@NonNull Frame frame) {
                long time = frame.getTime();
                Size size = frame.getSize();
                int format = frame.getFormat();
                Log.v(TAG, String.valueOf(size));
//                Log.v(TAG, String.valueOf(camera.getFrameProcessingMaxWidth()));
//                int userRotation = frame.getRotationToUser();
//                int viewRotation = frame.getRotationToView();
                if (frame.getDataClass() == byte[].class) {
                    long start = System.currentTimeMillis();
                    byte[] data = frame.getData();
//                                                 YuvImage yuv = new YuvImage(data, format, size.getWidth(), size.getHeight(), null);
//                                                 ByteArrayOutputStream out = new ByteArrayOutputStream();
//                                                 yuv.compressToJpeg(new Rect(0, 0, size.getWidth(), size.getHeight()), 100, out);
//                                                 byte[] bytes = out.toByteArray();
//                                                 Bitmap bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.length);


                    if (yuvType == null) {
                        yuvType = new Type.Builder(rs, Element.U8(rs)).setX(size.getHeight() * size.getWidth() * 3 / 2);
                        in = Allocation.createTyped(rs, yuvType.create(), Allocation.USAGE_SCRIPT);

                        rgbaType = new Type.Builder(rs, Element.RGBA_8888(rs)).setX(size.getWidth()).setY(size.getHeight());
                        out = Allocation.createTyped(rs, rgbaType.create(), Allocation.USAGE_SCRIPT);
                        yuvToRgbIntrinsic.setInput(in);
                    }

                    in.copyFrom(data);
                    yuvToRgbIntrinsic.forEach(out);
                    long start2 = System.currentTimeMillis();
                    Bitmap bitmap = Bitmap.createBitmap(size.getWidth(), size.getHeight(), Bitmap.Config.ARGB_8888);
                    Log.v(TAG, "alloc time " + (System.currentTimeMillis() - start2));
                    out.copyTo(bitmap);
                    Log.v(TAG, "conv time " + (System.currentTimeMillis() - start));
                    EventBus.getDefault().post(new CameraFrameEvent(bitmap));
//                                                 File directory = new File(Environment.getExternalStoragePublicDirectory(DIRECTORY_MOVIES).getPath() + "/VideoTest/images/");
//                                                 if (!directory.exists())
//                                                     directory.mkdirs();
//                                                 Log.i("file", directory.getAbsolutePath());
//
//                                                 String fileNameString = "img" + counter++ + ".jpeg";
//
//                                                 String uniqueOutFile = Environment.getExternalStoragePublicDirectory(DIRECTORY_MOVIES).getPath() + "/VideoTest/images/"
//                                                         + fileNameString;
//                                                 try {
//                                                 File outFile = new File(uniqueOutFile);
//                                                 FileOutputStream fileOutputStream = new FileOutputStream(outFile);
//                                                 bitmap.compress(Bitmap.CompressFormat.JPEG, 100, fileOutputStream);
//
//                                                     fileOutputStream.flush();
//                                                     fileOutputStream.close();
//                                                 } catch (IOException e) {
//                                                     e.printStackTrace();
//                                                 }

//                                                 Log.i(TAG,"camera1");
                } else if (frame.getDataClass() == Image.class) {
                    Image image = frame.getData();
                    ByteBuffer bb = image.getPlanes()[0].getBuffer();
                    byte[] data = new byte[bb.remaining()];
                    bb.get(data);

                    if (yuvType == null) {
                        yuvType = new Type.Builder(rs, Element.U8(rs)).setX(size.getHeight() * size.getWidth() * 3 / 2);
                        in = Allocation.createTyped(rs, yuvType.create(), Allocation.USAGE_SCRIPT);

                        rgbaType = new Type.Builder(rs, Element.RGBA_8888(rs)).setX(size.getWidth()).setY(size.getHeight());
                        out = Allocation.createTyped(rs, rgbaType.create(), Allocation.USAGE_SCRIPT);
                        yuvToRgbIntrinsic.setInput(in);
                    }

                    in.copyFrom(data);
                    yuvToRgbIntrinsic.forEach(out);
                    long start2 = System.currentTimeMillis();
                    Bitmap bitmap = Bitmap.createBitmap(size.getWidth(), size.getHeight(), Bitmap.Config.ARGB_8888);
                    Log.v(TAG, "alloc time " + (System.currentTimeMillis() - start2));

                    EventBus.getDefault().post(new CameraFrameEvent(bitmap));
                    image.close();
//                                                 Log.i(TAG,"camera2");
                }
            }
        });


        ttobj = new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                ttobj.setLanguage(new Locale("pl_PL"));
            }
        });


//        ActionBar actionBar = getSupportActionBar();
//        if (actionBar != null) {
//            actionBar.hide();
//        }
        try {
            communicationConfig = new CommunicationConfig(loadJSONFromAsset("communication.json"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        setTheme(android.R.style.Theme_NoTitleBar_Fullscreen);
        RelativeLayout llayout = (RelativeLayout) findViewById(R.id.activity_main);

        Button myButton = new Button(this);
        myButton.setText("Show Main");
        myButton.setX(100);
        myButton.setY(500);
        context = this;
        myButton.setOnClickListener((View.OnClickListener) v -> {

            communicationConfig.setBROKER_IP_OR_NAME(editText.getText().toString());
            startMqtt(communicationConfig);
            m_UnityPlayer = new UnityPlayer(context);
            int glesMode = m_UnityPlayer.getSettings().getInt("gles_mode", 1);
            boolean trueColor8888 = false;
            m_UnityPlayer.init(glesMode, trueColor8888);


            FrameLayout layout = (FrameLayout) findViewById(R.id.unity);
            WindowManager.LayoutParams lp = new WindowManager.LayoutParams(WindowManager.LayoutParams.FILL_PARENT,
                    WindowManager.LayoutParams.FILL_PARENT);
            layout.addView(m_UnityPlayer.getView(), 0, lp);

            m_UnityPlayer.windowFocusChanged(true);
            m_UnityPlayer.resume();

            Intent intent = new Intent(getApplicationContext(), CameraService.class);
            intent.putExtra(INTENT_CONFIG, communicationConfig);
            getApplicationContext().startService(intent);
            started = true;
            llayout.removeView(myButton);
            llayout.removeView(editText);
        });
        llayout.addView(myButton, 300, 200);
        editText = new EditText(this);
        editText.setText("192.168.0.100");
        editText.setX(50);
        editText.setY(200);
        llayout.addView(editText, 500, 150);


//        Intent intent = new Intent(this, MainUnityActivity.class);
//        intent.setFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
//        startActivity(intent);
//        setContentView(R.layout.activity_main);
//        handleIntent(getIntent());

        if (Build.VERSION.SDK_INT >= 23) {
            if (!Settings.canDrawOverlays(MainActivity.this)) {
                Intent intent3 = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getPackageName()));
                startActivityForResult(intent3, 1234);
            }
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.READ_EXTERNAL_STORAGE}, REQUEST_PERMISSION_STATE);
            }

            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQUEST_PERMISSION_STATE);
            }

            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.CAMERA}, REQUEST_PERMISSION_STATE);
            }
        }

        if (shouldAskPermissions()) {
            askPermissions();
        } else {
            Toast.makeText(MainActivity.this,
                    "Permission already granted",
                    Toast.LENGTH_SHORT)
                    .show();
        }


    }

    @Override
    public boolean dispatchTouchEvent(MotionEvent event) {
        x = event.getX();
        y = event.getY();
        Log.v(TAG, "touched" + x + " " + y);

        if (started && System.currentTimeMillis() - lastClicked > 3000 && screenWidth / 2.0f < x) {
            try {
                mqttHelper.publishMessage("click", "click/");
                lastClicked = System.currentTimeMillis();
                Log.v(TAG, "send clicked msg");
            } catch (MqttException e) {
                e.printStackTrace();
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
        }
        return super.dispatchTouchEvent(event);
    }


    private void showExplanation(String title,
                                 String message,
                                 final String permission,
                                 final int permissionRequestCode) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle(title)
                .setMessage(message)
                .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        requestPermission(permission, permissionRequestCode);
                    }
                });
        builder.create().show();
    }

    private void requestPermission(String permissionName, int permissionRequestCode) {
        ActivityCompat.requestPermissions(this,
                new String[]{permissionName}, permissionRequestCode);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[]
            permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        switch (requestCode) {
            case REQUEST_PERMISSION_STATE:
                if (grantResults.length > 0 && permissions[0].equals(Manifest.permission.WRITE_EXTERNAL_STORAGE)) {
                    // check whether storage permission granted or not.
                    if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                        Toast.makeText(MainActivity.this, "Permission Granted!", Toast.LENGTH_SHORT).show();
                        Log.v(TAG, "Permission Granted!");
                    } else {
                        Toast.makeText(MainActivity.this, "Permission Denied!", Toast.LENGTH_SHORT).show();
                        Log.v(TAG, "Permission Denied!");
                    }
                }
                break;

            default:
                break;
        }
    }


    protected boolean shouldAskPermissions() {
        return (Build.VERSION.SDK_INT > Build.VERSION_CODES.LOLLIPOP_MR1);
    }

    @TargetApi(23)
    protected void askPermissions() {
        String[] permissions = {
                "android.permission.READ_EXTERNAL_STORAGE",
                "android.permission.WRITE_EXTERNAL_STORAGE"
        };
        int requestCode = 200;
        requestPermissions(permissions, requestCode);
    }

    private void stopCameraService() {
        getApplicationContext().stopService(new Intent(getApplicationContext(), CameraService.class));
    }


    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
//        mOpenCvCameraView.disableView();
        if (started)
            m_UnityPlayer.windowFocusChanged(hasFocus);


    }

    @Override
    public void onPause() {
        super.onPause();
//        mOpenCvCameraView.disableView();
        camera.close();
        if (started)
            m_UnityPlayer.pause();
    }

    @Override
    public void onResume() {
        super.onResume();
        camera.open();
        if (!OpenCVLoader.initDebug()) {
            OpenCVLoader.initAsync(OpenCVLoader.OPENCV_VERSION_3_0_0, this, mLoaderCallback);
//            String s = org.bytedeco.opencv.global.opencv_core.CV_VERSION;
//            Loader.load(opencv_core.class);
        } else {
            mLoaderCallback.onManagerConnected(LoaderCallbackInterface.SUCCESS);
        }
        if (started)
            m_UnityPlayer.resume();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        camera.destroy();
        m_UnityPlayer.quit();
        ttobj.shutdown();
        stopCameraService();
        started = false;
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

    private void startMqtt(CommunicationConfig communicationConfig) {

        mqttHelper = new MqttHelper(getApplicationContext(), communicationConfig);
        mqttHelper.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean b, String s) {

            }

            @Override
            public void connectionLost(Throwable throwable) {

            }

            @Override
            public void messageArrived(String topic, MqttMessage mqttMessage) throws Exception {
                String message = mqttMessage.toString();
//                Toast.makeText(getApplicationContext(), message, Toast.LENGTH_SHORT).show();
                if (!isVoiceSet)
                    for (Voice v : ttobj.getVoices()
                    ) {

                        if (v.getName().equals("pl-pl-x-oda#male_2-local")) {
                            ttobj.setVoice(v);
                            isVoiceSet = true;
//                            dataReceived.setText(v.toString());
                        }
                    }
                if (topic.equals("unity/")) {
//                    Toast.makeText(getApplicationContext(), message,Toast.LENGTH_SHORT).show();
                    String[] sentences = message.split("\\.|,|\\?|\\s");
//                    Toast.makeText(getApplicationContext(), sentences[0], Toast.LENGTH_SHORT).show();
//                    m_UnityPlayer.UnitySendMessage(sentences[0], sentences[1], "");
//                    mUnityPlayer.UnitySendMessage("GameObject", "LookLeft", "");
                    switch (sentences[0]) {
                        case "LookLeftDown":
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookLeftDown", "");
                            break;
                        case "LookLeftUp":
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookLeftUp", "");
                            break;
                        case "LookLeft":
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookLeft", "");
                            break;
                        case "LookRightDown":
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookRightDown", "");
                            break;
                        case "LookRightUp":
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookRightUp", "");
                            break;
                        case "LookRight":
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookRight", "");
                            break;
                        case "LookStraightDown":
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookStraightDown", "");
                            break;
                        case "LookStraightUp":
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookStraightUp", "");
                            break;
                        case "LookStraight":
                            if (x != -1000) {
                                JsonObject json = new JsonObject();
                                json.addProperty("x", x);
                                json.addProperty("y", y);
                                Log.v(TAG, "onFaceDetectedEvent " + json.toString());
                                m_UnityPlayer.UnitySendMessage("GameObject", "LookFace", json.toString());
                            } else {
                                m_UnityPlayer.UnitySendMessage("GameObject", "LookStraight", "");
                            }
                            break;
                        default:
                            m_UnityPlayer.UnitySendMessage("GameObject", "LookStraight", "");
                            break;
                    }


                }
                if (topic.equals("config/")) {
                    if (message.contains("detect start")) {
                        Map<String, Boolean> map = new HashMap<>();
                        map.put("detect", true);
                        detect = true;
                        EventBus.getDefault().post(new ConfigEvent(map));
                    }
                    if (message.contains("detect stop")) {
                        Map<String, Boolean> map = new HashMap<>();
                        map.put("detect", false);
                        detect = false;
                        EventBus.getDefault().post(new ConfigEvent(map));
                    }
                }
                if (topic.equals("pepper/textToSpeech")) {
                    Log.w("Debug", message);
                    String[] sentences = message.split("\\.|,|\\?");
                    for (String sentence : sentences) {
                        ttobj.speak(sentence, TextToSpeech.QUEUE_ADD, null);
                    }

                }
                if (topic.equals("pepper/video")) {
                    String[] msg = message.split(" ");
                    if (msg[0].equals("start_recording")) {
                        Log.v(TAG, "start_recording");
//                        Intent intent = new Intent(MainActivity.this, RecordServiceOpenCV.class);
//                        intent.putExtra(RecordServiceOpenCV.INTENT_VIDEO_PATH, "/VideoTest/images/");
//                        intent.putExtra(RecordServiceOpenCV.INTENT_VIDEO_NAME, msg[1]);
//                        intent.putExtra(RecordServiceOpenCV.INTENT_VIDEO_WIDTH, 1920);
//                        intent.putExtra(RecordServiceOpenCV.INTENT_VIDEO_HEIGHT, 1080);
//                        startService(intent);

                        File directory = new File(Environment.getExternalStoragePublicDirectory(DIRECTORY_MOVIES).getPath() + "/VideoTest/images/");
                        if (!directory.exists())
                            directory.mkdirs();
                        Log.i("file", directory.getAbsolutePath());
//
                        String fileNameString = "videoOutput_" + msg[1] + ".mp4";
                        String uniqueOutFile = Environment.getExternalStoragePublicDirectory(DIRECTORY_MOVIES).getPath() + "/VideoTest/images/"
                                + fileNameString;
                        File outFile = new File(uniqueOutFile);
                        Log.i("file", outFile.getAbsolutePath());
                        Toast.makeText(getApplicationContext(), "start recording",
                                Toast.LENGTH_SHORT).show();
                        camera.takeVideoSnapshot(outFile);
                        AudioRecordRunnable audioRecordRunnable = new AudioRecordRunnable("audioOutput_" + msg[1] );
                        audioThread = new Thread(audioRecordRunnable);
                        runAudioThread = true;
                        audioThread.start();

                    }
                    if (msg[0].equals("stop_recording")) {
                        Log.v(TAG, "stop recording");
//                        stopService(new Intent(MainActivity.this, RecordServiceOpenCV.class));
                        camera.stopVideo();
                        runAudioThread = false;
                        audioThread.join();
                        Toast.makeText(getApplicationContext(), "stop recording",
                                Toast.LENGTH_SHORT).show();
                    }
                }


            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken iMqttDeliveryToken) {

            }
        });
        Log.i(TAG, "mqtt helper started");
        updateSender = new UpdateSender(getApplicationContext(), communicationConfig);
    }

//    @Override
//    public void onCameraViewStarted(int width, int height) {
////        mRgba = new Mat(height,width, CvType.CV_8UC4);
//        mRgba = new Mat();
//        mGray = new Mat();
//    }

//    @Override
//    public void onCameraViewStopped() {
//        mRgba.release();
//        mGray.release();
//    }

//    @Override
//    public Mat onCameraFrame(CameraBridgeViewBase.CvCameraViewFrame inputFrame) {
//        mRgba = inputFrame.rgba();
//        mGray = inputFrame.gray();
//        if (started)
//            EventBus.getDefault().post(new CameraFrameEvent(mRgba.clone(), mGray.clone()));
//        Log.w("onCameraFrame", "ok");
//        return null;
////        return mRgba;
//    }

    @Subscribe
    public void onFaceDetectedEvent(FaceDetectedEvent event) {
        x = event.x;
        y = event.y;
        JsonObject json = new JsonObject();
        json.addProperty("x", x);
        json.addProperty("y", y);
        Log.v(TAG, "onFaceDetectedEvent " + json.toString());
        m_UnityPlayer.UnitySendMessage("GameObject", "LookFace", json.toString());
    }

    class AudioRecordRunnable implements Runnable {
        private final String filename;
        String TAG = AudioRecordRunnable.class.getSimpleName();
        int sampleAudioRateInHz = 44100;

        AudioRecordRunnable(String name){
            filename = name;

        }
        @Override
        public void run() {
            // Set the thread priority
            android.os.Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);

            // Audio
            int bufferSize;
            short[] audioData;
            int bufferReadResult;






            bufferSize = getBufferSize();
            AudioRecord audioRecord = new AudioRecord(MediaRecorder.AudioSource.DEFAULT, sampleAudioRateInHz,
                    AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, bufferSize);

            audioData = new short[bufferSize / 2];

            Log.d(TAG, "audioRecord.startRecording()");

            if (audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "Audio Record can't initialize!");
                audioRecord = new AudioRecord(MediaRecorder.AudioSource.DEFAULT, sampleAudioRateInHz,
                        AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, bufferSize);
            }
//                try {
//                    Thread.sleep(100);
//                } catch (InterruptedException e) {
//                    e.printStackTrace();
//                }
            try {
                audioRecord.startRecording();
            } catch (Exception e) {
                e.printStackTrace();
            }
            // Audio Capture/Encoding Loop
//            while (runAudioThread) {
//                // Read from audioRecord
//                bufferReadResult = audioRecord.read(audioData, 0, audioData.length);
//                if (bufferReadResult > 0) {
//                    if (recording) {
//                    }
//                }
//            }

            byte[] bytes = new byte[audioData.length * 2];
            FileOutputStream fos = null;
            int readsize = 0;
            File directory = new File(Environment.getExternalStoragePublicDirectory(DIRECTORY_MOVIES).getPath() + "/VideoTest/audio/");
            if (!directory.exists())
                directory.mkdirs();
            String uniqueOutFile = Environment.getExternalStoragePublicDirectory(DIRECTORY_MOVIES).getPath() + "/VideoTest/audio/"
                    + filename + ".pcm";
            File f = new File(uniqueOutFile);
            if (f.exists()) {
                f.delete();

            }
            try {

                fos = new FileOutputStream(uniqueOutFile, true);

            } catch (FileNotFoundException e) {
                Log.e("AudioRecorder", e.getMessage());
            }
            long start;
            while (runAudioThread && audioRecord != null) {
                readsize = audioRecord.read(audioData, 0, audioData.length);
                if (AudioRecord.ERROR_INVALID_OPERATION != readsize && fos != null) {
                    try {
                        Log.v(TAG, "readsize " + String.valueOf(readsize));
                        if (readsize > 0 && readsize <= audioData.length) {
//                            mqttHelper.publishMessage(String.valueOf(System.currentTimeMillis()), "test/");
                            start = System.currentTimeMillis();
                            ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().put(audioData);
                            updateSender.sendUpdate(new Date(System.currentTimeMillis()), bytes, "audio", "audio");

                            Log.v(TAG, "audio time " + String.valueOf(System.currentTimeMillis() - start));
                            fos.write(bytes, 0, bytes.length);
                        }
                    } catch (IOException e) {
                        Log.e(TAG, e.getMessage());
                    }
                }
            }

            try {
                if (fos != null) {
                    fos.close();
                }
            } catch (IOException e) {
                Log.e(TAG, e.getMessage());
            }


            Log.v(TAG, "AudioThread Finished");
            byte buffer[] = null;
            int TOTAL_SIZE = 0;
            File file = new File(uniqueOutFile);
            File out = new File(Environment.getExternalStoragePublicDirectory(DIRECTORY_MOVIES).getPath() + "/VideoTest/audio/" + filename + ".wav");
            if (!file.exists()) {
                return;
            }
            try {
                rawToWave(file, out, sampleAudioRateInHz);
            } catch (IOException e) {
                e.printStackTrace();
            }
            if (file.exists()) {
                file.delete();

            }
            /* Capture/Encoding finished, release recorder */
            if (audioRecord != null) {
                audioRecord.stop();
                audioRecord.release();
                audioRecord = null;


                Log.v(TAG, "audioRecord released");


            }
        }

        private int getBufferSize() {
            int bufferSize =
                    AudioRecord.getMinBufferSize(
                            sampleAudioRateInHz, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
            if (bufferSize == AudioRecord.ERROR || bufferSize == AudioRecord.ERROR_BAD_VALUE) {
                bufferSize = sampleAudioRateInHz * 2;
            }
            return bufferSize;
        }
        private void rawToWave(final File rawFile, final File waveFile, int SAMPLE_RATE) throws IOException {

            int buffSize = getBufferSize();
            byte[] rawData = new byte[buffSize];
            DataInputStream input = null;

            DataOutputStream output = null;
            try {
                output = new DataOutputStream(new FileOutputStream(waveFile));
                // WAVE header
                // see http://ccrma.stanford.edu/courses/422/projects/WaveFormat/
//                output.writeChars("RIFF"); // chunk id
//                output.writeInt(36 + (int) rawFile.length()); // chunk size
//                output.writeChars("WAVE"); // format
//                output.writeChars("fmt "); // subchunk 1 id
//                output.writeInt(16); // subchunk 1 size
//                output.writeShort((short) 1); // audio format (1 = PCM)
//                output.writeShort((short) 1); // number of channels
//                output.writeInt(SAMPLE_RATE); // sample rate
//                output.writeInt(SAMPLE_RATE * 2); // byte rate
//                output.writeShort((short) 2); // block align
//                output.writeShort((short) 16); // bits per sample
//                output.writeChars("data"); // subchunk 2 id
//                output.writeInt((int) rawFile.length()); // subchunk 2 size
//                // Audio data (conversion big endian -> little endian)
////                short[] shorts = new short[rawData.length / 2];
////                ByteBuffer.wrap(rawData).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().get(shorts);
////                ByteBuffer bytes = ByteBuffer.allocate(shorts.length * 2);
////                for (short s : shorts) {
////                    bytes.putShort(s);
////                }
                writeWavHeader(output, (short) 1, SAMPLE_RATE, (short) 16, (int) rawFile.length());
                input = new DataInputStream(new FileInputStream(rawFile));
                int length = 0;
                while ((length = input.read(rawData)) != -1){
                    output.write(rawData, 0, length);
//                    output.write(rawData);
                }


            } finally {
                if (output != null) {
                    output.close();
                }
                if (input != null) {
                    input.close();
                }
            }
        }
        private void writeWavHeader(OutputStream out, short channels, int sampleRate, short bitDepth, int length) throws IOException {
            // Convert the multi-byte integers to raw bytes in little endian format as required by the spec
            byte[] littleBytes = ByteBuffer
                    .allocate(22)
                    .order(ByteOrder.LITTLE_ENDIAN)
                    .putShort(channels)
                    .putInt(sampleRate)
                    .putInt(sampleRate * channels * (bitDepth / 8))
                    .putShort((short) (channels * (bitDepth / 8)))
                    .putShort(bitDepth)
                    .putInt(36 + length)
                    .putInt(44 + length)
                    .array();

            // Not necessarily the best, but it's very easy to visualize this way
            out.write(new byte[]{
                    // RIFF header
                    'R', 'I', 'F', 'F', // ChunkID
                    littleBytes[14], littleBytes[15], littleBytes[16], littleBytes[17], // ChunkSize (must be updated later)
                    'W', 'A', 'V', 'E', // Format
                    // fmt subchunk
                    'f', 'm', 't', ' ', // Subchunk1ID
                    16, 0, 0, 0, // Subchunk1Size
                    1, 0, // AudioFormat
                    littleBytes[0], littleBytes[1], // NumChannels
                    littleBytes[2], littleBytes[3], littleBytes[4], littleBytes[5], // SampleRate
                    littleBytes[6], littleBytes[7], littleBytes[8], littleBytes[9], // ByteRate
                    littleBytes[10], littleBytes[11], // BlockAlign
                    littleBytes[12], littleBytes[13], // BitsPerSample
                    // data subchunk
                    'd', 'a', 't', 'a', // Subchunk2ID
                    littleBytes[18], littleBytes[19], littleBytes[20], littleBytes[21], // Subchunk2Size (must be updated later)
            });
        }
    }
}

