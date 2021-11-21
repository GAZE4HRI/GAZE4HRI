package com.example.testunity.communication;

import android.content.Context;
import android.util.Log;

import org.eclipse.paho.client.mqttv3.DisconnectedBufferOptions;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.json.JSONException;

import java.io.UnsupportedEncodingException;
import java.util.Date;

public class UpdateSender extends MqttHelper {
    private final String updateTopic;
    private boolean initialized = false;
    String serverURI;
    String clientId;
    final int qos = 0;

    public UpdateSender(Context context, CommunicationConfig config) {
        super(context, config);
        updateTopic =  config.UPDATE_TOPIC;
        initialized = true;
    }

    public boolean isInitialized() {
        return this.initialized;
    }

    public void sendUpdate(final Date timestamp, final byte[] rawData, final String recognizerName, final String recognizerType) {
        try {
            Log.v("sendUpdate", "sending an update");
            Log.v("sendUpdate", mqttAndroidClient.getClass().getName());
            Log.v("sendUpdate", new Date(System.currentTimeMillis()).toString());

            publishMessage(Formatter.formatRawData(timestamp, rawData, recognizerName, recognizerType), updateTopic, qos);
        } catch (MqttException | JSONException | UnsupportedEncodingException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void connect() {
        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
        mqttConnectOptions.setAutomaticReconnect(true);
        mqttConnectOptions.setCleanSession(false);


        try {

            mqttAndroidClient.connect(mqttConnectOptions, null, new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {

                    DisconnectedBufferOptions disconnectedBufferOptions = new DisconnectedBufferOptions();
                    disconnectedBufferOptions.setBufferEnabled(true);
                    disconnectedBufferOptions.setBufferSize(100);
                    disconnectedBufferOptions.setPersistBuffer(false);
                    disconnectedBufferOptions.setDeleteOldestMessages(false);
                    mqttAndroidClient.setBufferOpts(disconnectedBufferOptions);
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Log.w("Mqtt", "client " + clientId + " Failed to connect to: " + serverURI + exception.toString());
                }
            });


        } catch (MqttException ex) {
            ex.printStackTrace();
        }
    }

    public void initialize() {
        initialized = true;
        connect();
    }
}
