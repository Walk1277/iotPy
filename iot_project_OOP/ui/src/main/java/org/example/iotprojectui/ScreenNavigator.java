package org.example.iotprojectui;

import javafx.scene.layout.StackPane;

/**
 * Utility class for screen navigation
 */
public class ScreenNavigator {
    private StackPane container;
    private Runnable mainScreenFactory;
    
    public ScreenNavigator(StackPane container, Runnable mainScreenFactory) {
        this.container = container;
        this.mainScreenFactory = mainScreenFactory;
    }
    
    public void navigateToMainScreen() {
        container.getChildren().clear();
        mainScreenFactory.run();
    }
    
    public void navigateToScreen(javafx.scene.Node screen) {
        container.getChildren().clear();
        container.getChildren().add(screen);
    }
}

