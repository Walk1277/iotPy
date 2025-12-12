package org.example.iotprojectui;

import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import org.example.iotprojectui.controllers.StatusScreenController;
import org.example.iotprojectui.controllers.ReportScreenController;
import org.example.iotprojectui.controllers.AccidentScreenController;
import org.example.iotprojectui.controllers.UpdateScreenController;
import org.example.iotprojectui.controllers.SettingsScreenController;
import org.example.iotprojectui.controllers.LogScreenController;

/**
 * Main screen controller - manages the main dashboard with panels
 */
public class MainScreenController {
    private StackPane mainContainer;
    private ScreenNavigator navigator;
    
    // Screen controllers
    private StatusScreenController statusScreenController;
    private ReportScreenController reportScreenController;
    private AccidentScreenController accidentScreenController;
    private UpdateScreenController updateScreenController;
    private SettingsScreenController settingsScreenController;
    private LogScreenController logScreenController;
    
    // Main screen panels
    private VBox currentStatusPanel;
    private VBox drivingScorePanel;
    private VBox accidentDetectionPanel;
    private VBox settingsPanel;
    private VBox logCheckPanel;
    
    // Labels for real-time updates
    private Label currentStatusLabel;
    private Label currentStatusSubLabel;
    private Label drivingScoreLabel;
    private Label accidentStatusLabel;
    private Label gSensorLabel;
    
    // Response request modal
    private ResponseRequestModal responseModal;
    
    public MainScreenController(BorderPane root) {
        this.mainContainer = new StackPane();
        root.setCenter(mainContainer);
        
        // Initialize screen controllers
        this.statusScreenController = new StatusScreenController(this::showMainScreen);
        this.reportScreenController = new ReportScreenController(this::showMainScreen);
        this.accidentScreenController = new AccidentScreenController(this::showMainScreen);
        this.updateScreenController = new UpdateScreenController(this::showMainScreen);
        this.settingsScreenController = new SettingsScreenController(this::showMainScreen);
        this.logScreenController = new LogScreenController(this::showMainScreen);
        
        this.navigator = new ScreenNavigator(mainContainer, this::showMainScreen);
    }
    
    public void showMainScreen() {
        GridPane mainScreen = createMainScreen();
        navigator.navigateToScreen(mainScreen);
    }
    
    private GridPane createMainScreen() {
        GridPane grid = new GridPane();
        grid.setPadding(new Insets(8));
        grid.setHgap(8);
        grid.setVgap(8);
        
        // Top-Left: Current Status
        currentStatusPanel = createCurrentStatusPanel();
        grid.add(currentStatusPanel, 0, 0);
        
        // Top-Right: Driving Score
        drivingScorePanel = createDrivingScorePanel();
        grid.add(drivingScorePanel, 1, 0);
        
        // Bottom-Left: Accident Detection
        accidentDetectionPanel = createAccidentDetectionPanel();
        grid.add(accidentDetectionPanel, 0, 1);
        
        // Bottom-Right: Settings and Log Check (split vertically)
        HBox bottomRightBox = new HBox(6);
        bottomRightBox.setAlignment(Pos.CENTER);
        settingsPanel = createSettingsPanel();
        logCheckPanel = createLogCheckPanel();
        bottomRightBox.getChildren().addAll(settingsPanel, logCheckPanel);
        grid.add(bottomRightBox, 1, 1);
        
        // Set column and row constraints
        ColumnConstraints col1 = new ColumnConstraints();
        col1.setPercentWidth(50);
        ColumnConstraints col2 = new ColumnConstraints();
        col2.setPercentWidth(50);
        grid.getColumnConstraints().addAll(col1, col2);
        
        RowConstraints row1 = new RowConstraints();
        row1.setPercentHeight(50);
        RowConstraints row2 = new RowConstraints();
        row2.setPercentHeight(50);
        grid.getRowConstraints().addAll(row1, row2);
        
        return grid;
    }
    
    private VBox createCurrentStatusPanel() {
        VBox panel = new VBox(10);
        panel.setPadding(new Insets(15));
        panel.setStyle("-fx-background-color: #e8f5e9; -fx-border-color: #4caf50; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setAlignment(Pos.CENTER);
        
        Label title = new Label("Current Status");
        title.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        currentStatusLabel = new Label("Good");
        currentStatusLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #2e7d32;");
        
        currentStatusSubLabel = new Label("Keep current status");
        currentStatusSubLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #2e7d32;");
        
        panel.getChildren().addAll(title, currentStatusLabel, currentStatusSubLabel);
        panel.setOnMouseClicked(e -> statusScreenController.showScreen(mainContainer));
        panel.setStyle(panel.getStyle() + " -fx-cursor: hand;");
        
        return panel;
    }
    
    private VBox createDrivingScorePanel() {
        VBox panel = new VBox(10);
        panel.setPadding(new Insets(15));
        panel.setStyle("-fx-background-color: #fff3e0; -fx-border-color: #ff9800; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setAlignment(Pos.CENTER);
        
        Label title = new Label("Driving Score");
        title.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        drivingScoreLabel = new Label("87 pts");
        drivingScoreLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #e65100;");
        
        panel.getChildren().addAll(title, drivingScoreLabel);
        panel.setOnMouseClicked(e -> reportScreenController.showScreen(mainContainer));
        panel.setStyle(panel.getStyle() + " -fx-cursor: hand;");
        
        return panel;
    }
    
    private VBox createAccidentDetectionPanel() {
        VBox panel = new VBox(10);
        panel.setPadding(new Insets(15));
        panel.setStyle("-fx-background-color: #e3f2fd; -fx-border-color: #2196f3; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setAlignment(Pos.CENTER);
        
        Label title = new Label("Accident Detection");
        title.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        accidentStatusLabel = new Label("No Accident");
        accidentStatusLabel.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: #1976d2;");
        
        gSensorLabel = new Label("G-sensor: 1.0G");
        gSensorLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #1976d2;");
        
        panel.getChildren().addAll(title, accidentStatusLabel, gSensorLabel);
        panel.setOnMouseClicked(e -> accidentScreenController.showScreen(mainContainer));
        panel.setStyle(panel.getStyle() + " -fx-cursor: hand;");
        
        return panel;
    }
    
    private VBox createSettingsPanel() {
        VBox panel = new VBox(5);
        panel.setPadding(new Insets(6));
        panel.setStyle("-fx-background-color: #f3e5f5; -fx-border-color: #9c27b0; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setPrefWidth(190);
        
        Label title = new Label("Settings");
        title.setStyle("-fx-font-size: 13px; -fx-font-weight: bold;");
        
        Button updateBtn = new Button("Update");
        updateBtn.setPrefWidth(Double.MAX_VALUE);
        updateBtn.setPrefHeight(28);
        updateBtn.setStyle("-fx-font-size: 11px;");
        updateBtn.setOnAction(e -> updateScreenController.showScreen(mainContainer));
        
        Button personalSettingsBtn = new Button("Personal");
        personalSettingsBtn.setPrefWidth(Double.MAX_VALUE);
        personalSettingsBtn.setPrefHeight(28);
        personalSettingsBtn.setStyle("-fx-font-size: 11px;");
        personalSettingsBtn.setOnAction(e -> settingsScreenController.showPersonalSettingsScreen(mainContainer));
        
        Button drowsinessSettingsBtn = new Button("Drowsiness");
        drowsinessSettingsBtn.setPrefWidth(Double.MAX_VALUE);
        drowsinessSettingsBtn.setPrefHeight(28);
        drowsinessSettingsBtn.setStyle("-fx-font-size: 11px;");
        drowsinessSettingsBtn.setOnAction(e -> settingsScreenController.showDrowsinessSettingsScreen(mainContainer));
        
        Button autoReportSettingsBtn = new Button("Auto Report");
        autoReportSettingsBtn.setPrefWidth(Double.MAX_VALUE);
        autoReportSettingsBtn.setPrefHeight(28);
        autoReportSettingsBtn.setStyle("-fx-font-size: 11px;");
        autoReportSettingsBtn.setOnAction(e -> settingsScreenController.showAutoReportSettingsScreen(mainContainer));
        
        Button systemCheckBtn = new Button("System Check");
        systemCheckBtn.setPrefWidth(Double.MAX_VALUE);
        systemCheckBtn.setPrefHeight(28);
        systemCheckBtn.setStyle("-fx-font-size: 11px;");
        systemCheckBtn.setOnAction(e -> settingsScreenController.showSystemCheckScreen(mainContainer));
        
        panel.getChildren().addAll(title, updateBtn, personalSettingsBtn, drowsinessSettingsBtn, autoReportSettingsBtn, systemCheckBtn);
        
        return panel;
    }
    
    private VBox createLogCheckPanel() {
        VBox panel = new VBox(5);
        panel.setPadding(new Insets(6));
        panel.setStyle("-fx-background-color: #eceff1; -fx-border-color: #607d8b; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setPrefWidth(190);
        
        Label title = new Label("Log Check");
        title.setStyle("-fx-font-size: 13px; -fx-font-weight: bold;");
        
        TextArea logArea = new TextArea();
        logArea.setEditable(false);
        logArea.setPrefRowCount(5);
        logArea.setPrefHeight(115);
        logArea.setStyle("-fx-font-size: 9px;");
        logArea.setText("Loading logs...\n");
        
        logScreenController.loadLogs(logArea);
        
        Button refreshBtn = new Button("Refresh");
        refreshBtn.setPrefWidth(Double.MAX_VALUE);
        refreshBtn.setPrefHeight(24);
        refreshBtn.setStyle("-fx-font-size: 10px;");
        refreshBtn.setOnAction(e -> logScreenController.loadLogs(logArea));
        
        panel.getChildren().addAll(title, logArea, refreshBtn);
        panel.setOnMouseClicked(e -> {
            if (e.getTarget() != refreshBtn && e.getTarget() != logArea) {
                logScreenController.showScreen(mainContainer);
            }
        });
        panel.setStyle(panel.getStyle() + " -fx-cursor: hand;");
        
        return panel;
    }
    
    // Update methods for DataUpdater
    public void updateStatusLabel(String text, String subText, String color) {
        if (currentStatusLabel != null) {
            currentStatusLabel.setText(text);
            currentStatusLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: " + color + ";");
        }
        if (currentStatusSubLabel != null) {
            currentStatusSubLabel.setText(subText);
            currentStatusSubLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: " + color + ";");
        }
    }
    
    public void updateDrivingScore(String score) {
        if (drivingScoreLabel != null) {
            drivingScoreLabel.setText(score);
        }
    }
    
    public void updateAccidentStatus(String text, String color) {
        if (accidentStatusLabel != null) {
            accidentStatusLabel.setText(text);
            accidentStatusLabel.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: " + color + ";");
        }
    }
    
    public void updateGSensor(String text) {
        if (gSensorLabel != null) {
            gSensorLabel.setText(text);
        }
    }
    
    public void showResponseRequestModal(String message, double remainingTime) {
        Platform.runLater(() -> {
            System.out.println("[MainScreenController] showResponseRequestModal called - message: " + message + ", remaining: " + remainingTime);
            // Remove existing modal if any
            hideResponseRequestModal();
            
            // Create and show new modal
            responseModal = new ResponseRequestModal(message, remainingTime, () -> {
                // User responded - hide modal
                hideResponseRequestModal();
                // TODO: Send response to backend (could use a callback or file-based communication)
            });
            
            // Add modal on top of everything
            mainContainer.getChildren().add(responseModal);
            System.out.println("[MainScreenController] Response modal added to container. Children count: " + mainContainer.getChildren().size());
        });
    }
    
    public void updateResponseRequestModal(String message, double remainingTime) {
        Platform.runLater(() -> {
            if (responseModal != null) {
                responseModal.updateMessage(message);
                responseModal.updateCountdown(remainingTime);
            } else {
                // Modal doesn't exist, create it
                showResponseRequestModal(message, remainingTime);
            }
        });
    }
    
    public void hideResponseRequestModal() {
        Platform.runLater(() -> {
            if (responseModal != null) {
                responseModal.stop();
                mainContainer.getChildren().remove(responseModal);
                responseModal = null;
            }
        });
    }
    
    private boolean speakerAlertShown = false;
    
    public void showSpeakerStopAlert(double alarmDuration) {
        Platform.runLater(() -> {
            // Only show alert once per alarm session
            if (speakerAlertShown) {
                return;
            }
            
            speakerAlertShown = true;
            
            Alert alert = new Alert(Alert.AlertType.WARNING);
            alert.setTitle("Speaker Alert");
            alert.setHeaderText("Speaker is Active");
            alert.setContentText(String.format("The alarm speaker has been active for %.1f seconds.\n\nClick OK to stop the speaker.", alarmDuration));
            
            // Set alert to be modal and always on top
            alert.initOwner(mainContainer.getScene().getWindow());
            
            alert.showAndWait().ifPresent(response -> {
                if (response == ButtonType.OK) {
                    // Write stop request to file
                    writeStopSpeakerRequest();
                    speakerAlertShown = false;
                }
            });
        });
    }
    
    public void resetSpeakerAlertFlag() {
        speakerAlertShown = false;
    }
    
    public boolean isResponseRequestModalActive() {
        return responseModal != null;
    }
    
    public void hideSpeakerAlertIfShowing() {
        Platform.runLater(() -> {
            // If speaker alert is showing, we can't directly close it
            // But we can reset the flag so it won't show again
            // The alert will close when user clicks OK
            if (speakerAlertShown) {
                System.out.println("[MainScreenController] Speaker alert is showing, but accident modal has higher priority");
                // Note: JavaFX Alert.showAndWait() is blocking, so we can't close it programmatically
                // The user will need to close it first, but we prevent new ones from showing
                speakerAlertShown = true; // Keep flag true to prevent new alerts
            }
        });
    }
    
    private void writeStopSpeakerRequest() {
        // Try multiple paths (Raspberry Pi and development)
        String[] paths = {
            "/home/pi/iot/data/stop_speaker.json",
            System.getProperty("user.dir") + "/../data/stop_speaker.json",
            System.getProperty("user.dir") + "/data/stop_speaker.json",
            "data/stop_speaker.json"
        };
        
        for (String path : paths) {
            try {
                java.nio.file.Files.createDirectories(java.nio.file.Paths.get(path).getParent());
                
                com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
                com.fasterxml.jackson.databind.node.ObjectNode stopRequest = mapper.createObjectNode();
                stopRequest.put("stop", true);
                stopRequest.put("timestamp", java.time.LocalDateTime.now().format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
                
                try (java.io.FileWriter writer = new java.io.FileWriter(path)) {
                    writer.write(mapper.writerWithDefaultPrettyPrinter().writeValueAsString(stopRequest));
                }
                
                System.out.println("[MainScreenController] Stop speaker request written to: " + path);
                break; // Success, exit loop
            } catch (Exception e) {
                // Try next path
                continue;
            }
        }
    }
}

