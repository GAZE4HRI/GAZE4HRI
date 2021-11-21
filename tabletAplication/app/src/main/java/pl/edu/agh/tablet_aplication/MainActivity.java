package pl.edu.agh.tablet_aplication;

import android.content.Intent;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.speech.tts.TextToSpeech;
import android.speech.tts.Voice;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.Locale;

import pl.edu.agh.helpers.MqttHelper;
import pl.edu.agh.services.RecorderService;

import static android.speech.SpeechRecognizer.ERROR_CLIENT;
import static android.speech.SpeechRecognizer.ERROR_NO_MATCH;

public class MainActivity extends AppCompatActivity {

    MqttHelper mqttHelper;
    private static final int REQ_CODE_SPEECH_INPUT = 100;

    TextView dataReceived;
    TextToSpeech ttobj;
    private SpeechRecognizer mSpeechRecognizer;
    private Intent mSpeechRecognizerIntent;
    private final String topic = "pepper/speechToText/results";
    private boolean isVoiceSet = false;
    private String path = "/ExperimentONE/video/";
    Button maleBtn;
    Button femaleBtn;
    @Override
    protected void onDestroy() {
        super.onDestroy();
        ttobj.shutdown();
        mSpeechRecognizer.stopListening();
        mSpeechRecognizer.cancel();
        mSpeechRecognizer.destroy();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        dataReceived = (TextView) findViewById(R.id.text);
        ttobj=new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                ttobj.setLanguage(new Locale("pl_PL"));
            }
        });



        mSpeechRecognizer = SpeechRecognizer.createSpeechRecognizer(this);


        mSpeechRecognizerIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        mSpeechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        mSpeechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE,
                new Locale("pl_PL"));
        mSpeechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS,20000);
        mSpeechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS,20000);
        mSpeechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS,20000);




        mSpeechRecognizer.setRecognitionListener(new RecognitionListener() {
            @Override
            public void onReadyForSpeech(Bundle bundle) {
                Toast.makeText(getApplicationContext(),"onReadyForSpeech",
                        Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onBeginningOfSpeech() {
                Toast.makeText(getApplicationContext(),"onBeginningOfSpeech",
                        Toast.LENGTH_SHORT).show();

            }

            @Override
            public void onRmsChanged(float v) {


            }

            @Override
            public void onBufferReceived(byte[] bytes) {
                Toast.makeText(getApplicationContext(),"onBufferReceived",
                        Toast.LENGTH_SHORT).show();

            }

            @Override
            public void onEndOfSpeech() {
                Toast.makeText(getApplicationContext(),"onEndOfSpeech",
                        Toast.LENGTH_SHORT).show();
                try {
                    mqttHelper.publishMessage("EndOfSpeech",topic);
                } catch (MqttException | UnsupportedEncodingException e) {
                    e.printStackTrace();
                }

            }

            @Override
            public void onError(int i) {
                switch (i){
                    case ERROR_CLIENT:
                        try {
                            mqttHelper.publishMessage("nastąpił błąd klienta",topic);
                        } catch (MqttException | UnsupportedEncodingException e) {
                            e.printStackTrace();
                        }
                        break;
                    case ERROR_NO_MATCH:
                        try {
                            mqttHelper.publishMessage("nieudało rozpoznać się treści wpowiedzi",topic);
                        } catch (MqttException | UnsupportedEncodingException e) {
                            e.printStackTrace();
                        }
                        break;
                }


                Toast.makeText(getApplicationContext(),"onError" + i,
                        Toast.LENGTH_SHORT).show();

            }

            @Override
            public void onResults(Bundle bundle) {
                //getting all the matches
                ArrayList<String> matches = bundle
                        .getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);

                //displaying the first match
                if (matches != null) {
                    dataReceived.setText(matches.get(0));
                    try {
                        mqttHelper.publishMessage(matches.get(0),topic);
                    } catch (MqttException | UnsupportedEncodingException e) {
                        e.printStackTrace();
                    }
                }
//
//                mSpeechRecognizer.startListening(mSpeechRecognizerIntent);
            }

            @Override
            public void onPartialResults(Bundle bundle) {

            }

            @Override
            public void onEvent(int i, Bundle bundle) {
                Toast.makeText(getApplicationContext(),"onEvent",
                        Toast.LENGTH_SHORT).show();

            }
        });


        maleBtn = findViewById(R.id.maleVoiceBtn);
        maleBtn.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                isVoiceSet = true;
                dataReceived.setText("male voice set");
                for (Voice voice:ttobj.getVoices()

                        ) {

                    if(voice.getName().equals("pl-pl-x-oda#male_1-local")) {
                        ttobj.setVoice(voice);
                        isVoiceSet = true;
//                            dataReceived.setText(v.toString());
                    }
                }
            }
        });

        femaleBtn = findViewById(R.id.femaleVoiceBtn);
        femaleBtn.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                isVoiceSet = true;
                dataReceived.setText("female voice set");
                for (Voice voice:ttobj.getVoices()

                        ) {

                    if(voice.getName().equals("pl-pl-x-oda-network")) {
                        ttobj.setVoice(voice);
                        isVoiceSet = true;
//                            dataReceived.setText(v.toString());
                    }
                }

            }
        });

        findViewById(R.id.button).setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {
                switch (motionEvent.getAction()) {
                    case MotionEvent.ACTION_UP:
                        mSpeechRecognizer.stopListening();
                        dataReceived.setHint("You will see input here");
                        break;

                    case MotionEvent.ACTION_DOWN:

                        mSpeechRecognizer.startListening(mSpeechRecognizerIntent);
                        dataReceived.setText("");
                        dataReceived.setHint("Listening...");
                        break;
                }
                return false;
            }
        });

        startMqtt();

    }


    private void startMqtt(){
        mqttHelper = new MqttHelper(getApplicationContext());
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
                if (!isVoiceSet)
                    for (Voice v:ttobj.getVoices()

                            ) {

                        if(v.getName().equals("pl-pl-x-oda#male_1-local")) {
                            ttobj.setVoice(v);
                            isVoiceSet = true;
//                            dataReceived.setText(v.toString());
                        }
                    }
                if (topic.equals("pepper/speechToText")){
                    if (message.equals("start recognition")){
                        mSpeechRecognizer.startListening(mSpeechRecognizerIntent);
                        dataReceived.setText("");
                        dataReceived.setHint("Listening...");
                        Toast.makeText(getApplicationContext(),"start recognition",
                                Toast.LENGTH_SHORT).show();
                    }
                    if (message.equals("stop recognition")){
                        mSpeechRecognizer.stopListening();
                        dataReceived.setHint("You will see input here");
                        Toast.makeText(getApplicationContext(),"stop recognition",
                                Toast.LENGTH_SHORT).show();
                    }
                }
                if (topic.equals("pepper/textToSpeech")){
                    Log.w("Debug",message);
                    dataReceived.setText(message);
                    String[] sentences = message.split("\\.|,|\\?");
                    for(String sentence : sentences){
                        ttobj.speak(sentence,TextToSpeech.QUEUE_ADD, null);
                    }

                }
                if (topic.equals("pepper/video")){
                    String[] msg = message.split(" ");
                    if (msg[0].equals("start_recording")){
                        Intent intent = new Intent(MainActivity.this, RecorderService.class);
                        intent.putExtra(RecorderService.INTENT_VIDEO_PATH, path);
                        intent.putExtra(RecorderService.INTENT_VIDEO_NAME, msg[1]);
                        startService(intent);
                        Toast.makeText(getApplicationContext(),"start recording",
                                Toast.LENGTH_SHORT).show();
                    }
                    if (msg[0].equals("stop_recording")){
                        stopService(new Intent(MainActivity.this, RecorderService.class));
                        Toast.makeText(getApplicationContext(),"stop recording",
                                Toast.LENGTH_SHORT).show();
                    }
                }

            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken iMqttDeliveryToken) {

            }
        });
    }
}
