package org.example.iotprojectui;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;

public class JsonDataLoader {

    private static final ObjectMapper mapper = new ObjectMapper();

    public static JsonNode load(String path) {
        try {
            File file = new File(path);
            if (!file.exists()) {
                System.out.println("[WARN] JSON file does not exist: " + path);
                return null;
            }
            return mapper.readTree(file);

        } catch (IOException e) {
            System.out.println("[ERROR] JSON parsing failed: " + e.getMessage());
            return null;
        }
    }
}
