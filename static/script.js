let tasks = [];
let timers = {};

const BASE_URL = "localhost:8080";

async function loadTasks() {
    const res = await fetch(`${BASE_URL}/api/tasks`);
    tasks = await res.json();
    renderTasks();
}

async function addTask(e) {
    e.preventDefault();
    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;

    await fetch(`${BASE_URL}/api/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description }),
    });

    document.getElementById("taskForm").reset();
    document.getElementById("title").focus();
    loadTasks();
}

async function startTask(id) {
    await fetch(`${BASE_URL}/api/tasks/${id}/start`, { method: "POST" });
    loadTasks();
}

async function pauseTask(id) {
    await fetch(`${BASE_URL}/api/tasks/${id}/pause`, { method: "POST" });
    loadTasks();
}

async function completeTask(id) {
    await fetch(`${BASE_URL}/api/tasks/${id}/complete`, { method: "POST" });
    loadTasks();
}

function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h.toString().padStart(2, "0")}:${m
        .toString()
        .padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

function calculateElapsed(task) {
    let elapsed = task.total_elapsed;
    if (task.status === "active" && task.last_started) {
        const lastStarted = new Date(task.last_started);
        elapsed += (Date.now() - lastStarted.getTime()) / 1000;
    }
    return elapsed;
}

function updateTimers() {
    tasks.forEach((task) => {
        if (task.status === "active") {
            const el = document.getElementById(`timer-${task.id}`);
            if (el) {
                el.textContent = formatTime(calculateElapsed(task));
            }
        }
    });
}

function renderTasks() {
    Object.values(timers).forEach(clearInterval);
    timers = {};

    const activeTasks = tasks.filter((t) => t.status !== "completed");
    const completedTasks = tasks
        .filter((t) => t.status === "completed")
        .sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at));

    document.getElementById("activeTasks").innerHTML = activeTasks.length
        ? '<div class="section-title">Active Tasks</div>' +
          renderTaskList(activeTasks)
        : "";

    document.getElementById("completedTasks").innerHTML = completedTasks.length
        ? '<div class="section-title">Completed Tasks</div>' +
          renderTaskList(completedTasks)
        : "";

    tasks
        .filter((t) => t.status === "active")
        .forEach((task) => {
            timers[task.id] = setInterval(() => {
                const el = document.getElementById(`timer-${task.id}`);
                if (el) el.textContent = formatTime(calculateElapsed(task));
            }, 1000);
        });
}

function renderTaskList(taskList) {
    return `<div class="task-list">${taskList
        .map(
            (task) => `
                <div class="task-card ${
                    task.status === "completed" ? "completed" : ""
                }">
                    <div class="task-header">
                        <div class="task-title">${escapeHtml(task.title)}</div>
                        <div class="task-timer ${
                            task.status === "active" ? "active" : ""
                        }" 
                             id="timer-${task.id}">
                            ${formatTime(calculateElapsed(task))}
                        </div>
                    </div>
                    ${
                        task.description
                            ? `<div class="task-description">${escapeHtml(
                                  task.description
                              )}</div>`
                            : ""
                    }
                    <div class="task-meta">
                        <span class="task-status status-${task.status.replace(
                            "_",
                            "-"
                        )}">
                            ${task.status.replace("_", " ")}
                        </span>
                        <span>Created: ${new Date(
                            task.created_at
                        ).toLocaleString()}</span>
                        ${
                            task.completed_at
                                ? `<span>Completed: ${new Date(
                                      task.completed_at
                                  ).toLocaleString()}</span>`
                                : ""
                        }
                    </div>
                    <div class="task-actions">
                        ${
                            task.status === "not_started" ||
                            task.status === "paused"
                                ? `<button class="btn btn-success" onclick="startTask(${task.id})">▶ Start</button>`
                                : ""
                        }
                        ${
                            task.status === "active"
                                ? `<button class="btn btn-warning" onclick="pauseTask(${task.id})">⏸ Pause</button>`
                                : ""
                        }
                        ${
                            task.status !== "completed"
                                ? `<button class="btn btn-secondary" onclick="completeTask(${task.id})">✓ Complete</button>`
                                : ""
                        }
                    </div>
                </div>
            `
        )
        .join("")}</div>`;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById("taskForm").addEventListener("submit", addTask);
loadTasks();
setInterval(updateTimers, 100);
