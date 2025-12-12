package org.example.iotprojectui.controllers;

import javafx.geometry.Insets;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.BarChart;
import javafx.scene.chart.CategoryAxis;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import org.example.iotprojectui.JsonDataLoader;
import com.fasterxml.jackson.databind.JsonNode;

/**
 * Controller for the driving report screen with charts
 */
public class ReportScreenController implements BaseScreenController {
    private Runnable onBack;
    
    public ReportScreenController(Runnable onBack) {
        this.onBack = onBack;
    }
    
    @Override
    public void showScreen(StackPane container) {
        ScrollPane detailScreen = new ScrollPane();
        VBox content = new VBox(15);
        content.setPadding(new Insets(20));
        
        Button backBtn = new Button("← Back");
        backBtn.setOnAction(e -> onBack.run());
        
        Label title = new Label("Driving Report");
        title.setStyle("-fx-font-size: 20px; -fx-font-weight: bold;");
        
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
        
        VBox reportInfo = new VBox(10);
        if (logSummary != null) {
            if (logSummary.has("monthly_score")) {
                Label scoreLabel = new Label("Monthly Score: " + logSummary.get("monthly_score").asInt() + " pts");
                scoreLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");
                reportInfo.getChildren().add(scoreLabel);
            }
            
            // Daily Safety Score Chart
            CategoryAxis xAxisLine = new CategoryAxis();
            xAxisLine.setLabel("Day");
            xAxisLine.setTickLabelFont(javafx.scene.text.Font.font(9));
            NumberAxis yAxisLine = new NumberAxis(0, 100, 20);
            yAxisLine.setLabel("Score");
            yAxisLine.setTickLabelFont(javafx.scene.text.Font.font(9));
            
            LineChart<String, Number> lineChart = new LineChart<>(xAxisLine, yAxisLine);
            lineChart.setTitle("Daily Safety Score");
            lineChart.setPrefHeight(200);
            lineChart.setLegendVisible(false);
            lineChart.setStyle("-fx-font-size: 9px;");
            
            XYChart.Series<String, Number> scoreSeries = new XYChart.Series<>();
            if (logSummary.has("daily_scores")) {
                JsonNode dailyScores = logSummary.get("daily_scores");
                for (JsonNode score : dailyScores) {
                    int day = score.has("day") ? score.get("day").asInt() : 0;
                    int scoreValue = score.has("score") ? score.get("score").asInt() : 0;
                    scoreSeries.getData().add(new XYChart.Data<>("Day " + day, scoreValue));
                }
            }
            lineChart.getData().add(scoreSeries);
            
            // Event Count Bar Chart
            CategoryAxis xAxisBar = new CategoryAxis();
            xAxisBar.setLabel("Event");
            xAxisBar.setTickLabelFont(javafx.scene.text.Font.font(9));
            NumberAxis yAxisBar = new NumberAxis();
            yAxisBar.setLabel("Count");
            yAxisBar.setTickLabelFont(javafx.scene.text.Font.font(9));
            
            BarChart<String, Number> barChart = new BarChart<>(xAxisBar, yAxisBar);
            barChart.setTitle("Event Count by Type");
            barChart.setPrefHeight(200);
            barChart.setLegendVisible(false);
            barChart.setStyle("-fx-font-size: 9px;");
            
            XYChart.Series<String, Number> eventSeries = new XYChart.Series<>();
            if (logSummary.has("event_counts")) {
                JsonNode events = logSummary.get("event_counts");
                if (events.has("sudden_stop")) {
                    eventSeries.getData().add(new XYChart.Data<>("Sudden Stop", events.get("sudden_stop").asInt()));
                }
                if (events.has("sudden_acceleration")) {
                    eventSeries.getData().add(new XYChart.Data<>("Sudden Accel", events.get("sudden_acceleration").asInt()));
                }
                if (events.has("drowsiness")) {
                    eventSeries.getData().add(new XYChart.Data<>("Drowsiness", events.get("drowsiness").asInt()));
                }
            }
            barChart.getData().add(eventSeries);
            
            // Event counts text
            if (logSummary.has("event_counts")) {
                JsonNode events = logSummary.get("event_counts");
                Label eventsLabel = new Label("Event Details:");
                eventsLabel.setStyle("-fx-font-size: 14px; -fx-font-weight: bold;");
                reportInfo.getChildren().add(eventsLabel);
                
                if (events.has("sudden_stop")) {
                    Label stopLabel = new Label("  Sudden Stop: " + events.get("sudden_stop").asInt() + " times");
                    stopLabel.setStyle("-fx-font-size: 12px;");
                    reportInfo.getChildren().add(stopLabel);
                }
                if (events.has("sudden_acceleration")) {
                    Label accelLabel = new Label("  Sudden Acceleration: " + events.get("sudden_acceleration").asInt() + " times");
                    accelLabel.setStyle("-fx-font-size: 12px;");
                    reportInfo.getChildren().add(accelLabel);
                }
                if (events.has("drowsiness")) {
                    Label drowsyLabel = new Label("  Drowsiness: " + events.get("drowsiness").asInt() + " times");
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
        
        container.getChildren().clear();
        container.getChildren().add(detailScreen);
    }
}

