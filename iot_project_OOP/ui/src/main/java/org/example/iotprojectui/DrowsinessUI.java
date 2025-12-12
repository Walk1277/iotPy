package org.example.iotprojectui;

import com.fasterxml.jackson.databind.JsonNode;
import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.stage.Stage;
import javafx.util.Duration;

public class DrowsinessUI extends Application {

    // Try multiple paths for flexibility (Raspberry Pi and development)
    private static final String[] JSON_PATHS = {
        "/home/pi/iot/data/drowsiness.json",  // Raspberry Pi default
        System.getProperty("user.dir") + "/../data/drowsiness.json",  // Development (relative to project)
        System.getProperty("user.dir") + "/data/drowsiness.json",  // Development (current dir)
        "data/drowsiness.json"  // Fallback
    };

    private Label earLabel = new Label("EAR: -");
    private Label stateLabel = new Label("Status: -");
    private Label thresholdLabel = new Label("Threshold: -");
    private Label timeLabel = new Label("-");

    private BorderPane root = new BorderPane();

    @Override
    public void start(Stage stage) {
        stage.setTitle("Drowsiness Detection System");

        root.setPrefSize(800, 480);
        root.setBackground(new Background(new BackgroundFill(Color.BLACK, CornerRadii.EMPTY, Insets.EMPTY)));

        VBox center = new VBox(20);
        center.setAlignment(Pos.CENTER);

        earLabel.setStyle("-fx-font-size: 48px; -fx-text-fill: white;");
        thresholdLabel.setStyle("-fx-font-size: 32px; -fx-text-fill: #b0bec5;");
        stateLabel.setStyle("-fx-font-size: 60px; -fx-font-weight: bold;");
        timeLabel.setStyle("-fx-font-size: 24px; -fx-text-fill: #cfd8dc;");

        center.getChildren().addAll(earLabel, thresholdLabel, stateLabel, timeLabel);
        root.setCenter(center);

        Scene scene = new Scene(root);
        stage.setScene(scene);
        stage.show();

        // Read JSON every second
        Timeline timeline = new Timeline(new KeyFrame(Duration.seconds(1), e -> updateFromJson()));
        timeline.setCycleCount(Timeline.INDEFINITE);
        timeline.play();
    }

    private void updateFromJson() {
        JsonNode json = null;
        // Try each path until one works
        for (String path : JSON_PATHS) {
            json = JsonDataLoader.load(path);
            if (json != null) break;
        }
        if (json == null) return;

        double ear = json.get("ear").asDouble();
        double threshold = json.get("threshold").asDouble();
        String state = json.get("state").asText();
        String timestamp = json.get("timestamp").asText();

        Platform.runLater(() -> {
            earLabel.setText("EAR: " + ear);
            thresholdLabel.setText("Threshold: " + threshold);
            timeLabel.setText("Update: " + timestamp);

            if (state.equals("sleepy")) {
                stateLabel.setText("Drowsiness Detected!");
                stateLabel.setStyle("-fx-font-size: 60px; -fx-font-weight: bold; -fx-text-fill: #ff4444;");
                root.setBackground(new Background(new BackgroundFill(Color.DARKRED, CornerRadii.EMPTY, Insets.EMPTY)));
            } else {
                stateLabel.setText("Normal");
                stateLabel.setStyle("-fx-font-size: 60px; -fx-font-weight: bold; -fx-text-fill: #76ff03;");
                root.setBackground(new Background(new BackgroundFill(Color.BLACK, CornerRadii.EMPTY, Insets.EMPTY)));
            }
        });
    }

    public static void main(String[] args) {
        launch(args);
    }
}
