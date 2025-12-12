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
        
        Button autoReportSettingsBtn = new Button("자동 신고설정");
        autoReportSettingsBtn.setPrefWidth(Double.MAX_VALUE);
        autoReportSettingsBtn.setPrefHeight(30);
        autoReportSettingsBtn.setStyle("-fx-font-size: 11px;");
        autoReportSettingsBtn.setOnAction(e -> showAutoReportSettingsScreen());
        
        Button systemCheckBtn = new Button("시스템 체크");
        systemCheckBtn.setPrefWidth(Double.MAX_VALUE);
        systemCheckBtn.setPrefHeight(30);
        systemCheckBtn.setStyle("-fx-font-size: 11px;");
        systemCheckBtn.setOnAction(e -> showSystemCheckScreen());
        
        panel.getChildren().addAll(title, updateBtn, personalSettingsBtn, drowsinessSettingsBtn, autoReportSettingsBtn, systemCheckBtn);
        
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
        
        Label descriptionLabel = new Label("requirements.txt에 있는 Python 패키지들을 최신 버전으로 업데이트합니다.");
        descriptionLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #666;");
        descriptionLabel.setWrapText(true);
        
        TextArea updateLogArea = new TextArea();
        updateLogArea.setEditable(false);
        updateLogArea.setPrefRowCount(15);
        updateLogArea.setStyle("-fx-font-size: 10px;");
        updateLogArea.setText("업데이트 로그가 여기에 표시됩니다...\n\n");
        
        Button updateBtn = new Button("패키지 업데이트 실행");
        updateBtn.setPrefWidth(Double.MAX_VALUE);
        updateBtn.setStyle("-fx-font-size: 14px;");
        updateBtn.setOnAction(e -> {
            updateBtn.setDisable(true);
            updateLogArea.clear();
            updateLogArea.appendText("=== Python 패키지 업데이트 시작 ===\n");
            updateLogArea.appendText("requirements.txt에 있는 패키지들을 최신 버전으로 업데이트합니다.\n\n");
            
            CompletableFuture.runAsync(() -> {
                try {
                    // Get project directory (handle both development and Raspberry Pi)
                    String projectDir = System.getProperty("user.dir");
                    if (projectDir.contains("ui")) {
                        projectDir = new java.io.File(projectDir).getParent();
                    }
                    
                    String scriptPathTemp = projectDir + "/update_system.sh";
                    java.io.File scriptFile = new java.io.File(scriptPathTemp);
                    
                    // Try alternative paths for Raspberry Pi
                    if (!scriptFile.exists()) {
                        String altPath = "/home/pi/iot_project_OOP/update_system.sh";
                        if (new java.io.File(altPath).exists()) {
                            scriptPathTemp = altPath;
                            projectDir = "/home/pi/iot_project_OOP";
                        }
                    }
                    
                    final String scriptPath = scriptPathTemp;
                    
                    // Check if script exists
                    if (!new java.io.File(scriptPath).exists()) {
                        Platform.runLater(() -> {
                            updateBtn.setDisable(false);
                            updateLogArea.appendText("[ERROR] update_system.sh 파일을 찾을 수 없습니다.\n");
                            updateLogArea.appendText("경로: " + scriptPath + "\n");
                            Alert alert = new Alert(Alert.AlertType.ERROR);
                            alert.setTitle("오류");
                            alert.setHeaderText("스크립트 파일을 찾을 수 없습니다");
                            alert.setContentText("update_system.sh 파일이 존재하는지 확인하세요.");
                            alert.showAndWait();
                        });
                        return;
                    }
                    
                    // Make script executable
                    try {
                        java.io.File scriptFileObj = new java.io.File(scriptPath);
                        scriptFileObj.setExecutable(true);
                    } catch (Exception ignored) {}
                    
                    ProcessBuilder pb = new ProcessBuilder("bash", scriptPath);
                    pb.directory(new java.io.File(projectDir));
                    Process process = pb.start();
                    
                    // Read both stdout and stderr
                    BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                    
                    // Read stdout
                    String line;
                    while ((line = stdoutReader.readLine()) != null) {
                        final String logLine = line;
                        Platform.runLater(() -> {
                            updateLogArea.appendText(logLine + "\n");
                            // Auto-scroll to bottom
                            updateLogArea.setScrollTop(Double.MAX_VALUE);
                        });
                    }
                    
                    // Read stderr
                    while ((line = stderrReader.readLine()) != null) {
                        final String logLine = "[ERROR] " + line;
                        Platform.runLater(() -> {
                            updateLogArea.appendText(logLine + "\n");
                            updateLogArea.setScrollTop(Double.MAX_VALUE);
                        });
                    }
                    
                    int exitCode = process.waitFor();
                    
                    // Also read update.log file if it exists
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
                            updateLogArea.appendText("\n=== 업데이트 완료 ===\n");
                            Alert alert = new Alert(Alert.AlertType.INFORMATION);
                            alert.setTitle("업데이트 완료");
                            alert.setHeaderText("Python 패키지 업데이트가 완료되었습니다.");
                            alert.setContentText("변경사항을 적용하려면 백엔드를 재시작하는 것을 권장합니다.");
                            alert.showAndWait();
                        } else {
                            updateLogArea.appendText("\n=== 업데이트 실패 (종료 코드: " + exitCode + ") ===\n");
                            Alert alert = new Alert(Alert.AlertType.ERROR);
                            alert.setTitle("업데이트 실패");
                            alert.setHeaderText("업데이트 중 오류가 발생했습니다.");
                            alert.setContentText("위의 로그를 확인하여 문제를 해결하세요.");
                            alert.showAndWait();
                        }
                    });
                } catch (Exception ex) {
                    Platform.runLater(() -> {
                        updateBtn.setDisable(false);
                        updateLogArea.appendText("[ERROR] " + ex.getMessage() + "\n");
                        ex.printStackTrace();
                        Alert alert = new Alert(Alert.AlertType.ERROR);
                        alert.setTitle("오류");
                        alert.setHeaderText("업데이트 실행 실패");
                        alert.setContentText("오류: " + ex.getMessage());
                        alert.showAndWait();
                    });
                }
            });
        });
        
        content.getChildren().addAll(backBtn, title, descriptionLabel, updateLogArea, updateBtn);
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
            // Save threshold settings to config.py
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
                    
                    // Update EAR_THRESHOLD
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
                            alert.setTitle("저장");
                            alert.setHeaderText("설정이 저장되었습니다.");
                            alert.setContentText(String.format("임계값: %.2f\n알람 활성화: %s", 
                                thresholdValue, alarmEnabled ? "예" : "아니오"));
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
    
    /** Show auto report settings screen */
    private void showAutoReportSettingsScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("자동 신고 설정");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        // Auto report enable/disable
        CheckBox autoReportCheck = new CheckBox("자동 신고 활성화");
        autoReportCheck.setSelected(true);
        
        Separator separator1 = new Separator();
        
        // Phone number settings
        Label fromPhoneLabel = new Label("송신 전화번호:");
        fromPhoneLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
        TextField fromPhoneField = new TextField("010-7220-5917");
        fromPhoneField.setPromptText("예: 010-1234-5678");
        
        Label toPhoneLabel = new Label("수신 전화번호:");
        toPhoneLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
        TextField toPhoneField = new TextField("010-4090-7445");
        toPhoneField.setPromptText("예: 010-1234-5678");
        
        Separator separator2 = new Separator();
        
        // System log clear button
        Label systemLabel = new Label("시스템 관리");
        systemLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
        
        Button clearLogsBtn = new Button("시스템 로그 초기화");
        clearLogsBtn.setStyle("-fx-background-color: #d32f2f; -fx-text-fill: white; -fx-font-size: 14px;");
        clearLogsBtn.setPrefWidth(Double.MAX_VALUE);
        clearLogsBtn.setOnAction(e -> {
            Alert confirmAlert = new Alert(Alert.AlertType.CONFIRMATION);
            confirmAlert.setTitle("로그 초기화");
            confirmAlert.setHeaderText("로그를 초기화하시겠습니까?");
            confirmAlert.setContentText("모든 운전 이벤트 로그가 삭제되고 점수가 100점으로 초기화됩니다.\n이 작업은 되돌릴 수 없습니다.");
            
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
                                    successAlert.setTitle("완료");
                                    successAlert.setHeaderText("로그가 초기화되었습니다.");
                                    successAlert.setContentText("모든 운전 이벤트 로그가 삭제되고 점수가 100점으로 초기화되었습니다.");
                                    successAlert.showAndWait();
                                } else {
                                    Alert errorAlert = new Alert(Alert.AlertType.ERROR);
                                    errorAlert.setTitle("오류");
                                    errorAlert.setHeaderText("로그 초기화 실패");
                                    errorAlert.setContentText("로그 파일을 초기화하는 중 오류가 발생했습니다.");
                                    errorAlert.showAndWait();
                                }
                            });
                        } catch (Exception ex) {
                            Platform.runLater(() -> {
                                clearLogsBtn.setDisable(false);
                                Alert errorAlert = new Alert(Alert.AlertType.ERROR);
                                errorAlert.setTitle("오류");
                                errorAlert.setHeaderText("로그 초기화 실패");
                                errorAlert.setContentText("오류: " + ex.getMessage());
                                errorAlert.showAndWait();
                            });
                        }
                    });
                }
            });
        });
        
        // Save button
        Button saveBtn = new Button("저장");
        saveBtn.setPrefWidth(Double.MAX_VALUE);
        saveBtn.setStyle("-fx-font-size: 14px;");
        saveBtn.setOnAction(e -> {
            boolean autoReportEnabled = autoReportCheck.isSelected();
            String fromPhone = fromPhoneField.getText().trim();
            String toPhone = toPhoneField.getText().trim();
            
            // Validate phone numbers
            if (fromPhone.isEmpty() || toPhone.isEmpty()) {
                Alert alert = new Alert(Alert.AlertType.WARNING);
                alert.setTitle("입력 오류");
                alert.setHeaderText("전화번호를 입력해주세요.");
                alert.setContentText("송신 및 수신 전화번호를 모두 입력해야 합니다.");
                alert.showAndWait();
                return;
            }
            
            saveBtn.setDisable(true);
            
            // Save settings
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
                            alert.setTitle("저장");
                            alert.setHeaderText("설정이 저장되었습니다.");
                            alert.setContentText(String.format("자동 신고 활성화: %s\n송신 번호: %s\n수신 번호: %s",
                                autoReportEnabled ? "예" : "아니오", fromPhone, toPhone));
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
                        saveBtn.setDisable(false);
                        Alert alert = new Alert(Alert.AlertType.ERROR);
                        alert.setTitle("오류");
                        alert.setHeaderText("설정 저장 실패");
                        alert.setContentText("오류: " + ex.getMessage());
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
        
        mainContainer.getChildren().clear();
        mainContainer.getChildren().add(detailScreen);
    }
    
    /** Show system check screen */
    private void showSystemCheckScreen() {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← 뒤로");
        backBtn.setOnAction(e -> {
            mainContainer.getChildren().clear();
            mainContainer.getChildren().add(createMainScreen());
        });
        
        Label title = new Label("시스템 체크");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
        Label descriptionLabel = new Label("각 센서 및 기능이 정상적으로 작동하는지 확인합니다.");
        descriptionLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #666;");
        descriptionLabel.setWrapText(true);
        
        TextArea resultArea = new TextArea();
        resultArea.setEditable(false);
        resultArea.setPrefRowCount(20);
        resultArea.setStyle("-fx-font-size: 11px;");
        resultArea.setText("시스템 체크를 실행하려면 '시스템 체크 실행' 버튼을 클릭하세요.\n\n");
        
        Button checkBtn = new Button("시스템 체크 실행");
        checkBtn.setPrefWidth(Double.MAX_VALUE);
        checkBtn.setStyle("-fx-font-size: 14px;");
        
        checkBtn.setOnAction(e -> {
            checkBtn.setDisable(true);
            resultArea.clear();
            resultArea.appendText("=== 시스템 체크 시작 ===\n");
            resultArea.appendText("각 센서와 기능을 확인하는 중...\n\n");
            
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
                            resultArea.appendText("[ERROR] check_system.py 파일을 찾을 수 없습니다.\n");
                            resultArea.appendText("경로: " + scriptPath + "\n");
                        });
                        return;
                    }
                    
                    ProcessBuilder pb = new ProcessBuilder(pythonCmd, scriptPath);
                    pb.directory(new java.io.File(finalProjectDir));
                    Process process = pb.start();
                    
                    // Read stdout (JSON result)
                    BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    // Read stderr (progress messages)
                    BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                    
                    StringBuilder jsonOutput = new StringBuilder();
                    String line;
                    
                    // Read stderr for progress
                    while ((line = stderrReader.readLine()) != null) {
                        final String logLine = line;
                        Platform.runLater(() -> {
                            resultArea.appendText(logLine + "\n");
                            resultArea.setScrollTop(Double.MAX_VALUE);
                        });
                    }
                    
                    // Read stdout for JSON result
                    while ((line = stdoutReader.readLine()) != null) {
                        jsonOutput.append(line).append("\n");
                    }
                    
                    int exitCode = process.waitFor();
                    
                    // Parse and display JSON results
                    Platform.runLater(() -> {
                        checkBtn.setDisable(false);
                        
                        try {
                            com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
                            com.fasterxml.jackson.databind.JsonNode results = mapper.readTree(jsonOutput.toString());
                            
                            resultArea.appendText("\n=== 체크 결과 ===\n\n");
                            
                            if (results.has("checks")) {
                                com.fasterxml.jackson.databind.JsonNode checks = results.get("checks");
                                
                                // Camera check
                                if (checks.has("camera")) {
                                    com.fasterxml.jackson.databind.JsonNode camera = checks.get("camera");
                                    String status = camera.get("status").asText();
                                    String message = camera.get("message").asText();
                                    String details = camera.has("details") ? camera.get("details").asText() : "";
                                    String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                    resultArea.appendText(String.format("%s 카메라: %s\n   %s\n", statusIcon, message, details));
                                }
                                
                                // Accelerometer check
                                if (checks.has("accelerometer")) {
                                    com.fasterxml.jackson.databind.JsonNode accel = checks.get("accelerometer");
                                    String status = accel.get("status").asText();
                                    String message = accel.get("message").asText();
                                    String details = accel.has("details") ? accel.get("details").asText() : "";
                                    String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                    resultArea.appendText(String.format("%s 가속도 센서: %s\n   %s\n", statusIcon, message, details));
                                }
                                
                                // GPS check
                                if (checks.has("gps")) {
                                    com.fasterxml.jackson.databind.JsonNode gps = checks.get("gps");
                                    String status = gps.get("status").asText();
                                    String message = gps.get("message").asText();
                                    String details = gps.has("details") ? gps.get("details").asText() : "";
                                    String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                    resultArea.appendText(String.format("%s GPS: %s\n   %s\n", statusIcon, message, details));
                                }
                                
                                // Speaker check
                                if (checks.has("speaker")) {
                                    com.fasterxml.jackson.databind.JsonNode speaker = checks.get("speaker");
                                    String status = speaker.get("status").asText();
                                    String message = speaker.get("message").asText();
                                    String details = speaker.has("details") ? speaker.get("details").asText() : "";
                                    String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                    resultArea.appendText(String.format("%s 스피커: %s\n   %s\n", statusIcon, message, details));
                                }
                                
                                // SMS check
                                if (checks.has("sms")) {
                                    com.fasterxml.jackson.databind.JsonNode sms = checks.get("sms");
                                    String status = sms.get("status").asText();
                                    String message = sms.get("message").asText();
                                    String details = sms.has("details") ? sms.get("details").asText() : "";
                                    String statusIcon = status.equals("OK") ? "✅" : status.equals("WARNING") ? "⚠️" : "❌";
                                    resultArea.appendText(String.format("%s SMS (자동 신고): %s\n   %s\n", statusIcon, message, details));
                                }
                            }
                            
                            resultArea.appendText("\n=== 체크 완료 ===\n");
                            resultArea.setScrollTop(Double.MAX_VALUE);
                            
                            if (exitCode == 0) {
                                Alert alert = new Alert(Alert.AlertType.INFORMATION);
                                alert.setTitle("시스템 체크 완료");
                                alert.setHeaderText("모든 체크가 완료되었습니다.");
                                alert.setContentText("결과를 확인하세요.");
                                alert.showAndWait();
                            }
                        } catch (Exception parseEx) {
                            resultArea.appendText("\n[ERROR] 결과 파싱 실패: " + parseEx.getMessage() + "\n");
                            resultArea.appendText("원본 출력:\n" + jsonOutput.toString() + "\n");
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
        
        HBox buttonBox = new HBox(10);
        buttonBox.setAlignment(Pos.CENTER);
        
        Button refreshBtn = new Button("새로고침");
        refreshBtn.setOnAction(e -> loadLogs(logArea));
        
        Button clearBtn = new Button("로그 초기화");
        clearBtn.setStyle("-fx-background-color: #d32f2f; -fx-text-fill: white;");
        clearBtn.setOnAction(e -> {
            Alert confirmAlert = new Alert(Alert.AlertType.CONFIRMATION);
            confirmAlert.setTitle("로그 초기화");
            confirmAlert.setHeaderText("로그를 초기화하시겠습니까?");
            confirmAlert.setContentText("모든 운전 이벤트 로그가 삭제되고 점수가 100점으로 초기화됩니다.\n이 작업은 되돌릴 수 없습니다.");
            
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
                                    successAlert.setTitle("완료");
                                    successAlert.setHeaderText("로그가 초기화되었습니다.");
                                    successAlert.setContentText("모든 운전 이벤트 로그가 삭제되고 점수가 100점으로 초기화되었습니다.");
                                    successAlert.showAndWait();
                                    loadLogs(logArea);  // Refresh log display
                                } else {
                                    Alert errorAlert = new Alert(Alert.AlertType.ERROR);
                                    errorAlert.setTitle("오류");
                                    errorAlert.setHeaderText("로그 초기화 실패");
                                    errorAlert.setContentText("로그 파일을 초기화하는 중 오류가 발생했습니다.");
                                    errorAlert.showAndWait();
                                }
                            });
                        } catch (Exception ex) {
                            Platform.runLater(() -> {
                                clearBtn.setDisable(false);
                                refreshBtn.setDisable(false);
                                Alert errorAlert = new Alert(Alert.AlertType.ERROR);
                                errorAlert.setTitle("오류");
                                errorAlert.setHeaderText("로그 초기화 실패");
                                errorAlert.setContentText("오류: " + ex.getMessage());
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
            
            if (logSummary.has("report_stats")) {
                com.fasterxml.jackson.databind.JsonNode reportStats = logSummary.get("report_stats");
                logText.append("\n자동 신고 통계:\n");
                if (reportStats.has("alert_triggered")) {
                    logText.append("  경고 발생: ").append(reportStats.get("alert_triggered").asInt()).append("회\n");
                }
                if (reportStats.has("report_triggered")) {
                    logText.append("  신고 실행: ").append(reportStats.get("report_triggered").asInt()).append("회\n");
                }
                if (reportStats.has("report_cancelled")) {
                    logText.append("  신고 취소: ").append(reportStats.get("report_cancelled").asInt()).append("회\n");
                }
                if (reportStats.has("sms_sent")) {
                    logText.append("  SMS 발송: ").append(reportStats.get("sms_sent").asInt()).append("회\n");
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
