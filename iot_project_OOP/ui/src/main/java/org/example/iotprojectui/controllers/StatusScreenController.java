package org.example.iotprojectui.controllers;

import javafx.geometry.Insets;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import org.example.iotprojectui.StatusDataLoader;
import org.example.iotprojectui.JsonDataLoader;
import com.fasterxml.jackson.databind.JsonNode;

/**
 * Controller for the status detail screen
 */
public class StatusScreenController implements BaseScreenController {
    private Runnable onBack;
    
    public StatusScreenController(Runnable onBack) {
        this.onBack = onBack;
    }
    
    @Override
    public void showScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("Current Status Details");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        JsonNode statusJson = StatusDataLoader.load();
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
        
        VBox statusInfo = new VBox(10);
        if (drowsinessJson != null) {
            double ear = drowsinessJson.has("ear") ? drowsinessJson.get("ear").asDouble() : 0.0;
            String state = drowsinessJson.has("state") ? drowsinessJson.get("state").asText() : "unknown";
            
            Label earLabel = new Label("EAR: " + String.format("%.2f", ear));
            earLabel.setStyle("-fx-font-size: 14px;");
            Label stateLabel = new Label("State: " + (state.equals("sleepy") ? "Sleepy" : state.equals("normal") ? "Normal" : "Waiting"));
            stateLabel.setStyle("-fx-font-size: 14px;");
            
            statusInfo.getChildren().addAll(earLabel, stateLabel);
        }
        
        if (statusJson != null) {
            Label sensorLabel = new Label("Sensor Status: " + (statusJson.has("sensor_status") ? statusJson.get("sensor_status").asText() : "-"));
            sensorLabel.setStyle("-fx-font-size: 14px;");
            statusInfo.getChildren().add(sensorLabel);
        }
        
        content.getChildren().addAll(backBtn, title, statusInfo);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
}

