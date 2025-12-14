package org.example.iotprojectui;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.time.Duration;

/**
 * HTTP REST API client for real-time communication with Python backend.
 * Replaces file-based communication to eliminate I/O blocking issues.
 */
public class ApiDataLoader {
    private static final HttpClient client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(2))
        .build();
    
    private static final String API_BASE = "http://localhost:5000/api";
    private static final ObjectMapper mapper = new ObjectMapper();
    private static boolean apiAvailable = true;  // Try API first, fallback to files if unavailable
    
    /**
     * Load drowsiness data from API or fallback to file.
     */
    public static JsonNode loadDrowsiness() {
        if (apiAvailable) {
            JsonNode result = loadFromApi("/drowsiness");
            if (result != null) return result;
            // API failed, fallback to file
            apiAvailable = false;
        }
        return loadFromFile("drowsiness.json");
    }
    
    /**
     * Load system status from API or fallback to file.
     */
    public static JsonNode loadStatus() {
        if (apiAvailable) {
            JsonNode result = loadFromApi("/status");
            if (result != null) return result;
            // API failed, fallback to file
            apiAvailable = false;
        }
        return StatusDataLoader.load();
    }
    
    /**
     * Load log summary from API or fallback to file.
     */
    public static JsonNode loadLogSummary() {
        if (apiAvailable) {
            JsonNode result = loadFromApi("/log_summary");
            if (result != null) return result;
            // API failed, fallback to file
            apiAvailable = false;
        }
        return loadFromFile("log_summary.json");
    }
    
    /**
     * Load data from HTTP REST API.
     */
    private static JsonNode loadFromApi(String endpoint) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_BASE + endpoint))
                .timeout(Duration.ofSeconds(1))
                .GET()
                .build();
            
            HttpResponse<String> response = client.send(
                request, 
                HttpResponse.BodyHandlers.ofString()
            );
            
            if (response.statusCode() == 200) {
                return mapper.readTree(response.body());
            }
        } catch (Exception e) {
            // API unavailable, will fallback to file
            return null;
        }
        return null;
    }
    
    /**
     * Load data from file (fallback method).
     */
    private static JsonNode loadFromFile(String filename) {
        String[] paths = {
            "/home/pi/iot/data/" + filename,
            System.getProperty("user.dir") + "/../data/" + filename,
            System.getProperty("user.dir") + "/data/" + filename,
            "data/" + filename
        };
        
        for (String path : paths) {
            JsonNode result = JsonDataLoader.load(path);
            if (result != null) return result;
        }
        return null;
    }
    
    /**
     * Post user response to API.
     */
    public static void postUserResponse() {
        if (apiAvailable) {
            postToApi("/user_response", "{}");
        } else {
            // Fallback: write to file
            writeToFile("user_response.json", "{\"responded\": true}");
        }
    }
    
    /**
     * Post stop speaker request to API.
     */
    public static void postStopSpeaker() {
        if (apiAvailable) {
            postToApi("/stop_speaker", "{}");
        } else {
            // Fallback: write to file
            writeToFile("stop_speaker.json", "{\"stop\": true}");
        }
    }
    
    /**
     * Post data to HTTP REST API.
     */
    private static void postToApi(String endpoint, String body) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_BASE + endpoint))
                .timeout(Duration.ofSeconds(1))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
            
            client.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (Exception e) {
            // API unavailable, fallback handled by caller
        }
    }
    
    /**
     * Write data to file (fallback method).
     */
    private static void writeToFile(String filename, String content) {
        try {
            String[] paths = {
                "/home/pi/iot/data/" + filename,
                System.getProperty("user.dir") + "/../data/" + filename,
                System.getProperty("user.dir") + "/data/" + filename,
                "data/" + filename
            };
            
            for (String path : paths) {
                try {
                    java.io.File file = new java.io.File(path);
                    file.getParentFile().mkdirs();
                    java.nio.file.Files.write(
                        java.nio.file.Paths.get(path),
                        content.getBytes()
                    );
                    return;
                } catch (Exception e) {
                    continue;
                }
            }
        } catch (Exception e) {
            System.out.println("[API] Failed to write file: " + e.getMessage());
        }
    }
    
    /**
     * Reset API availability flag (for testing/recovery).
     */
    public static void resetApiAvailability() {
        apiAvailable = true;
    }
}

