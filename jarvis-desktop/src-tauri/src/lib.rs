#[tauri::command]
fn jarvis_status() -> String {
    "SYSTEM ONLINE | CORE ACTIVE".to_string()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![jarvis_status])
        .run(tauri::generate_context!())
        .expect("error while running JARVIS AI");
}
