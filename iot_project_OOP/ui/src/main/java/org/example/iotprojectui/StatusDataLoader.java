package org.example.iotprojectui;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;

/**
 * Loads system status JSON file for dashboard UI.
 */
public class StatusDataLoader {
    
    private static final ObjectMapper mapper = new ObjectMapper();
    
    // Try multiple paths for flexibility
    private static final String[] STATUS_PATHS = {
        "/home/pi/iot/data/status.json",  // Raspberry Pi default
        System.getProperty("user.dir") + "/../data/status.json",  // Development (relative to project)
        System.getProperty("user.dir") + "/data/status.json",  // Development (current dir)
        "data/status.json"  // Fallback
    };
    
    public static JsonNode load() {
        // Try each path until one works
        for (String path : STATUS_PATHS) {
            JsonNode json = loadFromPath(path);
            if (json != null) return json;
        }
        return null;
    }
    
    private static JsonNode loadFromPath(String path) {
        try {
            File file = new File(path);
            if (!file.exists()) {
                return null;
            }
            return mapper.readTree(file);
        } catch (IOException e) {
            return null;
        }
    }
}

