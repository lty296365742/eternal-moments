import Foundation

class SettingsViewModel: ObservableObject {
    @Published var selectedLanguage = "中文"
    let languages = ["中文", "English", "日本語"]
}
