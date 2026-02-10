use std::collections::HashMap;
use std::fmt;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;

use chrono::{DateTime, Local};
use clap::Parser;
use serde::Deserialize;
use tokio::net::TcpStream;
use tokio::time::timeout;

// ANSI color codes
const RED: &str = "\x1b[31m";
const GREEN: &str = "\x1b[32m";
const YELLOW: &str = "\x1b[33m";
const BOLD: &str = "\x1b[1m";
const RESET: &str = "\x1b[0m";

const SUPPORTED_TYPES: &[&str] = &["http", "tcp"];

#[derive(Parser)]
#[command(name = "downtime-benchmarker", about = "Measure service downtime during maintenance windows")]
struct Cli {
    /// Path to the YAML targets file
    #[arg(long = "target-urls")]
    target_urls: PathBuf,

    /// Seconds between checks
    #[arg(long = "check-interval", default_value = "1")]
    check_interval: u64,

    /// Per-check timeout in seconds
    #[arg(long, default_value = "5")]
    timeout: u64,
}

#[derive(Deserialize)]
struct TargetsFile {
    targets: Vec<RawTarget>,
}

#[derive(Deserialize)]
struct RawTarget {
    name: String,
    r#type: String,
    #[serde(default)]
    args: HashMap<String, serde_yaml::Value>,
}

#[derive(Clone)]
struct Target {
    name: String,
    check: Check,
}

#[derive(Clone)]
enum Check {
    Http { url: String },
    Tcp { host: String, port: u16 },
}

impl fmt::Display for Target {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.name)
    }
}

impl Target {
    fn icon(&self) -> &'static str {
        match self.check {
            Check::Http { .. } => "🌐",
            Check::Tcp { .. } => "🔌",
        }
    }

    fn type_name(&self) -> &'static str {
        match self.check {
            Check::Http { .. } => "http",
            Check::Tcp { .. } => "tcp",
        }
    }
}

fn validate_targets(raw_targets: Vec<RawTarget>) -> Result<Vec<Target>, String> {
    let mut targets = Vec::with_capacity(raw_targets.len());

    for (i, raw) in raw_targets.into_iter().enumerate() {
        let idx = i + 1;

        if !SUPPORTED_TYPES.contains(&raw.r#type.as_str()) {
            return Err(format!(
                "Target #{}: unsupported type '{}'. Supported types: {}",
                idx,
                raw.r#type,
                SUPPORTED_TYPES.join(", ")
            ));
        }

        let check = match raw.r#type.as_str() {
            "http" => {
                let allowed = &["url"];
                check_unknown_args(&raw.args, allowed, idx, "http")?;

                let url = require_string_arg(&raw.args, "url", idx, "http")?;
                Check::Http { url }
            }
            "tcp" => {
                let allowed = &["host", "port"];
                check_unknown_args(&raw.args, allowed, idx, "tcp")?;

                let host = require_string_arg(&raw.args, "host", idx, "tcp")?;
                let port_val = raw.args.get("port").ok_or_else(|| {
                    format!("Target #{} (tcp): missing required arg 'port'", idx)
                })?;
                let port = match port_val {
                    serde_yaml::Value::Number(n) => n
                        .as_u64()
                        .and_then(|v| u16::try_from(v).ok())
                        .ok_or_else(|| {
                            format!(
                                "Target #{} (tcp): 'port' must be a valid port number (1-65535)",
                                idx
                            )
                        })?,
                    _ => {
                        return Err(format!(
                            "Target #{} (tcp): 'port' must be a number",
                            idx
                        ))
                    }
                };
                if port == 0 {
                    return Err(format!(
                        "Target #{} (tcp): 'port' must be a valid port number (1-65535)",
                        idx
                    ));
                }
                Check::Tcp { host, port }
            }
            _ => unreachable!(),
        };

        targets.push(Target {
            name: raw.name,
            check,
        });
    }

    Ok(targets)
}

fn check_unknown_args(
    args: &HashMap<String, serde_yaml::Value>,
    allowed: &[&str],
    idx: usize,
    type_name: &str,
) -> Result<(), String> {
    for key in args.keys() {
        if !allowed.contains(&key.as_str()) {
            return Err(format!(
                "Target #{} ({}): unknown arg '{}'. Allowed args: {}",
                idx,
                type_name,
                key,
                allowed.join(", ")
            ));
        }
    }
    Ok(())
}

fn require_string_arg(
    args: &HashMap<String, serde_yaml::Value>,
    name: &str,
    idx: usize,
    type_name: &str,
) -> Result<String, String> {
    let val = args.get(name).ok_or_else(|| {
        format!(
            "Target #{} ({}): missing required arg '{}'",
            idx, type_name, name
        )
    })?;
    match val {
        serde_yaml::Value::String(s) => Ok(s.clone()),
        _ => Err(format!(
            "Target #{} ({}): '{}' must be a string",
            idx, type_name, name
        )),
    }
}

struct FailureWindow {
    start: DateTime<Local>,
    end: DateTime<Local>,
}

impl FailureWindow {
    fn duration_secs(&self) -> i64 {
        (self.end - self.start).num_seconds().max(1)
    }
}

struct TargetState {
    target: Target,
    is_failing: bool,
    failures: Vec<FailureWindow>,
}

async fn check_target(target: &Target, timeout_secs: u64) -> bool {
    let dur = Duration::from_secs(timeout_secs);
    match &target.check {
        Check::Http { url } => {
            let client = reqwest::Client::builder()
                .timeout(dur)
                .danger_accept_invalid_certs(false)
                .user_agent("downtime-benchmarker/0.1")
                .build();
            let client = match client {
                Ok(c) => c,
                Err(_) => return false,
            };
            match client.get(url).send().await {
                Ok(resp) => {
                    let status = resp.status().as_u16();
                    (200..400).contains(&status)
                }
                Err(_) => false,
            }
        }
        Check::Tcp { host, port } => {
            let addr_str = if host.contains(':') {
                // IPv6: wrap in brackets
                format!("[{}]:{}", host, port)
            } else {
                format!("{}:{}", host, port)
            };
            timeout(dur, TcpStream::connect(addr_str.as_str()))
                .await
                .map_or(false, |r| r.is_ok())
        }
    }
}

fn print_status_block(states: &[TargetState], results: &[bool]) {
    let now = Local::now().format("%H:%M:%S");
    println!("─── [{}] ───", now);
    for (state, &ok) in states.iter().zip(results.iter()) {
        let (check, color) = if ok {
            ("✓", GREEN)
        } else {
            ("✗", RED)
        };
        println!(
            "  {}{}{} {} {}",
            color, check, RESET, state.target.icon(), state.target
        );
    }
}

fn print_report(states: &[TargetState]) {
    println!();
    println!("{}📊 Downtime Benchmarking Results{}", BOLD, RESET);
    println!("═══════════════════════════════");
    println!();

    // Collect targets that had failures
    let mut failed_targets: Vec<&TargetState> = states
        .iter()
        .filter(|s| !s.failures.is_empty())
        .collect();

    if failed_targets.is_empty() {
        println!(
            "{}{}✅ No downtime detected! All targets remained healthy.{}",
            BOLD, GREEN, RESET
        );
        println!();
        return;
    }

    // Sort by time of first failure
    failed_targets.sort_by_key(|s| s.failures.first().map(|f| f.start));

    let earliest = failed_targets
        .iter()
        .filter_map(|s| s.failures.first().map(|f| f.start))
        .min()
        .unwrap();

    println!(
        "{}🔴 Failures started at: {}{}",
        RED,
        earliest.format("%H:%M:%S"),
        RESET
    );
    println!();
    println!(
        "{}📋 Details (sorted by time of first failure):{}",
        BOLD, RESET
    );
    println!();

    let mut total_downtime_secs: i64 = 0;

    for state in &failed_targets {
        let target_downtime: i64 = state.failures.iter().map(|f| f.duration_secs()).sum();
        total_downtime_secs += target_downtime;
        let count = state.failures.len();

        println!(
            "  {} {}{}{}",
            state.target.icon(),
            BOLD,
            state.target,
            RESET
        );
        println!(
            "     {}Total downtime: {}s | {} failure(s){}",
            RED, target_downtime, count, RESET
        );

        for (i, window) in state.failures.iter().enumerate() {
            let dur = window.duration_secs();
            let time = window.start.format("%H:%M:%S");
            let connector = if i == count - 1 { "└──" } else { "├──" };
            println!(
                "     {} {}{:<3}s @ {}{}",
                connector, RED, dur, time, RESET
            );
        }
        println!();
    }

    println!("───────────────────────────────");
    println!(
        "{}{}⏱️  Total downtime: {}s{}",
        BOLD, RED, total_downtime_secs, RESET
    );
    println!();
}

#[tokio::main]
async fn main() {
    let cli = Cli::parse();

    // Load targets file
    let content = match std::fs::read_to_string(&cli.target_urls) {
        Ok(c) => c,
        Err(e) => {
            eprintln!(
                "{}Error: Failed to read targets file '{}': {}{}",
                RED,
                cli.target_urls.display(),
                e,
                RESET
            );
            std::process::exit(1);
        }
    };

    let targets_file: TargetsFile = match serde_yaml::from_str(&content) {
        Ok(t) => t,
        Err(e) => {
            eprintln!(
                "{}Error: Failed to parse targets file: {}{}",
                RED, e, RESET
            );
            std::process::exit(1);
        }
    };

    if targets_file.targets.is_empty() {
        eprintln!(
            "{}Error: No targets defined in the targets file{}",
            RED, RESET
        );
        std::process::exit(1);
    }

    let targets = match validate_targets(targets_file.targets) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("{}Error: {}{}", RED, e, RESET);
            std::process::exit(1);
        }
    };

    println!(
        "{}Loaded {} target(s) from '{}'{}",
        BOLD,
        targets.len(),
        cli.target_urls.display(),
        RESET
    );

    // Initial check
    println!();
    println!("{}Running initial health check...{}", YELLOW, RESET);

    let initial_results = check_all(&targets, cli.timeout).await;

    let mut all_ok = true;
    for (target, &ok) in targets.iter().zip(initial_results.iter()) {
        if ok {
            println!(
                "  {} [{}] {} {}✓ healthy{}",
                target.icon(),
                target.type_name(),
                target,
                GREEN,
                RESET
            );
        } else {
            println!(
                "  {} [{}] {} {}✗ FAILED{}",
                target.icon(),
                target.type_name(),
                target,
                RED,
                RESET
            );
            all_ok = false;
        }
    }

    if !all_ok {
        eprintln!();
        eprintln!(
            "{}Error: Some targets failed the initial health check. Fix them before benchmarking.{}",
            RED, RESET
        );
        std::process::exit(1);
    }

    println!();
    println!(
        "{}{}✅ All targets healthy. Starting monitoring (interval: {}s, timeout: {}s){}",
        GREEN, BOLD, cli.check_interval, cli.timeout, RESET
    );
    println!();

    // Set up Ctrl+C handler
    let stop = Arc::new(AtomicBool::new(false));
    let stop_clone = stop.clone();
    ctrlc::set_handler(move || {
        stop_clone.store(true, Ordering::SeqCst);
    })
    .expect("Failed to set Ctrl+C handler");

    // Initialize target states
    let mut states: Vec<TargetState> = targets
        .iter()
        .map(|t| TargetState {
            target: t.clone(),
            is_failing: false,
            failures: Vec::new(),
        })
        .collect();

    // Monitoring loop
    loop {
        if stop.load(Ordering::SeqCst) {
            break;
        }

        tokio::time::sleep(Duration::from_secs(cli.check_interval)).await;

        if stop.load(Ordering::SeqCst) {
            break;
        }

        let results = check_all(&targets, cli.timeout).await;
        let now = Local::now();

        // Update states
        for (state, &ok) in states.iter_mut().zip(results.iter()) {
            if ok {
                if state.is_failing {
                    // Transition FAIL → OK: close current window
                    if let Some(window) = state.failures.last_mut() {
                        window.end = now;
                    }
                    state.is_failing = false;
                }
            } else if state.is_failing {
                // Still failing: extend the current window
                if let Some(window) = state.failures.last_mut() {
                    window.end = now;
                }
            } else {
                // Transition OK → FAIL: open new window
                state.failures.push(FailureWindow {
                    start: now,
                    end: now,
                });
                state.is_failing = true;
            }
        }

        print_status_block(&states, &results);
        println!(
            "{}⏳ Monitoring... Press Ctrl+C to stop and see results.{}",
            YELLOW, RESET
        );
    }

    // Close any still-open failure windows
    let now = Local::now();
    for state in &mut states {
        if state.is_failing {
            if let Some(window) = state.failures.last_mut() {
                window.end = now;
            }
        }
    }

    print_report(&states);
}

async fn check_all(targets: &[Target], timeout_secs: u64) -> Vec<bool> {
    let mut handles = Vec::with_capacity(targets.len());
    for target in targets {
        let target = target.clone();
        handles.push(tokio::spawn(
            async move { check_target(&target, timeout_secs).await },
        ));
    }

    let mut results = Vec::with_capacity(handles.len());
    for handle in handles {
        results.push(handle.await.unwrap_or(false));
    }
    results
}
