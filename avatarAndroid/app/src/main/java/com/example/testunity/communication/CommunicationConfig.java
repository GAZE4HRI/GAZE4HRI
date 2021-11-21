package com.example.testunity.communication;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.Serializable;

public class CommunicationConfig implements Serializable {
    public String BROKER_IP_OR_NAME;
    public final String BROKER_PORT;
    public final String BROKER_PROTOCOL;
    public final String UPDATE_TOPIC;
    public final String CONFIGURATION_TOPIC;
    public final int STARTING_UPDATE_INTERVAL;
    public static final String INTENT_CONFIG = "INTENT_CONFIG";

    public CommunicationConfig(String BROKER_IP_OR_NAME, String BROKER_PORT, String BROKER_PROTOCOL, String UPDATE_TOPIC, String CONFIGURATION_TOPIC, int STARTING_UPDATE_INTERVAL) {
        this.BROKER_IP_OR_NAME = BROKER_IP_OR_NAME;
        this.BROKER_PORT = BROKER_PORT;
        this.BROKER_PROTOCOL = BROKER_PROTOCOL;
        this.UPDATE_TOPIC = UPDATE_TOPIC;
        this.CONFIGURATION_TOPIC = CONFIGURATION_TOPIC;
        this.STARTING_UPDATE_INTERVAL = STARTING_UPDATE_INTERVAL;
    }

    public CommunicationConfig(String json) throws JSONException {
        JSONObject jsonObject = new JSONObject(json);
        BROKER_IP_OR_NAME = jsonObject.getString("BROKER_IP_OR_NAME");
        BROKER_PORT = jsonObject.getString("BROKER_PORT");
        BROKER_PROTOCOL = jsonObject.getString("BROKER_PROTOCOL");
        UPDATE_TOPIC = jsonObject.getString("BASE_TOPIC") + jsonObject.getString("UPDATE_TOPIC_SUFFIX");
        CONFIGURATION_TOPIC = jsonObject.getString("BASE_TOPIC") + jsonObject.getString("CONFIGURATION_TOPIC_SUFFIX");
        STARTING_UPDATE_INTERVAL = Integer.parseInt(jsonObject.getString("DEFAULT_TICK_LENGTH"));
    }


    public String getBROKER_IP_OR_NAME() {
        return BROKER_IP_OR_NAME;
    }

    public void setBROKER_IP_OR_NAME(String BROKER_IP_OR_NAME) {
        this.BROKER_IP_OR_NAME = BROKER_IP_OR_NAME;
    }

    public String getBROKER_PORT() {
        return BROKER_PORT;
    }

    public String getBROKER_PROTOCOL() {
        return BROKER_PROTOCOL;
    }

    public String getUPDATE_TOPIC() {
        return UPDATE_TOPIC;
    }

    public String getCONFIGURATION_TOPIC() {
        return CONFIGURATION_TOPIC;
    }

    public int getSTARTING_UPDATE_INTERVAL() {
        return STARTING_UPDATE_INTERVAL;
    }

    public static String getIntentConfig() {
        return INTENT_CONFIG;
    }


}
