import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.21"
    id("org.jetbrains.intellij") version "1.17.0"
}

group = "com.deepstudyai.coach"
version = "0.1.0-alpha"

repositories {
    mavenCentral()
}

dependencies {
    // Kotlin
    implementation(kotlin("stdlib"))
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")

    // LSP4J for Language Server Protocol
    implementation("org.eclipse.lsp4j:org.eclipse.lsp4j:0.21.1")
    implementation("org.eclipse.lsp4j:org.eclipse.lsp4j.jsonrpc:0.21.1")

    // Logging
    implementation("io.github.microutils:kotlin-logging-jvm:3.0.5")
    implementation("org.slf4j:slf4j-api:2.0.9")

    // HTTP client for API calls
    implementation("com.squareup.okhttp3:okhttp:4.12.0")

    // Testing
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("org.mockito.kotlin:mockito-kotlin:5.1.0")
}

// Configure Gradle IntelliJ Plugin
intellij {
    version.set("2023.1")
    type.set("IC") // IntelliJ IDEA Community Edition

    plugins.set(listOf(
        "com.intellij.java",
        "org.jetbrains.kotlin",
        "JavaScript",
        "Python",
        "org.jetbrains.plugins.yaml"
    ))
}

tasks {
    withType<JavaCompile> {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }

    withType<KotlinCompile> {
        kotlinOptions.jvmTarget = "17"
    }

    patchPluginXml {
        sinceBuild.set("231")
        untilBuild.set("241.*")

        pluginDescription.set("""
            <h1>Coach - AI with Level 4 Anticipatory Empathy</h1>

            <p><strong>Built on LangChain</strong> - 16 specialized AI wizards that predict problems before they happen.</p>

            <h2>Features</h2>
            <ul>
                <li><strong>Level 4 Predictions</strong> - Predicts issues 30-90 days ahead</li>
                <li><strong>16 Specialized Wizards</strong> - Security, Performance, Accessibility, and more</li>
                <li><strong>Multi-Wizard Collaboration</strong> - Wizards consult each other for complex scenarios</li>
                <li><strong>Framework Integration</strong> - Use Coach wizards in your own projects</li>
                <li><strong>Project Templates</strong> - Quick-start custom wizard development</li>
            </ul>

            <h2>Documentation</h2>
            <ul>
                <li><a href="https://docs.coach-ai.dev/installation">Installation Guide</a></li>
                <li><a href="https://docs.coach-ai.dev/user-manual">User Manual</a></li>
                <li><a href="https://docs.coach-ai.dev/custom-wizards">Custom Wizards Tutorial</a></li>
            </ul>
        """.trimIndent())
    }

    signPlugin {
        certificateChain.set(System.getenv("CERTIFICATE_CHAIN"))
        privateKey.set(System.getenv("PRIVATE_KEY"))
        password.set(System.getenv("PRIVATE_KEY_PASSWORD"))
    }

    publishPlugin {
        token.set(System.getenv("PUBLISH_TOKEN"))
    }

    test {
        useJUnitPlatform()
    }
}
