use serde::Serialize;
use std::process::Command;

#[derive(Serialize)]
struct SystemInfo {
    os: String,
    arch: String,
    hostname: String,
}

#[tauri::command]
fn jarvis_status() -> String {
    "SYSTEM ONLINE | CORE ACTIVE".to_string()
}

#[tauri::command]
fn system_info() -> SystemInfo {
    SystemInfo {
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        hostname: std::env::var("COMPUTERNAME")
            .or_else(|_| std::env::var("HOSTNAME"))
            .unwrap_or_else(|_| "UNKNOWN".to_string()),
    }
}

#[tauri::command]
fn open_url(url: String) -> Result<(), String> {
    if !(url.starts_with("https://") || url.starts_with("http://")) {
        return Err("Somente URLs HTTP/HTTPS são permitidas.".to_string());
    }
    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args(["/C", "start", "", &url])
            .spawn()
            .map_err(|e| e.to_string())?;
        return Ok(());
    }
    #[cfg(not(target_os = "windows"))]
    {
        Err("Abertura de URL está implementada para Windows nesta versão.".to_string())
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![jarvis_status, system_info, open_url])
        .run(tauri::generate_context!())
        .expect("error while running JARVIS AI");
}
