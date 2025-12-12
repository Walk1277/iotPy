package org.example.iotprojectui.controllers;

import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.control.ScrollPane;
import org.example.iotprojectui.JsonDataLoader;
import com.fasterxml.jackson.databind.JsonNode;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.CompletableFuture;

/**
 * Controller for the log screen
 */
public class LogScreenController implements BaseScreenController {
    private Runnable onBack;
    
    public LogScreenController(Runnable onBack) {
        this.onBack = onBack;
    }
    
    @Override
    public void showScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("Log Check");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        TextArea logArea = new TextArea();
        logArea.setEditable(false);
        logArea.setPrefRowCount(15);
        logArea.setStyle("-fx-font-size: 11px;");
        loadLogs(logArea);
        
        HBox buttonBox = new HBox(10);
        buttonBox.setAlignment(Pos.CENTER);
        
        Button refreshBtn = new Button("Refresh");
        refreshBtn.setOnAction(e -> loadLogs(logArea));
        
        Button clearBtn = new Button("Clear Logs");
        clearBtn.setStyle("-fx-background-color: #d32f2f; -fx-text-fill: white;");
        clearBtn.setOnAction(e -> {
            Alert confirmAlert = new Alert(Alert.AlertType.CONFIRMATION);
            confirmAlert.setTitle("Clear Logs");
            confirmAlert.setHeaderText("Do you want to clear logs?");
            confirmAlert.setContentText("All driving event logs will be deleted and the score will be reset to 100.\nThis action cannot be undone.");
            
            confirmAlert.showAndWait().ifPresent(response -> {
                if (response == ButtonType.OK) {
                    clearBtn.setDisable(true);
                    refreshBtn.setDisable(true);
                    
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
                            StringBuilder output = new StringBuilder();
                            while ((line = reader.readLine()) != null) {
                                output.append(line).append("\n");
                                System.out.println("[Clear Logs] " + line);
                            }
                            
                            int exitCode = process.waitFor();
                            Platform.runLater(() -> {
                                clearBtn.setDisable(false);
                                refreshBtn.setDisable(false);
                                
                                if (exitCode == 0) {
                                    Alert successAlert = new Alert(Alert.AlertType.INFORMATION);
                                    successAlert.setTitle("Complete");
                                    successAlert.setHeaderText("Logs cleared.");
                                    successAlert.setContentText("All driving event logs have been deleted and the score has been reset to 100.");
                                    successAlert.showAndWait();
                                    loadLogs(logArea);
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
                                clearBtn.setDisable(false);
                                refreshBtn.setDisable(false);
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
        
        buttonBox.getChildren().addAll(refreshBtn, clearBtn);
        content.getChildren().addAll(backBtn, title, logArea, buttonBox);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
    
    public void loadLogs(TextArea logArea) {
        JsonNode logSummary = null;
        String[] paths = {
            "/home/pi/iot/data/log_summary.json",
            System.getProperty("user.dir") + "/../data/log_summary.json",
            System.getProperty("user.dir") + "/data/log_summary.json",
            "data/log_summary.json"
        };
        for (String path : paths) {
            logSummary = JsonDataLoader.load(path);
            if (logSummary != null) break;
        }
        
        StringBuilder logText = new StringBuilder();
        logText.append("=== System Logs ===\n\n");
        
        if (logSummary != null) {
            if (logSummary.has("monthly_score")) {
                logText.append("Monthly Score: ").append(logSummary.get("monthly_score").asInt()).append(" pts\n");
            }
            
            if (logSummary.has("event_counts")) {
                JsonNode events = logSummary.get("event_counts");
                logText.append("\nEvent Counts:\n");
                if (events.has("sudden_stop")) {
                    logText.append("  Sudden Stop: ").append(events.get("sudden_stop").asInt()).append(" times\n");
                }
                if (events.has("sudden_acceleration")) {
                    logText.append("  Sudden Acceleration: ").append(events.get("sudden_acceleration").asInt()).append(" times\n");
                }
                if (events.has("drowsiness")) {
                    logText.append("  Drowsiness: ").append(events.get("drowsiness").asInt()).append(" times\n");
                }
            }
            
            if (logSummary.has("report_stats")) {
                JsonNode reportStats = logSummary.get("report_stats");
                logText.append("\nAuto Report Statistics:\n");
                if (reportStats.has("alert_triggered")) {
                    logText.append("  Alerts Triggered: ").append(reportStats.get("alert_triggered").asInt()).append(" times\n");
                }
                if (reportStats.has("report_triggered")) {
                    logText.append("  Reports Triggered: ").append(reportStats.get("report_triggered").asInt()).append(" times\n");
                }
                if (reportStats.has("report_cancelled")) {
                    logText.append("  Reports Cancelled: ").append(reportStats.get("report_cancelled").asInt()).append(" times\n");
                }
                if (reportStats.has("sms_sent")) {
                    logText.append("  SMS Sent: ").append(reportStats.get("sms_sent").asInt()).append(" times\n");
                }
            }
        } else {
            logText.append("Unable to load log data.\n");
        }
        
        logArea.setText(logText.toString());
    }
}

