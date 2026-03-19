// Ensure this is at the top of your main.js
async function generatePrompt() {
    const goal = document.getElementById('goal').value;
    const stack = document.getElementById('stack').value;
    const task = document.getElementById('task').value;
    const outputBox = document.getElementById('output');

    if (!goal) {
        alert("Please enter a goal first.");
        return;
    }

    outputBox.innerText = "Generating...";

    try {
        const response = await fetch('/generate_prompt', { method: 'POST' });
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            window.location.href = '/unlock';
            return;
        }

        // The Template
        const promptText = `You are an expert developer.

CONTEXT:
Goal: ${goal}
Stack: ${stack}
Task Type: ${task}

REQUIREMENTS:
1. Provide clean, production-ready code.
2. Follow ${stack} best practices.
3. Ensure no secrets or API keys are hardcoded.
4. Add brief comments explaining the logic.

OUTPUT:`;

        outputBox.innerText = promptText;

        // Save history only if user is pro
        if (typeof IS_PAID !== 'undefined' && IS_PAID) {
            saveToHistory(goal, promptText);
        }

    } catch (err) {
        console.error("Fetch error:", err);
        outputBox.innerText = "Error generating prompt. Check console.";
    }
}

function copyOutput() {
    const text = document.getElementById('output').innerText;
    if (text.includes("Your prompt will appear here")) return;
    
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.querySelector('button[onclick="copyOutput()"]');
        const originalText = btn.innerText;
        btn.innerText = "Copied!";
        setTimeout(() => btn.innerText = originalText, 2000);
    });
}