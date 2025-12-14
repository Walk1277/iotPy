package org.example.iotprojectui.controllers;

import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonBar;
import javafx.scene.control.ButtonType;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import org.example.iotprojectui.StatusDataLoader;
import com.fasterxml.jackson.databind.JsonNode;

/**
 * Controller for the accident detection screen
 */
public class AccidentScreenController implements BaseScreenController {
    private Runnable onBack;
    
    public AccidentScreenController(Runnable onBack) {
        this.onBack = onBack;
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
        
        // Auto Report Popup Test Button
        Label autoReportLabel = new Label("Accident Auto Report Popup Test");
        autoReportLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        Label autoReportDesc = new Label("Test if the popup that appears during accident detection works correctly.");
        autoReportDesc.setStyle("-fx-font-size: 12px; -fx-text-fill: #666;");
        autoReportDesc.setWrapText(true);
        
        Button testPopupBtn = new Button("Test Popup");
        testPopupBtn.setStyle("-fx-font-size: 14px; -fx-pref-width: 200;");
        testPopupBtn.setOnAction(e -> {
            testAccidentPopup(container);
        });
        
        VBox autoReportBox = new VBox(10);
        autoReportBox.getChildren().addAll(autoReportLabel, autoReportDesc, testPopupBtn);
        autoReportBox.setPadding(new Insets(10, 0, 10, 0));
        
        Button testBtn = new Button("Test Accident Detection");
        testBtn.setOnAction(e -> {
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle("Accident Detection");
            alert.setHeaderText("Accident detected!");
            alert.setContentText("Touch the screen within 10 seconds to cancel the report.");
            alert.showAndWait();
        });
        
        content.getChildren().addAll(backBtn, title, accidentInfo, autoReportBox, testBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
    
    /**
     * Test accident popup - shows the same popup that appears during actual accident detection
     * This is a safe test that doesn't interfere with the actual accident detection system
     */
    private void testAccidentPopup(StackPane container) {
        Platform.runLater(() -> {
            // Create the same Alert dialog as MainScreenController.showResponseRequestModal
            Alert alert = new Alert(Alert.AlertType.ERROR);
            alert.setTitle("ACCIDENT DETECTED!");
            alert.setHeaderText("⚠️ Accident Detected!");
            
            String message = "Test: Accident auto report popup is working correctly.";
            double remainingTime = 10.0;
            int seconds = (int) Math.ceil(remainingTime);
            
            String contentText = message + "\n\n" +
                    "Time remaining: " + seconds + " seconds\n\n" +
                    "Click 'Cancel Report' button to cancel the report.";
            alert.setContentText(contentText);
            
            // Add Cancel Report button (same as MainScreenController)
            ButtonType cancelReportButton = new ButtonType("Cancel Report", ButtonBar.ButtonData.CANCEL_CLOSE);
            alert.getButtonTypes().setAll(cancelReportButton, ButtonType.CLOSE);
            
            // Set alert to be modal and always on top
            if (container.getScene() != null && container.getScene().getWindow() != null) {
                alert.initOwner(container.getScene().getWindow());
            }
            
            // Show alert and wait for user response
            alert.showAndWait().ifPresent(response -> {
                if (response == cancelReportButton) {
                    // User clicked "Cancel Report" - show confirmation
                    Alert confirmAlert = new Alert(Alert.AlertType.INFORMATION);
                    confirmAlert.setTitle("Test Complete");
                    confirmAlert.setHeaderText("Popup Test Successful");
                    confirmAlert.setContentText("Accident auto report popup is working correctly.\n'Cancel Report' button is functioning properly.");
                    confirmAlert.showAndWait();
                } else {
                    // User closed the alert
                    Alert infoAlert = new Alert(Alert.AlertType.INFORMATION);
                    infoAlert.setTitle("Test Complete");
                    infoAlert.setHeaderText("Popup Test Complete");
                    infoAlert.setContentText("Accident auto report popup was displayed correctly.");
                    infoAlert.showAndWait();
                }
            });
        });
    }
}

