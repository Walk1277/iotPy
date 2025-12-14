package org.example.iotprojectui.controllers;

import javafx.geometry.Insets;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import org.example.iotprojectui.StatusDataLoader;
import org.example.iotprojectui.MainScreenController;
import com.fasterxml.jackson.databind.JsonNode;

/**
 * Controller for the accident detection screen
 */
public class AccidentScreenController implements BaseScreenController {
    private Runnable onBack;
    private MainScreenController mainScreenController;
    
    public AccidentScreenController(Runnable onBack, MainScreenController mainScreenController) {
        this.onBack = onBack;
        this.mainScreenController = mainScreenController;
    }
    
    @Override
    public void showScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("Accident Detection Details");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        JsonNode statusJson = StatusDataLoader.load();
        VBox accidentInfo = new VBox(10);
        
        if (statusJson != null) {
            double gValue = statusJson.has("accel_magnitude") ? statusJson.get("accel_magnitude").asDouble() : 1.0;
            boolean impactDetected = statusJson.has("impact_detected") && statusJson.get("impact_detected").asBoolean();
            String gpsPos = statusJson.has("gps_position_string") ? statusJson.get("gps_position_string").asText() : "(-, -)";
            
            Label gLabel = new Label("G-Sensor: " + String.format("%.2fG", gValue));
            gLabel.setStyle("-fx-font-size: 14px;");
            
            Label impactLabel = new Label("Impact Detection: " + (impactDetected ? "Detected" : "None"));
            impactLabel.setStyle("-fx-font-size: 14px;");
            
            Label gpsLabel = new Label("GPS Position: " + gpsPos);
            gpsLabel.setStyle("-fx-font-size: 14px;");
            
            accidentInfo.getChildren().addAll(gLabel, impactLabel, gpsLabel);
        }
        
        // Emergency Report Button - Triggers the actual emergency report popup
        Button emergencyReportBtn = new Button("Trigger Emergency Report");
        emergencyReportBtn.setStyle("-fx-background-color: #d32f2f; -fx-text-fill: white; -fx-font-size: 14px; -fx-font-weight: bold; -fx-padding: 10px 20px;");
        emergencyReportBtn.setOnAction(e -> {
            if (mainScreenController != null) {
                // Show the emergency report popup with 10 second countdown
                mainScreenController.showResponseRequestModal(
                    "Touch screen within 10 seconds to cancel report",
                    10.0
                );
            } else {
                Alert alert = new Alert(Alert.AlertType.WARNING);
                alert.setTitle("Error");
                alert.setHeaderText("Cannot trigger emergency report");
                alert.setContentText("Main screen controller is not available.");
                alert.showAndWait();
            }
        });
        
        content.getChildren().addAll(backBtn, title, accidentInfo, emergencyReportBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
}

