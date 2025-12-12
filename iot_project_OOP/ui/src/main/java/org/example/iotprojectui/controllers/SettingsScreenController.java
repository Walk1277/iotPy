package org.example.iotprojectui.controllers;

import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.control.ScrollPane;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.CompletableFuture;

/**
 * Controller for all settings screens (Personal, Drowsiness, Auto Report, System Check)
 */
public class SettingsScreenController {
    private Runnable onBack;
    
    public SettingsScreenController(Runnable onBack) {
        this.onBack = onBack;
    }
    
    public void showPersonalSettingsScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("Personal Settings");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        Label nameLabel = new Label("Name:");
        TextField nameField = new TextField("User");
        
        Label phoneLabel = new Label("Phone:");
        TextField phoneField = new TextField("010-0000-0000");
        
        Button saveBtn = new Button("Save");
        saveBtn.setOnAction(e -> {
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle("Save");
            alert.setHeaderText("Settings saved.");
            alert.showAndWait();
        });
        
        content.getChildren().addAll(backBtn, title, nameLabel, nameField, phoneLabel, phoneField, saveBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
    
    public void showDrowsinessSettingsScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("Drowsiness Detection Settings");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        Label thresholdLabel = new Label("Threshold: 0.22");
        thresholdLabel.setStyle("-fx-font-size: 14px;");
        
        Slider thresholdSlider = new Slider(0.1, 0.4, 0.22);
        thresholdSlider.setShowTickLabels(true);
        thresholdSlider.setShowTickMarks(true);
        thresholdSlider.setMajorTickUnit(0.05);
        thresholdSlider.valueProperty().addListener((obs, o, n) ->
            thresholdLabel.setText("Threshold: " + String.format("%.2f", n.doubleValue()))
        );
        
        CheckBox alarmCheck = new CheckBox("Enable Alarm");
        alarmCheck.setSelected(true);
        
        Button saveBtn = new Button("Save");
        saveBtn.setOnAction(e -> {
            double thresholdValue = thresholdSlider.getValue();
            boolean alarmEnabled = alarmCheck.isSelected();
            
            CompletableFuture.runAsync(() -> {
                try {
                    String projectDir = System.getProperty("user.dir");
                    if (projectDir.contains("ui")) {
                        projectDir = new java.io.File(projectDir).getParent();
                    }
                    
                    String[] pythonPaths = {"python3", "python"};
                    String pythonCmd = "python3";
                    for (String path : pythonPaths) {
                        try {
                            Process testProcess = new ProcessBuilder(path, "--version").start();
                            if (testProcess.waitFor() == 0) {
                                pythonCmd = path;
                                break;
                            }
                        } catch (Exception ignored) {}
                    }
                    
                    String scriptPath = projectDir + "/update_config.py";
                    java.io.File scriptFile = new java.io.File(scriptPath);
                    
                    if (!scriptFile.exists()) {
                        String altPath = "/home/pi/iot_project_OOP/update_config.py";
                        if (new java.io.File(altPath).exists()) {
                            scriptPath = altPath;
                            projectDir = "/home/pi/iot_project_OOP";
                        }
                    }
                    
                    ProcessBuilder pb1 = new ProcessBuilder(
                        pythonCmd,
                        scriptPath,
                        "EAR_THRESHOLD",
                        String.valueOf(thresholdValue)
                    );
                    pb1.directory(new java.io.File(projectDir));
                    Process process1 = pb1.start();
                    
                    BufferedReader reader1 = new BufferedReader(new InputStreamReader(process1.getInputStream()));
                    String line;
                    while ((line = reader1.readLine()) != null) {
                        System.out.println("[Config Update] " + line);
                    }
                    int exitCode1 = process1.waitFor();
                    
                    Platform.runLater(() -> {
                        if (exitCode1 == 0) {
                            Alert alert = new Alert(Alert.AlertType.INFORMATION);
                            alert.setTitle("Save");
                            alert.setHeaderText("Settings saved.");
                            alert.setContentText(String.format("Threshold: %.2f\nAlarm Enabled: %s", 
                                thresholdValue, alarmEnabled ? "Yes" : "No"));
                            alert.showAndWait();
                        } else {
                            Alert alert = new Alert(Alert.AlertType.ERROR);
                            alert.setTitle("Error");
                            alert.setHeaderText("Failed to save settings");
                            alert.setContentText("Failed to update config.py.");
                            alert.showAndWait();
                        }
                    });
                } catch (Exception ex) {
                    Platform.runLater(() -> {
                        Alert alert = new Alert(Alert.AlertType.ERROR);
                        alert.setTitle("Error");
                        alert.setHeaderText("Failed to save settings");
                        alert.setContentText("Error: " + ex.getMessage());
                        alert.showAndWait();
                    });
                }
            });
        });
        
        content.getChildren().addAll(backBtn, title, thresholdLabel, thresholdSlider, alarmCheck, saveBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
    
    public void showAutoReportSettingsScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("Auto Report Settings");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        CheckBox autoReportCheck = new CheckBox("Enable Auto Report");
        autoReportCheck.setSelected(true);
        
        Separator separator1 = new Separator();
        
        Label fromPhoneLabel = new Label("From Phone Number:");
        fromPhoneLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
        TextField fromPhoneField = new TextField("010-7220-5917");
        fromPhoneField.setPromptText("e.g., 010-1234-5678");
        
        Label toPhoneLabel = new Label("To Phone Number:");
        toPhoneLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
        TextField toPhoneField = new TextField("010-4090-7445");
        toPhoneField.setPromptText("e.g., 010-1234-5678");
        
        Separator separator2 = new Separator();
        
        Label systemLabel = new Label("System Management");
        systemLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        Button clearLogsBtn = new Button("Clear System Logs");
        clearLogsBtn.setStyle("-fx-background-color: #d32f2f; -fx-text-fill: white; -fx-font-size: 14px;");
        clearLogsBtn.setPrefWidth(Double.MAX_VALUE);
        clearLogsBtn.setOnAction(e -> {
            Alert confirmAlert = new Alert(Alert.AlertType.CONFIRMATION);
            confirmAlert.setTitle("Clear Logs");
            confirmAlert.setHeaderText("Do you want to clear logs?");
            confirmAlert.setContentText("All driving event logs will be deleted and the score will be reset to 100.\nThis action cannot be undone.");
            
            confirmAlert.showAndWait().ifPresent(response -> {
                if (response == ButtonType.OK) {
                    clearLogsBtn.setDisable(true);
                    
                    CompletableFuture.runAsync(() -> {
                        try {
                            String projectDir = System.getProperty("user.dir");
                            if (projectDir.contains("ui")) {
                                projectDir = new java.io.File(projectDir).getParent();
                            }
                            
                            String[] pythonPaths = {"python3", "python"};
                            String pythonCmd = "python3";
                            for (String path : pythonPaths) {
                                try {
                                    Process testProcess = new ProcessBuilder(path, "--version").start();
                                    if (testProcess.waitFor() == 0) {
                                        pythonCmd = path;
                                        break;
                                    }
                                } catch (Exception ignored) {}
                            }
                            
                            String scriptPath = projectDir + "/clear_logs.py";
                            java.io.File scriptFile = new java.io.File(scriptPath);
                            
                            if (!scriptFile.exists()) {
                                String altPath = "/home/pi/iot_project_OOP/clear_logs.py";
                                if (new java.io.File(altPath).exists()) {
                                    scriptPath = altPath;
                                    projectDir = "/home/pi/iot_project_OOP";
                                }
                            }
                            
                            ProcessBuilder pb = new ProcessBuilder(pythonCmd, scriptPath);
                            pb.directory(new java.io.File(projectDir));
                            Process process = pb.start();
                            
                            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                            String line;
                            while ((line = reader.readLine()) != null) {
                                System.out.println("[Clear Logs] " + line);
                            }
                            
                            int exitCode = process.waitFor();
                            Platform.runLater(() -> {
                                clearLogsBtn.setDisable(false);
                                
                                if (exitCode == 0) {
                                    Alert successAlert = new Alert(Alert.AlertType.INFORMATION);
                                    successAlert.setTitle("Complete");
                                    successAlert.setHeaderText("Logs cleared.");
                                    successAlert.setContentText("All driving event logs have been deleted and the score has been reset to 100.");
                                    successAlert.showAndWait();
                                } else {
                                    Alert errorAlert = new Alert(Alert.AlertType.ERROR);
                                    errorAlert.setTitle("Error");
                                    errorAlert.setHeaderText("Failed to clear logs");
                                    errorAlert.setContentText("An error occurred while clearing log files.");
                                    errorAlert.showAndWait();
                                }
                            });
                        } catch (Exception ex) {
                            Platform.runLater(() -> {
                                clearLogsBtn.setDisable(false);
                                Alert errorAlert = new Alert(Alert.AlertType.ERROR);
                                errorAlert.setTitle("Error");
                                errorAlert.setHeaderText("Failed to clear logs");
                                errorAlert.setContentText("Error: " + ex.getMessage());
                                errorAlert.showAndWait();
                            });
                        }
                    });
                }
            });
        });
        
        Button saveBtn = new Button("Save");
        saveBtn.setPrefWidth(Double.MAX_VALUE);
        saveBtn.setStyle("-fx-font-size: 14px;");
        saveBtn.setOnAction(e -> {
            boolean autoReportEnabled = autoReportCheck.isSelected();
            String fromPhone = fromPhoneField.getText().trim();
            String toPhone = toPhoneField.getText().trim();
            
            if (fromPhone.isEmpty() || toPhone.isEmpty()) {
                Alert alert = new Alert(Alert.AlertType.WARNING);
                alert.setTitle("Input Error");
                alert.setHeaderText("Please enter phone numbers.");
                alert.setContentText("Both sender and receiver phone numbers must be entered.");
                alert.showAndWait();
                return;
            }
            
            saveBtn.setDisable(true);
            
            CompletableFuture.runAsync(() -> {
                try {
                    String projectDir = System.getProperty("user.dir");
                    if (projectDir.contains("ui")) {
                        projectDir = new java.io.File(projectDir).getParent();
                    }
                    
                    String[] pythonPaths = {"python3", "python"};
                    String pythonCmd = "python3";
                    for (String path : pythonPaths) {
                        try {
                            Process testProcess = new ProcessBuilder(path, "--version").start();
                            if (testProcess.waitFor() == 0) {
                                pythonCmd = path;
                                break;
                            }
                        } catch (Exception ignored) {}
                    }
                    
                    String scriptPath = projectDir + "/update_config.py";
                    java.io.File scriptFile = new java.io.File(scriptPath);
                    
                    if (!scriptFile.exists()) {
                        String altPath = "/home/pi/iot_project_OOP/update_config.py";
                        if (new java.io.File(altPath).exists()) {
                            scriptPath = altPath;
                            projectDir = "/home/pi/iot_project_OOP";
                        }
                    }
                    
                    // Update AUTO_REPORT_ENABLED
                    ProcessBuilder pb1 = new ProcessBuilder(
                        pythonCmd,
                        scriptPath,
                        "AUTO_REPORT_ENABLED",
                        String.valueOf(autoReportEnabled)
                    );
                    pb1.directory(new java.io.File(projectDir));
                    Process process1 = pb1.start();
                    BufferedReader reader1 = new BufferedReader(new InputStreamReader(process1.getInputStream()));
                    String line;
                    while ((line = reader1.readLine()) != null) {
                        System.out.println("[Config Update] " + line);
                    }
                    int exitCode1 = process1.waitFor();
                    
                    // Update SMS_FROM_NUMBER
                    ProcessBuilder pb2 = new ProcessBuilder(
                        pythonCmd,
                        scriptPath,
                        "SMS_FROM_NUMBER",
                        fromPhone
                    );
                    pb2.directory(new java.io.File(projectDir));
                    Process process2 = pb2.start();
                    BufferedReader reader2 = new BufferedReader(new InputStreamReader(process2.getInputStream()));
                    while ((line = reader2.readLine()) != null) {
                        System.out.println("[Config Update] " + line);
                    }
                    int exitCode2 = process2.waitFor();
                    
                    // Update SMS_TO_NUMBER
                    ProcessBuilder pb3 = new ProcessBuilder(
                        pythonCmd,
                        scriptPath,
                        "SMS_TO_NUMBER",
                        toPhone
                    );
                    pb3.directory(new java.io.File(projectDir));
                    Process process3 = pb3.start();
                    BufferedReader reader3 = new BufferedReader(new InputStreamReader(process3.getInputStream()));
                    while ((line = reader3.readLine()) != null) {
                        System.out.println("[Config Update] " + line);
                    }
                    int exitCode3 = process3.waitFor();
                    
                    Platform.runLater(() -> {
                        saveBtn.setDisable(false);
                        
                        if (exitCode1 == 0 && exitCode2 == 0 && exitCode3 == 0) {
                            Alert alert = new Alert(Alert.AlertType.INFORMATION);
                            alert.setTitle("Save");
                            alert.setHeaderText("Settings saved.");
                            alert.setContentText(String.format("Auto Report Enabled: %s\nFrom Number: %s\nTo Number: %s",
                                autoReportEnabled ? "Yes" : "No", fromPhone, toPhone));
                            alert.showAndWait();
                        } else {
                            Alert alert = new Alert(Alert.AlertType.ERROR);
                            alert.setTitle("Error");
                            alert.setHeaderText("Failed to save settings");
                            alert.setContentText("Failed to update config.py.");
                            alert.showAndWait();
                        }
                    });
                } catch (Exception ex) {
                    Platform.runLater(() -> {
                        saveBtn.setDisable(false);
                        Alert alert = new Alert(Alert.AlertType.ERROR);
                        alert.setTitle("Error");
                        alert.setHeaderText("Failed to save settings");
                        alert.setContentText("Error: " + ex.getMessage());
                        alert.showAndWait();
                    });
                }
            });
        });
        
        content.getChildren().addAll(backBtn, title, autoReportCheck, separator1,
            fromPhoneLabel, fromPhoneField, toPhoneLabel, toPhoneField, separator2,
            systemLabel, clearLogsBtn, saveBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
    
    public void showSystemCheckScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("System Check");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        Label descriptionLabel = new Label("Check if each sensor and function is working properly.");
        descriptionLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #666;");
        descriptionLabel.setWrapText(true);
        
        TextArea resultArea = new TextArea();
        resultArea.setEditable(false);
        resultArea.setPrefRowCount(20);
        resultArea.setStyle("-fx-font-size: 11px;");
        resultArea.setText("Click the 'Run System Check' button to execute system check.\n\n");
        
        Button checkBtn = new Button("Run System Check");
        checkBtn.setPrefWidth(Double.MAX_VALUE);
        checkBtn.setStyle("-fx-font-size: 14px;");
        
        checkBtn.setOnAction(e -> {
            checkBtn.setDisable(true);
            resultArea.clear();
            resultArea.appendText("=== Starting System Check ===\n");
            resultArea.appendText("Checking sensors and functions...\n\n");
            
            CompletableFuture.runAsync(() -> {
                try {
                    String projectDir = System.getProperty("user.dir");
                    if (projectDir.contains("ui")) {
                        projectDir = new java.io.File(projectDir).getParent();
                    }
                    
                    String[] pythonPaths = {"python3", "python"};
                    String pythonCmd = "python3";
                    for (String path : pythonPaths) {
                        try {
                            Process testProcess = new ProcessBuilder(path, "--version").start();
                            if (testProcess.waitFor() == 0) {
                                pythonCmd = path;
                                break;
                            }
                        } catch (Exception ignored) {}
                    }
                    
                    String scriptPathTemp = projectDir + "/check_system.py";
                    java.io.File scriptFile = new java.io.File(scriptPathTemp);
                    
                    if (!scriptFile.exists()) {
                        String altPath = "/home/pi/iot_project_OOP/check_system.py";
                        if (new java.io.File(altPath).exists()) {
                            scriptPathTemp = altPath;
                            projectDir = "/home/pi/iot_project_OOP";
                        }
                    }
                    
                    final String scriptPath = scriptPathTemp;
                    final String finalProjectDir = projectDir;
                    
                    if (!new java.io.File(scriptPath).exists()) {
                        Platform.runLater(() -> {
                            checkBtn.setDisable(false);
                            resultArea.appendText("[ERROR] Cannot find check_system.py file.\n");
                            resultArea.appendText("Path: " + scriptPath + "\n");
                        });
                        return;
                    }
                    
                    ProcessBuilder pb = new ProcessBuilder(pythonCmd, scriptPath);
                    pb.directory(new java.io.File(finalProjectDir));
                    Process process = pb.start();
                    
                    BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                    
                    StringBuilder jsonOutput = new StringBuilder();
                    String line;
                    
                    while ((line = stderrReader.readLine()) != null) {
                        final String logLine = line;
                        Platform.runLater(() -> {
                            resultArea.appendText(logLine + "\n");
                            resultArea.setScrollTop(Double.MAX_VALUE);
                        });
                    }
                    
                    while ((line = stdoutReader.readLine()) != null) {
                        jsonOutput.append(line).append("\n");
                    }
                    
                    int exitCode = process.waitFor();
                    
                    Platform.runLater(() -> {
                        checkBtn.setDisable(false);
                        
                        try {
                            ObjectMapper mapper = new ObjectMapper();
                            JsonNode results = mapper.readTree(jsonOutput.toString());
                            
                            resultArea.appendText("\n=== Check Results ===\n\n");
                            
                            if (results.has("checks")) {
                                JsonNode checks = results.get("checks");
                                
                                // Camera check
                                if (checks.has("camera")) {
                                    JsonNode camera = checks.get("camera");
                                String status = camera.get("status").asText();
                                String message = camera.get("message").asText();
                                String details = camera.has("details") ? camera.get("details").asText() : "";
                                String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                resultArea.appendText(String.format("%s Camera: %s\n   %s\n", statusIcon, message, details));
                                }
                                
                                // Accelerometer check
                                if (checks.has("accelerometer")) {
                                    JsonNode accel = checks.get("accelerometer");
                                String status = accel.get("status").asText();
                                String message = accel.get("message").asText();
                                String details = accel.has("details") ? accel.get("details").asText() : "";
                                String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                resultArea.appendText(String.format("%s Accelerometer: %s\n   %s\n", statusIcon, message, details));
                                }
                                
                                // GPS check
                                if (checks.has("gps")) {
                                    JsonNode gps = checks.get("gps");
                                String status = gps.get("status").asText();
                                String message = gps.get("message").asText();
                                String details = gps.has("details") ? gps.get("details").asText() : "";
                                String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                resultArea.appendText(String.format("%s GPS: %s\n   %s\n", statusIcon, message, details));
                                }
                                
                                // Speaker check
                                if (checks.has("speaker")) {
                                    JsonNode speaker = checks.get("speaker");
                                String status = speaker.get("status").asText();
                                String message = speaker.get("message").asText();
                                String details = speaker.has("details") ? speaker.get("details").asText() : "";
                                String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                resultArea.appendText(String.format("%s Speaker: %s\n   %s\n", statusIcon, message, details));
                                }
                                
                                // SMS check
                                if (checks.has("sms")) {
                                    JsonNode sms = checks.get("sms");
                                String status = sms.get("status").asText();
                                String message = sms.get("message").asText();
                                String details = sms.has("details") ? sms.get("details").asText() : "";
                                String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                resultArea.appendText(String.format("%s SMS (Auto Report): %s\n   %s\n", statusIcon, message, details));
                                }
                            }
                            
                            resultArea.appendText("\n=== Check Complete ===\n");
                            resultArea.setScrollTop(Double.MAX_VALUE);
                            
                            if (exitCode == 0) {
                                Alert alert = new Alert(Alert.AlertType.INFORMATION);
                                alert.setTitle("System Check Complete");
                                alert.setHeaderText("All checks completed.");
                                alert.setContentText("Please check the results.");
                                alert.showAndWait();
                            }
                        } catch (Exception parseEx) {
                            resultArea.appendText("\n[ERROR] Failed to parse results: " + parseEx.getMessage() + "\n");
                            resultArea.appendText("Original output:\n" + jsonOutput.toString() + "\n");
                        }
                    });
                } catch (Exception ex) {
                    Platform.runLater(() -> {
                        checkBtn.setDisable(false);
                        resultArea.appendText("[ERROR] " + ex.getMessage() + "\n");
                        ex.printStackTrace();
                    });
                }
            });
        });
        
        content.getChildren().addAll(backBtn, title, descriptionLabel, resultArea, checkBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
}

