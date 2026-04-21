/**
 * Mirror Logger Extension
 *
 * Integrates Pi with the Mirror Mind memory system.
 *
 * Events handled:
 * - session_start      → unmute + close stale orphans + extract pending memories
 * - before_agent_start → log user prompt with explicit session id
 * - agent_end          → log assistant response (all messages in the turn)
 * - session_shutdown   → close conversation + backup database
 *
 * All heavy logic lives in the Python CLI. This extension is a thin dispatcher.
 * Failures are swallowed to never block Pi — but logged to $MEMORY_DIR/mirror-logger.log.
 */

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { appendFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

// Respect MEMORY_DIR so Pi session files land in the same directory Python reads.
// Fallback to ~/.mirror-poc if unset.
function _resolveMemoryDir(): string {
	const raw = process.env.MEMORY_DIR;
	if (!raw) return join(homedir(), ".mirror-poc");
	return raw.startsWith("~") ? join(homedir(), raw.slice(2)) : raw;
}

const MIRROR_DIR = _resolveMemoryDir();
const LOG_FILE = join(MIRROR_DIR, "mirror-logger.log");

// Content size limit for CLI arguments (~50KB, safe for macOS ARG_MAX)
const MAX_CONTENT_SIZE = 50_000;

export default function (pi: ExtensionAPI) {
	// --- Helpers ---

	function log(level: string, msg: string): void {
		try {
			const ts = new Date().toISOString();
			mkdirSync(MIRROR_DIR, { recursive: true });
			appendFileSync(LOG_FILE, `${ts} [${level}] ${msg}\n`);
		} catch {
			// Logging failure must never break anything
		}
	}

	async function runPy(args: string[]): Promise<string> {
		try {
			const result = await pi.exec("python3", args, {
				timeout: 30_000,
			});
			const stderr = (result?.stderr ?? "").trim();
			if (stderr) {
				log("WARN", `stderr from [${args.slice(0, 3).join(" ")}]: ${stderr.slice(0, 500)}`);
			}
			return (result?.stdout ?? "").trim();
		} catch (err: unknown) {
			const message = err instanceof Error ? err.message : String(err);
			log("ERROR", `runPy failed [${args.slice(0, 3).join(" ")}]: ${message.slice(0, 500)}`);
			return "";
		}
	}

	/** Extract readable text from a content blocks array or plain string. */
	function extractText(content: unknown): string {
		if (typeof content === "string") return content;
		if (!Array.isArray(content)) return "";
		return content
			.filter((b: Record<string, unknown>) => b && b.type === "text" && typeof b.text === "string")
			.map((b: Record<string, unknown>) => b.text as string)
			.join("\n");
	}

	/** Truncate content to fit in CLI arguments. */
	function truncate(text: string): string {
		if (text.length <= MAX_CONTENT_SIZE) return text;
		return text.slice(0, MAX_CONTENT_SIZE) + "\n[… truncated]";
	}

	// --- 1. session_start → unmute + close stale orphans + extract pending ---

	pi.on("session_start", async (_event, ctx) => {
		log("INFO", "session_start fired");
		const summary = await runPy(["-m", "memory", "conversation-logger", "session-start"]);
		log("INFO", `session-start result: ${summary || "(empty)"}`);
		if (ctx.hasUI) {
			if (summary) {
				ctx.ui.notify(summary, "info");
			}
			ctx.ui.setStatus("mirror", summary || "Memory ready");
		}
	});

	// --- 2. before_agent_start → log user prompt with explicit session id ---

	pi.on("before_agent_start", async (event, ctx) => {
		const sessionId = ctx.sessionManager.getSessionFile() ?? null;
		if (!sessionId) return;

		const prompt = event.prompt ?? "";
		if (!prompt || prompt.startsWith("/")) return;

		log("INFO", `log-user: ${prompt.slice(0, 80)}...`);
		await runPy([
			"-m",
			"memory",
			"conversation-logger",
			"log-user",
			sessionId,
			truncate(prompt),
			"--interface",
			"pi",
		]);
	});

	// --- 3. agent_end → log assistant response ---
	//
	// agent_end fires once per user prompt, with ALL messages in the cycle
	// (assistant + tool calls + tool results). Extract only assistant text
	// and log as a single consolidated message.

	pi.on("agent_end", async (event, ctx) => {
		const sessionId = ctx.sessionManager.getSessionFile() ?? null;
		if (!sessionId) return;

		const messages = (event as Record<string, unknown>).messages;
		if (!Array.isArray(messages) || messages.length === 0) return;

		const assistantTexts: string[] = [];
		for (const msg of messages) {
			if (
				msg &&
				typeof msg === "object" &&
				"role" in msg &&
				(msg as Record<string, unknown>).role === "assistant"
			) {
				const text = extractText((msg as Record<string, unknown>).content);
				if (text.trim()) {
					assistantTexts.push(text);
				}
			}
		}

		if (assistantTexts.length === 0) return;

		log("INFO", `log-assistant: ${assistantTexts.length} block(s), ${assistantTexts.join("").length} chars`);

		const combined = assistantTexts.join("\n\n---\n\n");
		const content = truncate(combined);

		await runPy([
			"-m",
			"memory",
			"conversation-logger",
			"log-assistant",
			sessionId,
			content,
			"--interface",
			"pi",
		]);
	});

	// --- 4. session_shutdown → close conversation + backup ---
	//
	// Uses extract=False because extraction calls the LLM and can take 30s+.
	// Extraction happens at the next session_start via extract_pending.

	pi.on("session_shutdown", async (_event, ctx) => {
		const sessionId = ctx.sessionManager.getSessionFile() ?? null;

		if (sessionId) {
			await runPy(["-m", "memory", "conversation-logger", "session-end-pi", sessionId]);
			log("INFO", `session closed: ${sessionId}`);
		}

		await runPy(["-m", "memory", "backup", "--silent"]);
	});
}
