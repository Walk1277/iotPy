package org.example.iotprojectui;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.layout.*;
import javafx.util.Duration;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

/**
 * Full-screen modal for response request when accident is detected
 */
public class ResponseRequestModal extends StackPane {
    private Label messageLabel;
    private Label countdownLabel;
    private Timeline countdownTimeline;
    @SuppressWarnings("unused")
    private Runnable onResponse;
    
    public ResponseRequestModal(String message, double remainingTime, Runnable onResponse) {
        this.onResponse = onResponse;
        
        // Create full-screen overlay
        setStyle("-fx-background-color: rgba(0, 0, 0, 0.9);");
        setPrefSize(800, 440);
        
        VBox content = new VBox(30);
        content.setAlignment(Pos.CENTER);
        content.setPadding(new Insets(40));
        
        // Warning icon (text-based)
        Label warningIcon = new Label("⚠️");
        warningIcon.setStyle("-fx-font-size: 80px;");
        
        // Title
        Label titleLabel = new Label("ACCIDENT DETECTED!");
        titleLabel.setStyle("-fx-font-size: 36px; -fx-font-weight: bold; -fx-text-fill: #ff4444;");
        
        // Message
        messageLabel = new Label(message);
        messageLabel.setStyle("-fx-font-size: 24px; -fx-text-fill: #ffffff; -fx-wrap-text: true;");
        messageLabel.setMaxWidth(700);
        messageLabel.setAlignment(Pos.CENTER);
        
        // Countdown
        countdownLabel = new Label();
        countdownLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #ffaa00;");
        updateCountdown(remainingTime);
        
        // Instruction
        Label instructionLabel = new Label("TOUCH THE SCREEN TO CANCEL REPORT");
        instructionLabel.setStyle("-fx-font-size: 20px; -fx-font-weight: bold; -fx-text-fill: #ffffff;");
        
        content.getChildren().addAll(warningIcon, titleLabel, messageLabel, countdownLabel, instructionLabel);
        
        getChildren().add(content);
        
        // Make entire modal clickable
        setOnMouseClicked(e -> {
            // Write response to file for backend to read
            writeUserResponse();
            if (onResponse != null) {
                onResponse.run();
            }
        });
        
        // Start countdown animation
        startCountdown(remainingTime);
    }
    
    private void startCountdown(double initialTime) {
        final double[] remaining = {initialTime};
        
        countdownTimeline = new Timeline(new KeyFrame(Duration.seconds(0.1), e -> {
            remaining[0] -= 0.1;
            if (remaining[0] <= 0) {
                remaining[0] = 0;
                if (countdownTimeline != null) {
                    countdownTimeline.stop();
                }
            }
            updateCountdown(remaining[0]);
        }));
        countdownTimeline.setCycleCount(Timeline.INDEFINITE);
        countdownTimeline.play();
    }
    
    public void updateCountdown(double remainingTime) {
        if (countdownLabel != null) {
            int seconds = (int) Math.ceil(remainingTime);
            countdownLabel.setText(String.format("%d seconds", seconds));
            
            // Change color based on remaining time
            if (remainingTime <= 3) {
                countdownLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #ff0000;");
            } else if (remainingTime <= 5) {
                countdownLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #ff8800;");
            } else {
                countdownLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #ffaa00;");
            }
        }
    }
    
    public void updateMessage(String message) {
        if (messageLabel != null) {
            messageLabel.setText(message);
        }
    }
    
    public void stop() {
        if (countdownTimeline != null) {
            countdownTimeline.stop();
        }
    }
    
    private void writeUserResponse() {
        // Try multiple paths (Raspberry Pi and development)
        String[] paths = {
            "/home/pi/iot/data/user_response.json",
            System.getProperty("user.dir") + "/../data/user_response.json",
            System.getProperty("user.dir") + "/data/user_response.json",
            "data/user_response.json"
        };
        
        for (String path : paths) {
            try {
                // Create parent directory if it doesn't exist
                Files.createDirectories(Paths.get(path).getParent());
                
                // Write response JSON
                ObjectMapper mapper = new ObjectMapper();
                ObjectNode response = mapper.createObjectNode();
                response.put("responded", true);
                response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
                
                try (FileWriter writer = new FileWriter(path)) {
                    writer.write(mapper.writerWithDefaultPrettyPrinter().writeValueAsString(response));
                }
                
                System.out.println("[ResponseRequestModal] User response written to: " + path);
                break; // Success, exit loop
            } catch (IOException e) {
                // Try next path
                continue;
            }
        }
    }
}

