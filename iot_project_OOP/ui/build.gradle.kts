plugins {
    java
    application
    id("org.openjfx.javafxplugin") version "0.0.13"
}

group = "org.example"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

val junitVersion = "5.12.1"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
}

application {
    // Use demo for full UI
    mainClass.set("org.example.iotprojectui.demo")
}

javafx {
    version = "21.0.6"
    // Only include modules that are actually used
    // javafx.web, javafx.media, javafx.swing are not available on all platforms
    modules = listOf("javafx.controls", "javafx.fxml")
    // Platform classifier will be automatically detected:
    // - linux-aarch64 for Raspberry Pi (ARM64)
    // - linux-arm32 for Raspberry Pi (ARM32)
    // - linux-x86_64 for x86_64 Linux
    // - win-x86_64 for Windows
    // - mac-aarch64 for Apple Silicon
    // - mac-x86_64 for Intel Mac
}

dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.2")
    implementation("org.controlsfx:controlsfx:11.2.1")
    implementation("com.dlsc.formsfx:formsfx-core:11.6.0") {
        exclude(group = "org.openjfx")
    }
    implementation("net.synedra:validatorfx:0.6.1") {
        exclude(group = "org.openjfx")
    }
    implementation("org.kordamp.ikonli:ikonli-javafx:12.3.1")
    implementation("org.kordamp.bootstrapfx:bootstrapfx-core:0.4.0")
    implementation("eu.hansolo:tilesfx:21.0.9") {
        exclude(group = "org.openjfx")
    }
    dependencies {
        implementation("org.jetbrains.kotlin:kotlin-stdlib:1.9.23")
    }
    implementation("com.github.almasb:fxgl:17.3") {
        exclude(group = "org.openjfx")
        exclude(group = "org.jetbrains.kotlin")
    }
    testImplementation("org.junit.jupiter:junit-jupiter-api:${junitVersion}")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:${junitVersion}")
}

tasks.withType<Test> {
    useJUnitPlatform()
}
