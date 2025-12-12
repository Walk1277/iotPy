package org.example.iotprojectui.controllers;

import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.control.ScrollPane;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.CompletableFuture;

/**
 * Controller for the software update screen
 */
public class UpdateScreenController implements BaseScreenController {
    private Runnable onBack;
    
    public UpdateScreenController(Runnable onBack) {
        this.onBack = onBack;
    }
    
    @Override
    public void showScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("Software Update");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        Label descriptionLabel = new Label("Update Python packages in requirements.txt to the latest version.");
        descriptionLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #666;");
        descriptionLabel.setWrapText(true);
        
        TextArea updateLogArea = new TextArea();
        updateLogArea.setEditable(false);
        updateLogArea.setPrefRowCount(15);
        updateLogArea.setStyle("-fx-font-size: 10px;");
        updateLogArea.setText("Update logs will be displayed here...\n\n");
        
        Button updateBtn = new Button("Run Package Update");
        updateBtn.setPrefWidth(Double.MAX_VALUE);
        updateBtn.setStyle("-fx-font-size: 14px;");
        updateBtn.setOnAction(e -> {
            updateBtn.setDisable(true);
            updateLogArea.clear();
            updateLogArea.appendText("=== Starting Python Package Update ===\n");
            updateLogArea.appendText("Updating packages in requirements.txt to the latest version.\n\n");
            
            CompletableFuture.runAsync(() -> {
                try {
                    String projectDir = System.getProperty("user.dir");
                    if (projectDir.contains("ui")) {
                        projectDir = new java.io.File(projectDir).getParent();
                    }
                    
                    String scriptPathTemp = projectDir + "/update_system.sh";
                    java.io.File scriptFile = new java.io.File(scriptPathTemp);
                    
                    if (!scriptFile.exists()) {
                        String altPath = "/home/pi/iot_project_OOP/update_system.sh";
                        if (new java.io.File(altPath).exists()) {
                            scriptPathTemp = altPath;
                            projectDir = "/home/pi/iot_project_OOP";
                        }
                    }
                    
                    final String scriptPath = scriptPathTemp;
                    
                    if (!new java.io.File(scriptPath).exists()) {
                        Platform.runLater(() -> {
                            updateBtn.setDisable(false);
                            updateLogArea.appendText("[ERROR] Cannot find update_system.sh file.\n");
                            updateLogArea.appendText("Path: " + scriptPath + "\n");
                            Alert alert = new Alert(Alert.AlertType.ERROR);
                            alert.setTitle("Error");
                            alert.setHeaderText("Script file not found");
                            alert.setContentText("Please check if update_system.sh file exists.");
                            alert.showAndWait();
                        });
                        return;
                    }
                    
                    try {
                        java.io.File scriptFileObj = new java.io.File(scriptPath);
                        scriptFileObj.setExecutable(true);
                    } catch (Exception ignored) {}
                    
                    ProcessBuilder pb = new ProcessBuilder("bash", scriptPath);
                    pb.directory(new java.io.File(projectDir));
                    Process process = pb.start();
                    
                    BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                    
                    String line;
                    while ((line = stdoutReader.readLine()) != null) {
                        final String logLine = line;
                        Platform.runLater(() -> {
                            updateLogArea.appendText(logLine + "\n");
                            updateLogArea.setScrollTop(Double.MAX_VALUE);
                        });
                    }
                    
                    while ((line = stderrReader.readLine()) != null) {
                        final String logLine = "[ERROR] " + line;
                        Platform.runLater(() -> {
                            updateLogArea.appendText(logLine + "\n");
                            updateLogArea.setScrollTop(Double.MAX_VALUE);
                        });
                    }
                    
                    int exitCode = process.waitFor();
                    
                    String logFilePath = projectDir + "/update.log";
                    java.io.File logFile = new java.io.File(logFilePath);
                    if (logFile.exists()) {
                        try {
                            java.util.Scanner scanner = new java.util.Scanner(logFile);
                            while (scanner.hasNextLine()) {
                                final String logLine = scanner.nextLine();
                                Platform.runLater(() -> {
                                    updateLogArea.appendText(logLine + "\n");
                                    updateLogArea.setScrollTop(Double.MAX_VALUE);
                                });
                            }
                            scanner.close();
                        } catch (Exception ignored) {}
                    }
                    
                    Platform.runLater(() -> {
                        updateBtn.setDisable(false);
                        if (exitCode == 0) {
                            updateLogArea.appendText("\n=== Update Complete ===\n");
                            Alert alert = new Alert(Alert.AlertType.INFORMATION);
                            alert.setTitle("Update Complete");
                            alert.setHeaderText("Python package update completed.");
                            alert.setContentText("It is recommended to restart the backend to apply changes.");
                            alert.showAndWait();
                        } else {
                            updateLogArea.appendText("\n=== Update Failed (Exit Code: " + exitCode + ") ===\n");
                            Alert alert = new Alert(Alert.AlertType.ERROR);
                            alert.setTitle("Update Failed");
                            alert.setHeaderText("An error occurred during update.");
                            alert.setContentText("Please check the logs above to resolve the issue.");
                            alert.showAndWait();
                        }
                    });
                } catch (Exception ex) {
                    Platform.runLater(() -> {
                        updateBtn.setDisable(false);
                        updateLogArea.appendText("[ERROR] " + ex.getMessage() + "\n");
                        ex.printStackTrace();
                        Alert alert = new Alert(Alert.AlertType.ERROR);
                        alert.setTitle("Error");
                        alert.setHeaderText("Update execution failed");
                        alert.setContentText("Error: " + ex.getMessage());
                        alert.showAndWait();
                    });
                }
            });
        });
        
        content.getChildren().addAll(backBtn, title, descriptionLabel, updateLogArea, updateBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
}

