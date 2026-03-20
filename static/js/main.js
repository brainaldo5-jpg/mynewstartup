// --- 1. FIREBASE CONFIGURATION ---
// Replace these with your actual keys from the Firebase Console Settings
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// Initialize Firebase safely
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const db = firebase.firestore();

// --- 2. SELECTING ELEMENTS ---
const generateBtn = document.getElementById('generateBtn');
const resultBox = document.getElementById('resultBox');
const outputArea = document.getElementById('outputArea');
const copyBtn = document.getElementById('copyBtn');

// This picks up the data we passed from Python/Jinja in app.html
const configElement = document.getElementById('app-config');
const isPaidUser = configElement.getAttribute('data-is-paid') === 'True';
const userEmail = configElement.getAttribute('data-email');

// --- 3. GENERATION LOGIC ---
generateBtn.addEventListener('click', async () => {
    const stack = document.getElementById('techStack').value;
    const goal = document.getElementById('actionType').value;
    const prompt = document.getElementById('userInput').value;

    if (!prompt) {
        alert("Please describe what you want to build first!");
        return;
    }

    // UI Loading State
    generateBtn.innerText = "Architecting Blueprint...";
    generateBtn.disabled = true;

    try {
        const response = await fetch('/generate_prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                stack: stack, 
                goal: goal, 
                prompt: prompt 
            })
        });

        // Handle the 3-prompt limit (403 Forbidden)
        if (response.status === 403) {
            alert("🚀 Free Limit Reached! Redirecting to unlock Pro for lifetime access (₦200).");
            window.location.href = '/unlock';
            return;
        }

        const data = await response.json();

        if (data.result) {
            // Display the Result
            resultBox.innerText = data.result;
            outputArea.classList.remove('hidden');

            // Save to Firebase History ONLY if they are a Pro Member
            if (isPaidUser && userEmail !== "guest@example.com") {
                saveToHistory(stack, goal, data.result);
            }
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Connection lost. Please check your internet.");
    } finally {
        generateBtn.innerText = "Generate Professional Architecture";
        generateBtn.disabled = false;
    }
});

// --- 4. FIREBASE HISTORY FUNCTION ---
async function saveToHistory(stack, goal, content) {
    try {
        await db.collection('users').doc(userEmail).collection('history').add({
            title: `${stack} - ${goal}`,
            content: content,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });
        console.log("Blueprint saved to your Pro History.");
    } catch (e) {
        console.warn("History could not be saved to Firebase:", e);
    }
}

// --- 5. CLIPBOARD UTILITY ---
copyBtn.addEventListener('click', () => {
    const text = resultBox.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const originalText = copyBtn.innerText;
        copyBtn.innerText = "Copied!";
        setTimeout(() => { copyBtn.innerText = originalText; }, 2000);
    });
});