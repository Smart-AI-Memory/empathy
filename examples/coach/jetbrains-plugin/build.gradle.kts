plugins {
    id("org.jetbrains.kotlin.jvm") version "1.9.21"
    id("org.jetbrains.intellij") version "1.16.1"
}

group = "com.deepstudyai"
version = "1.7.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib")

    // LSP support
    implementation("org.eclipse.lsp4j:org.eclipse.lsp4j:0.21.1")

    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("junit:junit:4.13.2")
}

intellij {
    version.set("2024.1")
    type.set("IC") // IntelliJ IDEA Community Edition

    plugins.set(listOf(
        // Add plugin dependencies here
    ))
}

tasks {
    // Set the JVM compatibility versions
    withType<JavaCompile> {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }

    withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
        kotlinOptions.jvmTarget = "17"
    }

    patchPluginXml {
        sinceBuild.set("241")
        untilBuild.set("243.*")

        changeNotes.set("""
            <h2>1.7.0 - Production/Stable Release</h2>
            <ul>
                <li>Production-ready stable release</li>
                <li>16 specialized wizards for software development</li>
                <li>Level 4 Anticipatory predictions (30-90 days)</li>
                <li>Multi-wizard collaboration</li>
                <li>Full IntelliJ Platform integration</li>
                <li>90.71% test coverage</li>
                <li>Real-time code analysis</li>
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
}
