package com.example.testunity.communication;

import android.util.Base64;
import android.util.Pair;

import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Map;

final class Formatter {
    static String formatRawData(Date timestamp, byte[] rawData, String recognizerName, String recognizerType) throws JSONException {
        JSONObject update = createBasicUpdateJson(timestamp, recognizerName,recognizerType);
        addRawDataToUpdate(update, rawData);
        return update.toString();
    }

    static String formatEmotionWithRawData(Date timestamp, Pair<Map<String, Float>, byte[]> emotionWithRawData, String recognizerName, String recognizerType) throws JSONException {
        JSONObject update = createBasicUpdateJson(timestamp, recognizerName,recognizerType);
        Map<String, Float> emotionData = emotionWithRawData.first;
        addEmotionDataToUpdate(update, emotionData);
        byte[] rawData=emotionWithRawData.second;
        addRawDataToUpdate(update, rawData);
        return update.toString();
    }

    private static void addRawDataToUpdate(JSONObject update, byte[] rawData) throws JSONException {
        update.put("raw_data", Base64.encodeToString(rawData, Base64.DEFAULT));
    }

    private static void addEmotionDataToUpdate(JSONObject update, Map<String, Float> emotionData) throws JSONException {
        JSONObject emotionDataObject = new JSONObject();
        for (String key : emotionData.keySet()) {
            emotionDataObject.put(key, emotionData.get(key));
        }
        update.put("emotion_data", emotionDataObject);
    }

    private static JSONObject createBasicUpdateJson(Date timestamp, String recognizerName, String recognizerType) throws JSONException {
        JSONObject update = new JSONObject();
        update.put("network", recognizerName);
        update.put("type", recognizerType);
        SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault());
        update.put("timestamp", format.format(timestamp));
        return update;
    }

    static String formatEmotionData(Date timestamp, final Map<String, Float> emotionData, String recognizerName, String recognizerType) throws JSONException {
        JSONObject update = createBasicUpdateJson(timestamp, recognizerName,recognizerType);
        addEmotionDataToUpdate(update, emotionData);

        return update.toString();
    }
}
