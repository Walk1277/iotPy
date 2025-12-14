package org.example.iotprojectui;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
import javafx.util.Duration;

/**
 * Main Application class for IoT Driver Monitoring System UI
 */
public class MainApplication extends Application {
    
    private MainScreenController mainScreenController;
    private DataUpdater dataUpdater;
    
    @Override
    public void start(Stage primaryStage) {
        BorderPane root = new BorderPane();
        
        // Wrap BorderPane in StackPane for modal overlay support
        StackPane rootStackPane = new StackPane();
        rootStackPane.getChildren().add(root);
        
        // Initialize controllers
        mainScreenController = new MainScreenController(root);
        dataUpdater = new DataUpdater(mainScreenController);
        
        // Create and show main screen
        mainScreenController.showMainScreen();
        
        Scene scene = new Scene(rootStackPane, 800, 440);
        primaryStage.setTitle("Smart Accident Prevention Kit");
        primaryStage.setScene(scene);
        primaryStage.setResizable(false);
        primaryStage.show();
        
        // Start updating data from Python backend (faster update with API - 100ms)
        Timeline updateTimeline = new Timeline(new KeyFrame(Duration.millis(100), e -> {
            dataUpdater.updateFromBackend();
        }));
        updateTimeline.setCycleCount(Timeline.INDEFINITE);
        updateTimeline.play();
    }

    public static void main(String[] args) {
        launch(args);
    }
}

