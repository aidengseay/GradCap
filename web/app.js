
"use strict";

// ============================================================================
// Configuration
// ============================================================================

const API = {
    text: "/api/text",
    clear: "/api/clear",
    brightness: "/api/brightness",
    animation: "/api/animation"
};

const BRIGHTNESS_INTERVAL_MS = 100;

// ============================================================================
// Display State
// ============================================================================

// The website starts in a blank state.
// The CircuitPython backend will also initialize the matrix as blank.

const displayState = {
    mode: "blank",
    text: null,
    textColor: "#ffffff",
    animation: null,
    brightness: 0.25
};

// ============================================================================
// DOM Elements
// ============================================================================

const currentMode = document.getElementById("current-mode");
const currentContent = document.getElementById("current-content");

const textInput = document.getElementById("text-input");
const textColorInput = document.getElementById("text-color");
const textColorValue = document.getElementById("text-color-value");
const sendTextButton = document.getElementById("send-text");

const brightnessSlider = document.getElementById("brightness");
const brightnessValue = document.getElementById("brightness-value");

const animationSelect = document.getElementById("animation-select");
const startAnimationButton = document.getElementById("start-animation");

const clearButton = document.getElementById("clear-display");

// ============================================================================
// API Communication
// ============================================================================

async function sendRequest(endpoint, payload = null) {
    const options = {
        method: "POST"
    };

    if(payload !== null) {
        options.headers = {
            "Content-Type": "application/json"
        };

        options.body = JSON.stringify(payload);
    }

    const response = await fetch(endpoint, options);

    if (!response.ok) {
        throw new Error(
            `HTTP ${response.status}: ${response.statusText}`
        );
    }

    // Only an HTTP success response is required.
    // The backend does not need to return JSON.
}

// ============================================================================
// UI State
// ============================================================================

function updateStatus() {
    switch(displayState.mode) {
        case "text":
            currentMode.textContent = "Scrolling Text";
            currentContent.textContent = displayState.text;
            break;

        case "animation":
            currentMode.textContent = "Animation";
            currentContent.textContent = displayState.animation;
            break;

        default:
            currentMode.textContent = "Blank";
            currentContent.textContent = "None";
            break;
    }

    brightnessValue.textContent =
        `${Math.round(displayState.brightness * 100)}%`;
}

function showError(error) {
    console.error("GradCap Error:", error);
    alert(`Unable to communicate with GradCap:\n${error.message}`);
}

// ============================================================================
// Custom Text
// ============================================================================

async function sendText() {
    const text = textInput.value.trim();
    const color = textColorInput.value;

    if(text.length === 0) {
        alert("Please enter text to display.");
        return;
    }

    sendTextButton.disabled = true;

    try {
        await sendRequest(API.text, {
            text: text,
            color: color
        });

        displayState.mode = "text";
        displayState.text = text;
        displayState.textColor = color;
        displayState.animation = null;

        updateStatus();
    } catch (error) {
        showError(error);
    } finally {
        sendTextButton.disabled = false;
    }
}

// ============================================================================
// Animations
// ============================================================================

async function startAnimation() {
    const animation = animationSelect.value;

    startAnimationButton.disabled = true;

    try {
        await sendRequest(API.animation, { animation });

        displayState.mode = "animation";
        displayState.animation = animation;
        displayState.text = null;

        updateStatus();
    } catch (error) {
        showError(error);
    } finally {
        startAnimationButton.disabled = false;
    }
}

// ============================================================================
// Clear Display
// ============================================================================

async function clearDisplay() {
    clearButton.disabled = true;

    try {
        await sendRequest(API.clear);

        displayState.mode = "blank";
        displayState.text = null;
        displayState.animation = null;

        updateStatus();
    } catch (error) {
        showError(error);
    } finally {
        clearButton.disabled = false;
    }
}

// ============================================================================
// Brightness
// ============================================================================

// Throttle requests and send the latest slider value.
// Requests are serialized so an older request cannot arrive after a newer one.

let brightnessSending = false;
let brightnessPending = false;
let brightnessLastSent = 0;
let brightnessTimer = null;

function queueBrightness() {
    // Update the percentage label immediately.
    brightnessValue.textContent = `${brightnessSlider.value}%`;

    brightnessPending = true;
    scheduleBrightness();
}

function scheduleBrightness() {
    if(!brightnessPending || brightnessSending || brightnessTimer !== null) {
        return;
    }

    const elapsed = Date.now() - brightnessLastSent;
    const delay = Math.max(0, BRIGHTNESS_INTERVAL_MS - elapsed);

    brightnessTimer = setTimeout(() => {
        brightnessTimer = null;
        flushBrightness();
    }, delay);
}

async function flushBrightness() {
    if(!brightnessPending || brightnessSending) {
        return;
    }

    brightnessSending = true;
    brightnessPending = false;
    brightnessLastSent = Date.now();

    const brightness = Number(brightnessSlider.value) / 100;

    try {
        await sendRequest(API.brightness, { brightness });

        displayState.brightness = brightness;
    } catch (error) {
        showError(error);
    } finally {
        brightnessSending = false;

        // If the slider moved while the request was in progress,
        // send the most recent value next.
        scheduleBrightness();
    }
}

// ============================================================================
// Event Listeners
// ============================================================================

sendTextButton.addEventListener("click", sendText);

textInput.addEventListener("keydown", (event) => {
    if(event.key === "Enter") {
        sendText();
    }
});

textColorInput.addEventListener("input", () => {
    textColorValue.textContent = textColorInput.value.toUpperCase();
});

startAnimationButton.addEventListener("click", startAnimation);

clearButton.addEventListener("click", clearDisplay);

brightnessSlider.addEventListener("input", queueBrightness);

// ============================================================================
// Initialization
// ============================================================================

updateStatus();

console.log("GradCap Controller initialized");
