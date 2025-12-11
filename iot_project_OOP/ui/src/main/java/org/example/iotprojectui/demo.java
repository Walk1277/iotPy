package org.example.iotprojectui;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.BarChart;
import javafx.scene.chart.CategoryAxis;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.stage.Stage;
import javafx.util.Duration;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.CompletableFuture;

public class demo extends Application {

    // Main container
    private BorderPane root;
    private StackPane mainContainer;
    
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
    
    // Timeline for updating data from Python backend
    private Timeline updateTimeline;
    
    @Override
    public void start(Stage primaryStage) {
        root = new BorderPane();
        mainContainer = new StackPane();
        
        // Create main screen
        GridPane mainScreen = createMainScreen();
        mainContainer.getChildren().add(mainScreen);
        
        root.setCenter(mainContainer);
        
        Scene scene = new Scene(root, 800, 480);
        primaryStage.setTitle("Smart Accident Prevention Kit");
        primaryStage.setScene(scene);
        primaryStage.setResizable(false);
        primaryStage.show();
        
        // Start updating data from Python backend every second
        updateTimeline = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
            updateFromBackend();
        }));
        updateTimeline.setCycleCount(Timeline.INDEFINITE);
        updateTimeline.play();
    }
    
    /** Create main screen with 2x2 grid layout */
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
    
    /** Top-Left: Current Status Panel */
    private VBox createCurrentStatusPanel() {
        VBox panel = new VBox(10);
        panel.setPadding(new Insets(15));
        panel.setStyle("-fx-background-color: #e8f5e9; -fx-border-color: #4caf50; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setAlignment(Pos.CENTER);
        
        Label title = new Label("현재 상태");
        title.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        currentStatusLabel = new Label("Good");
        currentStatusLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #2e7d32;");
        
        currentStatusSubLabel = new Label("현재 상태를 유지하세요");
        currentStatusSubLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #2e7d32;");
        
        panel.getChildren().addAll(title, currentStatusLabel, currentStatusSubLabel);
        
        // Make clickable - navigate to detailed status screen
        panel.setOnMouseClicked(e -> showDetailedStatusScreen());
        panel.setStyle(panel.getStyle() + " -fx-cursor: hand;");
        
        return panel;
    }
    
    /** Top-Right: Driving Score Panel */
    private VBox createDrivingScorePanel() {
        VBox panel = new VBox(10);
        panel.setPadding(new Insets(15));
        panel.setStyle("-fx-background-color: #fff3e0; -fx-border-color: #ff9800; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setAlignment(Pos.CENTER);
        
        Label title = new Label("운전 점수");
        title.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        drivingScoreLabel = new Label("87점");
        drivingScoreLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #e65100;");
        
        panel.getChildren().addAll(title, drivingScoreLabel);
        
        // Make clickable - navigate to detailed report screen
        panel.setOnMouseClicked(e -> showDetailedReportScreen());
        panel.setStyle(panel.getStyle() + " -fx-cursor: hand;");
        
        return panel;
    }
    
    /** Bottom-Left: Accident Detection Panel */
    private VBox createAccidentDetectionPanel() {
        VBox panel = new VBox(10);
        panel.setPadding(new Insets(15));
        panel.setStyle("-fx-background-color: #e3f2fd; -fx-border-color: #2196f3; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setAlignment(Pos.CENTER);
        
        Label title = new Label("사고 감지");
        title.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        accidentStatusLabel = new Label("사고 감지 안됨");
        accidentStatusLabel.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: #1976d2;");
        
        gSensorLabel = new Label("G-sensor: 1.0G");
        gSensorLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #1976d2;");
        
        panel.getChildren().addAll(title, accidentStatusLabel, gSensorLabel);
        
        // Make clickable - navigate to detailed accident screen
        panel.setOnMouseClicked(e -> showDetailedAccidentScreen());
        panel.setStyle(panel.getStyle() + " -fx-cursor: hand;");
        
        return panel;
    }
    
    /** Bottom-Right-Left: Settings Panel */
    private VBox createSettingsPanel() {
        VBox panel = new VBox(6);
        panel.setPadding(new Insets(8));
        panel.setStyle("-fx-background-color: #f3e5f5; -fx-border-color: #9c27b0; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setPrefWidth(190); // Fixed width to prevent cutting
        
        Label title = new Label("설정");
        title.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
        
        Button updateBtn = new Button("업데이트");
        updateBtn.setPrefWidth(Double.MAX_VALUE);
        updateBtn.setPrefHeight(30);
        updateBtn.setStyle("-fx-font-size: 11px;");
        updateBtn.setOnAction(e -> showUpdateScreen());
        
        Button personalSettingsBtn = new Button("개인설정");
        personalSettingsBtn.setPrefWidth(Double.MAX_VALUE);
        personalSettingsBtn.setPrefHeight(30);
        personalSettingsBtn.setStyle("-fx-font-size: 11px;");
        personalSettingsBtn.setOnAction(e -> showPersonalSettingsScreen());
        
        Button drowsinessSettingsBtn = new Button("졸음 감지설정");
        drowsinessSettingsBtn.setPrefWidth(Double.MAX_VALUE);
        drowsinessSettingsBtn.setPrefHeight(30);
        drowsinessSettingsBtn.setStyle("-fx-font-size: 11px;");
        drowsinessSettingsBtn.setOnAction(e -> showDrowsinessSettingsScreen());
        
        panel.getChildren().addAll(title, updateBtn, personalSettingsBtn, drowsinessSettingsBtn);
        
        return panel;
    }
    
    /** Bottom-Right-Right: Log Check Panel */
    private VBox createLogCheckPanel() {
        VBox panel = new VBox(6);
        panel.setPadding(new Insets(8));
        panel.setStyle("-fx-background-color: #eceff1; -fx-border-color: #607d8b; -fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;");
        panel.setPrefWidth(190); // Fixed width to prevent cutting
        
        Label title = new Label("로그 확인");
        title.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
        
        TextArea logArea = new TextArea();
        logArea.setEditable(false);
        logArea.setPrefRowCount(5); // Reduced from 8 to fit better
        logArea.setPrefHeight(120); // Fixed height
        logArea.setStyle("-fx-font-size: 9px;");
        logArea.setText("로그 로딩 중...\n");
        
        // Load logs initially
        loadLogs(logArea);
        
        Button refreshBtn = new Button("새로고침");
        refreshBtn.setPrefWidth(Double.MAX_VALUE);
        refreshBtn.setPrefHeight(25);
        refreshBtn.setStyle("-fx-font-size: 10px;");
        refreshBtn.setOnAction(e -> {
            loadLogs(logArea);
        });
        
        panel.getChildren().addAll(title, logArea, refreshBtn);
        
        // Make panel clickable - navigate to detailed log screen
        panel.setOnMouseClicked(e -> {
            // Only navigate if not clicking on the button or text area
            if (e.getTarget() != refreshBtn && e.getTarget() != logArea) {
                showDetailedLogScreen();
            }
        });
        panel.setStyle(panel.getStyle() + " -fx-cursor: hand;");
        
        return panel;
    }
    
    /** Update data from backend */
    private void updateFromBackend() {
        // Update status from status.json
        com.fasterxml.jackson.databind.JsonNode statusJson = StatusDataLoader.load();
        if (statusJson != null) {
            Platform.runLater(() -> {
                try {
                    // Update current status
                    if (currentStatusLabel != null) {
                        // Check drowsiness status
                        com.fasterxml.jackson.databind.JsonNode drowsinessJson = null;
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
                        
                        if (drowsinessJson != null) {
                            String state = drowsinessJson.has("state") ? drowsinessJson.get("state").asText() : "unknown";
                            boolean alarmOn = drowsinessJson.has("alarm_on") ? drowsinessJson.get("alarm_on").asBoolean() : false;
                            
                            if (state.equals("sleepy") || alarmOn) {
                                currentStatusLabel.setText("Alert");
                                currentStatusLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #d32f2f;");
                                if (currentStatusSubLabel != null) {
                                    currentStatusSubLabel.setText("졸음이 감지되었습니다!");
                                    currentStatusSubLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #d32f2f;");
                                }
                            } else if (state.equals("normal")) {
                                currentStatusLabel.setText("Good");
                                currentStatusLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #2e7d32;");
                                if (currentStatusSubLabel != null) {
                                    currentStatusSubLabel.setText("현재 상태를 유지하세요");
                                    currentStatusSubLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #2e7d32;");
                                }
                            } else {
                                currentStatusLabel.setText("Waiting");
                                currentStatusLabel.setStyle("-fx-font-size: 48px; -fx-font-weight: bold; -fx-text-fill: #757575;");
                                if (currentStatusSubLabel != null) {
                                    currentStatusSubLabel.setText("카메라를 확인 중...");
                                    currentStatusSubLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #757575;");
                                }
                            }
                        }
                    }
                    
                    // Update driving score
                    if (drivingScoreLabel != null) {
                        com.fasterxml.jackson.databind.JsonNode logSummary = null;
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
                        
                        if (logSummary != null && logSummary.has("monthly_score")) {
                            int score = logSummary.get("monthly_score").asInt();
                            drivingScoreLabel.setText(score + "점");
                        }
                    }
                    
                    // Update accident detection
                    if (accidentStatusLabel != null && gSensorLabel != null) {
                        double gValue = statusJson.has("accel_magnitude") ? statusJson.get("accel_magnitude").asDouble() : 1.0;
                        boolean impactDetected = statusJson.has("impact_detected") && statusJson.get("impact_detected").asBoolean();
                        
                        gSensorLabel.setText(String.format("G-sensor: %.1fG", gValue));
                        
                        if (impactDetected) {
                            accidentStatusLabel.setText("사고 감지됨!");
                            accidentStatusLabel.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: #d32f2f;");
                        } else {
                            accidentStatusLabel.setText("사고 감지 안됨");
                            accidentStatusLabel.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: #1976d2;");
                        }
                    }
                } catch (Exception e) {
                    System.err.println("[ERROR] Failed to update: " + e.getMessage());
                }
            });
        }
    }
    
    /** Show detailed status screen */
    private void showDetailedStatusScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        // Back button
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("현재 상태 상세");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        // Load and display detailed status
        com.fasterxml.jackson.databind.JsonNode statusJson = StatusDataLoader.load();
        com.fasterxml.jackson.databind.JsonNode drowsinessJson = null;
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
            Label stateLabel = new Label("상태: " + (state.equals("sleepy") ? "졸음" : state.equals("normal") ? "정상" : "대기"));
            stateLabel.setStyle("-fx-font-size: 14px;");
            
            statusInfo.getChildren().addAll(earLabel, stateLabel);
        }
        
        if (statusJson != null) {
            Label sensorLabel = new Label("센서 상태: " + (statusJson.has("sensor_status") ? statusJson.get("sensor_status").asText() : "-"));
            sensorLabel.setStyle("-fx-font-size: 14px;");
            statusInfo.getChildren().add(sensorLabel);
        }
        
        content.getChildren().addAll(backBtn, title, statusInfo);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        mainContainer.getChildren().clear();
        mainContainer.getChildren().add(detailScreen);
    }
    
    /** Show detailed report screen */
    private void showDetailedReportScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("운전 리포트");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        // Load and display report data
        com.fasterxml.jackson.databind.JsonNode logSummary = null;
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
        
        VBox reportInfo = new VBox(10);
        if (logSummary != null) {
            if (logSummary.has("monthly_score")) {
                Label scoreLabel = new Label("월간 점수: " + logSummary.get("monthly_score").asInt() + "점");
                scoreLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
                reportInfo.getChildren().add(scoreLabel);
            }
            
            // Daily Safety Score Chart
            CategoryAxis xAxisLine = new CategoryAxis();
            xAxisLine.setLabel("일");
            xAxisLine.setTickLabelFont(javafx.scene.text.Font.font(9));
            NumberAxis yAxisLine = new NumberAxis(0, 100, 20);
            yAxisLine.setLabel("점수");
            yAxisLine.setTickLabelFont(javafx.scene.text.Font.font(9));
            
            LineChart<String, Number> lineChart = new LineChart<>(xAxisLine, yAxisLine);
            lineChart.setTitle("일별 안전 점수");
            lineChart.setPrefHeight(200);
            lineChart.setLegendVisible(false);
            lineChart.setStyle("-fx-font-size: 9px;");
            
            XYChart.Series<String, Number> scoreSeries = new XYChart.Series<>();
            if (logSummary.has("daily_scores")) {
                com.fasterxml.jackson.databind.JsonNode dailyScores = logSummary.get("daily_scores");
                for (com.fasterxml.jackson.databind.JsonNode score : dailyScores) {
                    int day = score.has("day") ? score.get("day").asInt() : 0;
                    int scoreValue = score.has("score") ? score.get("score").asInt() : 0;
                    scoreSeries.getData().add(new XYChart.Data<>(day + "일", scoreValue));
                }
            }
            lineChart.getData().add(scoreSeries);
            
            // Event Count Bar Chart
            CategoryAxis xAxisBar = new CategoryAxis();
            xAxisBar.setLabel("이벤트");
            xAxisBar.setTickLabelFont(javafx.scene.text.Font.font(9));
            NumberAxis yAxisBar = new NumberAxis();
            yAxisBar.setLabel("횟수");
            yAxisBar.setTickLabelFont(javafx.scene.text.Font.font(9));
            
            BarChart<String, Number> barChart = new BarChart<>(xAxisBar, yAxisBar);
            barChart.setTitle("이벤트 타입별 횟수");
            barChart.setPrefHeight(200);
            barChart.setLegendVisible(false);
            barChart.setStyle("-fx-font-size: 9px;");
            
            XYChart.Series<String, Number> eventSeries = new XYChart.Series<>();
            if (logSummary.has("event_counts")) {
                com.fasterxml.jackson.databind.JsonNode events = logSummary.get("event_counts");
                if (events.has("sudden_stop")) {
                    eventSeries.getData().add(new XYChart.Data<>("급정거", events.get("sudden_stop").asInt()));
                }
                if (events.has("sudden_acceleration")) {
                    eventSeries.getData().add(new XYChart.Data<>("급가속", events.get("sudden_acceleration").asInt()));
                }
                if (events.has("drowsiness")) {
                    eventSeries.getData().add(new XYChart.Data<>("졸음", events.get("drowsiness").asInt()));
                }
            }
            barChart.getData().add(eventSeries);
            
            // Event counts text
            if (logSummary.has("event_counts")) {
                com.fasterxml.jackson.databind.JsonNode events = logSummary.get("event_counts");
                Label eventsLabel = new Label("이벤트 상세:");
                eventsLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
                reportInfo.getChildren().add(eventsLabel);
                
                if (events.has("sudden_stop")) {
                    Label stopLabel = new Label("  급정거: " + events.get("sudden_stop").asInt() + "회");
                    stopLabel.setStyle("-fx-font-size: 12px;");
                    reportInfo.getChildren().add(stopLabel);
                }
                if (events.has("sudden_acceleration")) {
                    Label accelLabel = new Label("  급가속: " + events.get("sudden_acceleration").asInt() + "회");
                    accelLabel.setStyle("-fx-font-size: 12px;");
                    reportInfo.getChildren().add(accelLabel);
                }
                if (events.has("drowsiness")) {
                    Label drowsyLabel = new Label("  졸음: " + events.get("drowsiness").asInt() + "회");
                    drowsyLabel.setStyle("-fx-font-size: 12px;");
                    reportInfo.getChildren().add(drowsyLabel);
                }
            }
            
            // Add charts
            VBox chartBox = new VBox(10, lineChart, barChart);
            reportInfo.getChildren().add(chartBox);
        }
        
        content.getChildren().addAll(backBtn, title, reportInfo);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        mainContainer.getChildren().clear();
        mainContainer.getChildren().add(detailScreen);
    }
    
    /** Show detailed accident screen */
    private void showDetailedAccidentScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("사고 감지 상세");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        com.fasterxml.jackson.databind.JsonNode statusJson = StatusDataLoader.load();
        VBox accidentInfo = new VBox(10);
        
        if (statusJson != null) {
            double gValue = statusJson.has("accel_magnitude") ? statusJson.get("accel_magnitude").asDouble() : 1.0;
            boolean impactDetected = statusJson.has("impact_detected") && statusJson.get("impact_detected").asBoolean();
            String gpsPos = statusJson.has("gps_position_string") ? statusJson.get("gps_position_string").asText() : "(-, -)";
            
            Label gLabel = new Label("G-Sensor: " + String.format("%.2fG", gValue));
            gLabel.setStyle("-fx-font-size: 14px;");
            
            Label impactLabel = new Label("충격 감지: " + (impactDetected ? "감지됨" : "없음"));
            impactLabel.setStyle("-fx-font-size: 14px;");
            
            Label gpsLabel = new Label("GPS 위치: " + gpsPos);
            gpsLabel.setStyle("-fx-font-size: 14px;");
            
            accidentInfo.getChildren().addAll(gLabel, impactLabel, gpsLabel);
        }
        
        Button testBtn = new Button("사고 감지 테스트");
        testBtn.setOnAction(e -> {
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle("사고 감지");
            alert.setHeaderText("사고가 감지되었습니다!");
            alert.setContentText("10초 내 화면을 터치하여 신고를 취소하세요.");
            alert.showAndWait();
        });
        
        content.getChildren().addAll(backBtn, title, accidentInfo, testBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        mainContainer.getChildren().clear();
        mainContainer.getChildren().add(detailScreen);
    }
    
    /** Show update screen */
    private void showUpdateScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("소프트웨어 업데이트");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        Label currentVersion = new Label("현재 버전: v1.0.0");
        currentVersion.setStyle("-fx-font-size: 14px;");
        
        Label latestVersion = new Label("최신 버전: 확인 필요");
        latestVersion.setStyle("-fx-font-size: 14px;");
        
        TextArea updateLogArea = new TextArea();
        updateLogArea.setEditable(false);
        updateLogArea.setPrefRowCount(8);
        updateLogArea.setStyle("-fx-font-size: 10px;");
        updateLogArea.setText("업데이트 로그가 여기에 표시됩니다...\n");
        
        Button checkBtn = new Button("업데이트 확인");
        checkBtn.setOnAction(e -> {
            checkBtn.setDisable(true);
            updateLogArea.appendText("[INFO] GitHub에서 최신 버전 확인 중...\n");
            
            CompletableFuture.runAsync(() -> {
                try {
                    // Get project directory (handle both development and Raspberry Pi)
                    String projectDir = System.getProperty("user.dir");
                    if (projectDir.contains("ui")) {
                        projectDir = new java.io.File(projectDir).getParent();
                    }
                    
                    String scriptPath = projectDir + "/check_update.sh";
                    java.io.File scriptFile = new java.io.File(scriptPath);
                    
                    // Try alternative paths for Raspberry Pi
                    if (!scriptFile.exists()) {
                        String altPath = "/home/pi/iot_project_OOP/check_update.sh";
                        if (new java.io.File(altPath).exists()) {
                            scriptPath = altPath;
                            projectDir = "/home/pi/iot_project_OOP";
                        }
                    }
                    
                    ProcessBuilder pb = new ProcessBuilder("bash", scriptPath);
                    pb.directory(new java.io.File(projectDir));
                    Process process = pb.start();
                    
                    BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    String result = reader.readLine();
                    int exitCode = process.waitFor();
                    
                    Platform.runLater(() -> {
                        checkBtn.setDisable(false);
                        if (exitCode == 0 && result != null) {
                            if (result.startsWith("UPDATE_AVAILABLE:")) {
                                String version = result.split(":")[1];
                                latestVersion.setText("최신 버전: " + version + " (업데이트 필요)");
                                latestVersion.setStyle("-fx-font-size: 14px; -fx-text-fill: #d32f2f;");
                                updateLogArea.appendText("[INFO] 새 버전 발견: " + version + "\n");
                            } else {
                                String version = result.split(":")[1];
                                latestVersion.setText("최신 버전: " + version + " (최신 상태)");
                                latestVersion.setStyle("-fx-font-size: 14px; -fx-text-fill: #2e7d32;");
                                updateLogArea.appendText("[INFO] 최신 버전입니다.\n");
                            }
                        } else {
                            updateLogArea.appendText("[ERROR] 버전 확인 실패\n");
                        }
                    });
                } catch (Exception ex) {
                    Platform.runLater(() -> {
                        checkBtn.setDisable(false);
                        updateLogArea.appendText("[ERROR] " + ex.getMessage() + "\n");
                    });
                }
            });
        });
        
        Button updateBtn = new Button("업데이트 실행");
        updateBtn.setOnAction(e -> {
            updateBtn.setDisable(true);
            updateLogArea.appendText("[INFO] 시스템 업데이트 시작...\n");
            
            CompletableFuture.runAsync(() -> {
                try {
                    // Get project directory (handle both development and Raspberry Pi)
                    String projectDir = System.getProperty("user.dir");
                    if (projectDir.contains("ui")) {
                        projectDir = new java.io.File(projectDir).getParent();
                    }
                    
                    String scriptPath = projectDir + "/update_system.sh";
                    java.io.File scriptFile = new java.io.File(scriptPath);
                    
                    // Try alternative paths for Raspberry Pi
                    if (!scriptFile.exists()) {
                        String altPath = "/home/pi/iot_project_OOP/update_system.sh";
                        if (new java.io.File(altPath).exists()) {
                            scriptPath = altPath;
                            projectDir = "/home/pi/iot_project_OOP";
                        }
                    }
                    
                    ProcessBuilder pb = new ProcessBuilder("bash", scriptPath);
                    pb.directory(new java.io.File(projectDir));
                    Process process = pb.start();
                    
                    BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    String line;
                    while ((line = reader.readLine()) != null) {
                        final String logLine = line;
                        Platform.runLater(() -> {
                            updateLogArea.appendText(logLine + "\n");
                        });
                    }
                    
                    int exitCode = process.waitFor();
                    Platform.runLater(() -> {
                        updateBtn.setDisable(false);
                        if (exitCode == 0) {
                            updateLogArea.appendText("[INFO] 업데이트 완료!\n");
                            Alert alert = new Alert(Alert.AlertType.INFORMATION);
                            alert.setTitle("업데이트");
                            alert.setHeaderText("업데이트가 완료되었습니다.");
                            alert.setContentText("시스템을 재시작하는 것을 권장합니다.");
                            alert.showAndWait();
                        } else {
                            updateLogArea.appendText("[ERROR] 업데이트 실패\n");
                            Alert alert = new Alert(Alert.AlertType.ERROR);
                            alert.setTitle("오류");
                            alert.setHeaderText("업데이트 실패");
                            alert.setContentText("업데이트 로그를 확인하세요.");
                            alert.showAndWait();
                        }
                    });
                } catch (Exception ex) {
                    Platform.runLater(() -> {
                        updateBtn.setDisable(false);
                        updateLogArea.appendText("[ERROR] " + ex.getMessage() + "\n");
                    });
                }
            });
        });
        
        content.getChildren().addAll(backBtn, title, currentVersion, latestVersion, checkBtn, updateBtn, updateLogArea);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        mainContainer.getChildren().clear();
        mainContainer.getChildren().add(detailScreen);
    }
    
    /** Show personal settings screen */
    private void showPersonalSettingsScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("개인 설정");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        Label nameLabel = new Label("이름:");
        TextField nameField = new TextField("사용자");
        
        Label phoneLabel = new Label("전화번호:");
        TextField phoneField = new TextField("010-0000-0000");
        
        Button saveBtn = new Button("저장");
        saveBtn.setOnAction(e -> {
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle("저장");
            alert.setHeaderText("설정이 저장되었습니다.");
            alert.showAndWait();
        });
        
        content.getChildren().addAll(backBtn, title, nameLabel, nameField, phoneLabel, phoneField, saveBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        mainContainer.getChildren().clear();
        mainContainer.getChildren().add(detailScreen);
    }
    
    /** Show drowsiness settings screen */
    private void showDrowsinessSettingsScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("졸음 감지 설정");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        Label thresholdLabel = new Label("임계값: 0.22");
        thresholdLabel.setStyle("-fx-font-size: 14px;");
        
        Slider thresholdSlider = new Slider(0.1, 0.4, 0.22);
        thresholdSlider.setShowTickLabels(true);
        thresholdSlider.setShowTickMarks(true);
        thresholdSlider.setMajorTickUnit(0.05);
        thresholdSlider.valueProperty().addListener((obs, o, n) ->
            thresholdLabel.setText("임계값: " + String.format("%.2f", n.doubleValue()))
        );
        
        CheckBox alarmCheck = new CheckBox("알람 활성화");
        alarmCheck.setSelected(true);
        
        Button saveBtn = new Button("저장");
        saveBtn.setOnAction(e -> {
            // Save threshold to config.py
            double thresholdValue = thresholdSlider.getValue();
            boolean alarmEnabled = alarmCheck.isSelected();
            
            // Run Python script to update config
            CompletableFuture.runAsync(() -> {
                try {
                    // Get project directory (handle both development and Raspberry Pi)
                    String projectDir = System.getProperty("user.dir");
                    if (projectDir.contains("ui")) {
                        projectDir = new java.io.File(projectDir).getParent();
                    }
                    
                    // Try multiple Python paths for compatibility
                    String[] pythonPaths = {"python3", "python"};
                    String pythonCmd = "python3"; // Default
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
                    
                    // Try alternative paths for Raspberry Pi
                    if (!scriptFile.exists()) {
                        // Try absolute path for Raspberry Pi
                        String altPath = "/home/pi/iot_project_OOP/update_config.py";
                        if (new java.io.File(altPath).exists()) {
                            scriptPath = altPath;
                            projectDir = "/home/pi/iot_project_OOP";
                        }
                    }
                    
                    ProcessBuilder pb = new ProcessBuilder(
                        pythonCmd,
                        scriptPath,
                        "EAR_THRESHOLD",
                        String.valueOf(thresholdValue)
                    );
                    pb.directory(new java.io.File(projectDir));
                    Process process = pb.start();
                    
                    BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.out.println("[Config Update] " + line);
                    }
                    
                    int exitCode = process.waitFor();
                    Platform.runLater(() -> {
                        if (exitCode == 0) {
                            Alert alert = new Alert(Alert.AlertType.INFORMATION);
                            alert.setTitle("저장");
                            alert.setHeaderText("설정이 저장되었습니다.");
                            alert.setContentText(String.format("임계값: %.2f\n알람 활성화: %s", thresholdValue, alarmEnabled ? "예" : "아니오"));
                            alert.showAndWait();
                        } else {
                            Alert alert = new Alert(Alert.AlertType.ERROR);
                            alert.setTitle("오류");
                            alert.setHeaderText("설정 저장 실패");
                            alert.setContentText("config.py 업데이트에 실패했습니다.");
                            alert.showAndWait();
                        }
                    });
                } catch (Exception ex) {
                    Platform.runLater(() -> {
                        Alert alert = new Alert(Alert.AlertType.ERROR);
                        alert.setTitle("오류");
                        alert.setHeaderText("설정 저장 실패");
                        alert.setContentText("오류: " + ex.getMessage());
                        alert.showAndWait();
                    });
                }
            });
        });
        
        content.getChildren().addAll(backBtn, title, thresholdLabel, thresholdSlider, alarmCheck, saveBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        mainContainer.getChildren().clear();
        mainContainer.getChildren().add(detailScreen);
    }
    
    /** Show detailed log screen */
    private void showDetailedLogScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("로그 확인");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        TextArea logArea = new TextArea();
        logArea.setEditable(false);
        logArea.setPrefRowCount(15);
        logArea.setStyle("-fx-font-size: 11px;");
        loadLogs(logArea);
        
        Button refreshBtn = new Button("새로고침");
        refreshBtn.setOnAction(e -> loadLogs(logArea));
        
        content.getChildren().addAll(backBtn, title, logArea, refreshBtn);
        detailScreen.setContent(content);
        detailScreen.setFitToWidth(true);
        
        mainContainer.getChildren().clear();
        mainContainer.getChildren().add(detailScreen);
    }
    
    /** Load logs into text area */
    private void loadLogs(TextArea logArea) {
        // Load log summary
        com.fasterxml.jackson.databind.JsonNode logSummary = null;
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
        logText.append("=== 시스템 로그 ===\n\n");
        
        if (logSummary != null) {
            if (logSummary.has("monthly_score")) {
                logText.append("월간 점수: ").append(logSummary.get("monthly_score").asInt()).append("점\n");
            }
            
            if (logSummary.has("event_counts")) {
                com.fasterxml.jackson.databind.JsonNode events = logSummary.get("event_counts");
                logText.append("\n이벤트 카운트:\n");
                if (events.has("sudden_stop")) {
                    logText.append("  급정거: ").append(events.get("sudden_stop").asInt()).append("회\n");
                }
                if (events.has("sudden_acceleration")) {
                    logText.append("  급가속: ").append(events.get("sudden_acceleration").asInt()).append("회\n");
                }
                if (events.has("drowsiness")) {
                    logText.append("  졸음: ").append(events.get("drowsiness").asInt()).append("회\n");
                }
            }
        } else {
            logText.append("로그 데이터를 불러올 수 없습니다.\n");
        }
        
        logArea.setText(logText.toString());
    }

    public static void main(String[] args) {
        launch();
    }
}
