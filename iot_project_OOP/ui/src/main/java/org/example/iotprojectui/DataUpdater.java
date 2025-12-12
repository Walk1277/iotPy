package org.example.iotprojectui;

import javafx.application.Platform;
import com.fasterxml.jackson.databind.JsonNode;

/**
 * Handles real-time data updates from Python backend
 */
public class DataUpdater {
    private MainScreenController mainScreenController;
    
    public DataUpdater(MainScreenController mainScreenController) {
        this.mainScreenController = mainScreenController;
    }
    
    public void updateFromBackend() {
        JsonNode statusJson = StatusDataLoader.load();
        if (statusJson != null) {
            Platform.runLater(() -> {
                try {
                    updateCurrentStatus();
                    updateDrivingScore();
                    updateAccidentDetection(statusJson);
                } catch (Exception e) {
                    System.err.println("[ERROR] Failed to update: " + e.getMessage());
                }
            });
        }
    }
    
    private void updateCurrentStatus() {
        JsonNode drowsinessJson = null;
        String[] paths = {
            "/home/pi/iot/data/drowsiness.json",
            System.getProperty("user.dir") + "/../data/drowsiness.json",
            System.getProperty("user.dir") + "/data/drowsiness.json",
            "data/drowsiness.json"
        };
        for (String path : paths) {
            drowsinessJson = JsonDataLoader.load(path);
            if (drowsinessJson != null) break;
        }
        
        if (drowsinessJson != null) {
            String state = drowsinessJson.has("state") ? drowsinessJson.get("state").asText() : "unknown";
            boolean alarmOn = drowsinessJson.has("alarm_on") ? drowsinessJson.get("alarm_on").asBoolean() : false;
            boolean showSpeakerPopup = drowsinessJson.has("show_speaker_popup") && drowsinessJson.get("show_speaker_popup").asBoolean();
            double alarmDuration = drowsinessJson.has("alarm_duration") ? drowsinessJson.get("alarm_duration").asDouble() : 0.0;
            
            // Check if speaker popup should be shown
            if (showSpeakerPopup && alarmOn) {
                mainScreenController.showSpeakerStopAlert(alarmDuration);
            } else if (!alarmOn) {
                // Reset alert flag when alarm is off
                mainScreenController.resetSpeakerAlertFlag();
            }
            
            if (state.equals("sleepy") || alarmOn) {
                mainScreenController.updateStatusLabel("Alert", "Drowsiness detected!", "#d32f2f");
            } else if (state.equals("normal")) {
                mainScreenController.updateStatusLabel("Good", "Keep current status", "#2e7d32");
            } else {
                mainScreenController.updateStatusLabel("Waiting", "Checking camera...", "#757575");
            }
        }
    }
    
    private void updateDrivingScore() {
        JsonNode logSummary = null;
        String[] paths = {
            "/home/pi/iot/data/log_summary.json",
            System.getProperty("user.dir") + "/../data/log_summary.json",
            System.getProperty("user.dir") + "/data/log_summary.json",
            "data/log_summary.json"
        };
        for (String path : paths) {
            logSummary = JsonDataLoader.load(path);
            if (logSummary != null) break;
        }
        
        if (logSummary != null && logSummary.has("monthly_score")) {
            int score = logSummary.get("monthly_score").asInt();
            mainScreenController.updateDrivingScore(score + " pts");
        }
    }
    
    private void updateAccidentDetection(JsonNode statusJson) {
        double gValue = statusJson.has("accel_magnitude") ? statusJson.get("accel_magnitude").asDouble() : 1.0;
        boolean impactDetected = statusJson.has("impact_detected") && statusJson.get("impact_detected").asBoolean();
        
        mainScreenController.updateGSensor(String.format("G-sensor: %.1fG", gValue));
        
        // Check for response request
        boolean responseRequested = statusJson.has("response_requested") && statusJson.get("response_requested").asBoolean();
        
        if (responseRequested) {
            // Show response request modal
            String message = statusJson.has("response_message") ? statusJson.get("response_message").asText() : "Touch screen to cancel report";
            double remainingTime = statusJson.has("response_remaining_time") ? statusJson.get("response_remaining_time").asDouble() : 10.0;
            
            mainScreenController.updateResponseRequestModal(message, remainingTime);
            mainScreenController.updateAccidentStatus("Response Required!", "#ff5722");
        } else {
            // Hide modal if it exists
            mainScreenController.hideResponseRequestModal();
            
            if (impactDetected) {
                mainScreenController.updateAccidentStatus("Accident Detected!", "#d32f2f");
            } else {
                mainScreenController.updateAccidentStatus("No Accident", "#1976d2");
            }
        }
    }
}

