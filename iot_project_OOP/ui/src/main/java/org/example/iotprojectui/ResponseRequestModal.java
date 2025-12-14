package org.example.iotprojectui;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.layout.*;
import javafx.util.Duration;

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
        
        // Remove overlay background - make it transparent
        setStyle("-fx-background-color: transparent;");
        setAlignment(Pos.CENTER);  // Center the modal content
        
        // Create modal content box (400x300 size, centered, eye-catching colors)
        VBox modalBox = new VBox(20);
        modalBox.setAlignment(Pos.CENTER);
        modalBox.setPadding(new Insets(25));
        // Eye-catching style: bright red background with white border
        modalBox.setStyle("-fx-background-color: #ff1a1a; -fx-background-radius: 15; -fx-border-color: #ffffff; -fx-border-width: 4; -fx-border-radius: 15;");
        modalBox.setMaxWidth(400);
        modalBox.setMaxHeight(300);
        modalBox.setPrefWidth(400);
        modalBox.setPrefHeight(300);
        modalBox.setMinWidth(400);
        modalBox.setMinHeight(300);
        
        VBox content = new VBox(15);
        content.setAlignment(Pos.CENTER);
        content.setPadding(new Insets(15));
        
        // Warning icon
        Label warningIcon = new Label("⚠️");
        warningIcon.setStyle("-fx-font-size: 45px;");
        
        // Title - white text on red background for contrast
        Label titleLabel = new Label("ACCIDENT DETECTED!");
        titleLabel.setStyle("-fx-font-size: 20px; -fx-font-weight: bold; -fx-text-fill: #ffffff;");
        
        // Message - white text
        messageLabel = new Label(message);
        messageLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #ffffff; -fx-wrap-text: true;");
        messageLabel.setMaxWidth(320);
        messageLabel.setAlignment(Pos.CENTER);
        
        // Countdown - yellow for visibility
        countdownLabel = new Label();
        countdownLabel.setStyle("-fx-font-size: 32px; -fx-font-weight: bold; -fx-text-fill: #ffff00;");
        updateCountdown(remainingTime);
        
        // Instruction - white text
        Label instructionLabel = new Label("TOUCH TO CANCEL");
        instructionLabel.setStyle("-fx-font-size: 13px; -fx-font-weight: bold; -fx-text-fill: #ffffff;");
        
        content.getChildren().addAll(warningIcon, titleLabel, messageLabel, countdownLabel, instructionLabel);
        modalBox.getChildren().add(content);
        
        getChildren().add(modalBox);
        
        // Make modal box clickable
        modalBox.setOnMouseClicked(e -> {
            // Use API first, fallback to file
            ApiDataLoader.postUserResponse();
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
                countdownLabel.setStyle("-fx-font-size: 32px; -fx-font-weight: bold; -fx-text-fill: #ffffff;");  // White when urgent
            } else if (remainingTime <= 5) {
                countdownLabel.setStyle("-fx-font-size: 32px; -fx-font-weight: bold; -fx-text-fill: #ffaa00;");  // Orange
            } else {
                countdownLabel.setStyle("-fx-font-size: 32px; -fx-font-weight: bold; -fx-text-fill: #ffff00;");  // Yellow
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
    
    // Removed writeUserResponse() - now using ApiDataLoader.postUserResponse()
}

