package com.example.testunity.events;

import java.util.Map;

public class ConfigEvent {
    public Map<String, Boolean> config;

    public ConfigEvent(Map<String,Boolean> config){
        this.config = config;
    }
}
